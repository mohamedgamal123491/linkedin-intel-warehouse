import os
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from supabase import create_client, Client
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --- Configurations ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

class PostAnalysis(BaseModel):
    project_code: str = Field(description="Must be one of: 'AI_ERP', 'COSTING', 'ODOO_ACC', 'CASE_STUDIES', or 'OTHER'")
    relevance_score: int = Field(description="Relevance percentage from 0 to 100")
    tags: List[str] = Field(description="3 to 5 targeted hashtags, e.g. ['#Odoo18', '#CostAccounting']")
    odoo_feature_or_module: str = Field(description="Odoo module or functional area (e.g. Accounting, MRP, Invoicing, Inventory, AI/Automation)")
    practical_takeaway: str = Field(description="Arabic concise summary of practical value for an ERP / Accounting consultant")
    key_ideas: List[str] = Field(description="List of key actionable ideas or takeaways in Arabic")

SYSTEM_PROMPT = """
You are an expert ERP & Cost Accounting Consultant specializing in Odoo ERP, Financial Accounting, Cost Accounting, and AI Automation in business applications.

Analyze the provided LinkedIn post and categorize it into ONE of these ongoing project categories:
- 'AI_ERP': AI agents, LLMs, document OCR, robotic process automation (RPA), financial bots integrated with Odoo/ERP.
- 'COSTING': Cost accounting, manufacturing (MRP), BOM costing, Landed Costs, standard vs actual costing, AVCO/FIFO inventory valuation.
- 'ODOO_ACC': Financial accounting, Chart of Accounts, Bank Reconciliation, E-Invoicing (ZATCA / ETA), Taxes, General Ledger in Odoo.
- 'CASE_STUDIES': Real-world implementation stories, troubleshooting, lessons learned, consultant best practices.
- 'OTHER': Irrelevant to ERP, Accounting, or AI.

Provide clear, professional, and practical Arabic takeaways.
"""

def analyze_post_with_ai(post_text: str, author_name: str = "", author_title: str = "") -> PostAnalysis:
    """Classifies and enriches a post using Gemini API."""
    if not ai_client:
        raise ValueError("GEMINI_API_KEY is not set.")

    prompt = f"Author: {author_name} ({author_title})\nPost Content:\n\"\"\"{post_text}\"\"\""
    response = ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=PostAnalysis,
            temperature=0.2,
        ),
    )
    return PostAnalysis.model_validate_json(response.text)

def ingest_post(post_data: Dict[str, Any]):
    """Saves raw post and AI analysis directly into Supabase Data Warehouse."""
    url = post_data["post_url"]
    
    # 1. Check duplicate
    existing = supabase.table("linkedin_posts").select("id").eq("post_url", url).execute()
    if existing.data:
        print(f"[-] Skipped existing post: {url}")
        return

    # 2. AI Analysis
    analysis = analyze_post_with_ai(
        post_data["post_text"],
        post_data.get("author_name", ""),
        post_data.get("author_title", "")
    )
    
    if analysis.project_code == "OTHER" or analysis.relevance_score < 40:
        print(f"[-] Low relevance ({analysis.relevance_score}%): {url}")
        return

    # 3. Insert Post
    post_res = supabase.table("linkedin_posts").insert({
        "post_url": url,
        "author_name": post_data.get("author_name"),
        "author_title": post_data.get("author_title"),
        "post_text": post_data["post_text"],
        "published_date": post_data.get("published_date"),
        "engagement_likes": post_data.get("likes", 0),
        "engagement_comments": post_data.get("comments", 0),
        "raw_metadata": post_data.get("raw_metadata", {})
    }).execute()
    
    if not post_res.data:
        print(f"[!] Failed to insert post: {url}")
        return
        
    post_id = post_res.data[0]["id"]

    # 4. Fetch Project ID
    proj_res = supabase.table("projects").select("id").eq("code", analysis.project_code).execute()
    if not proj_res.data:
        print(f"[!] Project code {analysis.project_code} not found in DB")
        return
    project_id = proj_res.data[0]["id"]

    # 5. Insert Insights
    supabase.table("post_project_insights").insert({
        "post_id": post_id,
        "project_id": project_id,
        "relevance_score": analysis.relevance_score,
        "tags": analysis.tags,
        "odoo_feature_or_module": analysis.odoo_feature_or_module,
        "practical_takeaway": analysis.practical_takeaway,
        "key_ideas": analysis.key_ideas
    }).execute()

    print(f"[+] Saved & Mapped to [{analysis.project_code}] ({analysis.relevance_score}%): {url}")

if __name__ == "__main__":
    print("LinkedIn Intel Warehouse Pipeline ready.")
