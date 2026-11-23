-- ====================================================================
-- LinkedIn Intelligence Warehouse Schema (Odoo, Accounting, Costing & AI)
-- Host: Supabase / PostgreSQL
-- ====================================================================

-- 1. Projects table
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    keywords TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. LinkedIn Posts table
CREATE TABLE IF NOT EXISTS public.linkedin_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_url TEXT UNIQUE NOT NULL,
    author_name VARCHAR(255),
    author_title TEXT,
    post_text TEXT NOT NULL,
    published_date TIMESTAMPTZ,
    engagement_likes INT DEFAULT 0,
    engagement_comments INT DEFAULT 0,
    raw_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. AI Insights and Project Mapping table
CREATE TABLE IF NOT EXISTS public.post_project_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES public.linkedin_posts(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    relevance_score INT CHECK (relevance_score BETWEEN 0 AND 100),
    tags TEXT[] DEFAULT '{}',
    odoo_feature_or_module VARCHAR(100),
    practical_takeaway TEXT,
    key_ideas JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    UNIQUE(post_id, project_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_posts_published_date ON public.linkedin_posts(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_insights_project_id ON public.post_project_insights(project_id);
CREATE INDEX IF NOT EXISTS idx_insights_score ON public.post_project_insights(relevance_score DESC);

-- 4. Initial Seed Data for Domain Projects
INSERT INTO public.projects (code, title, description, keywords) VALUES
('AI_ERP', 'AI & Odoo Integration', 'وكلاء الذكاء الاصطناعي، أتمتة القيود، معالجة المستندات الذكية، والشات بوت للتقارير في أودو', ARRAY['AI', 'Agent', 'OCR', 'LLM', 'Automation', 'Python', 'API']),
('COSTING', 'Cost Accounting & Manufacturing (MRP)', 'حساب التكاليف المعيارية والفعلية، تكاليف أوامر التصنيع، Landed Cost، وتقييم المخزون AVCO/FIFO', ARRAY['Costing', 'Cost Accounting', 'MRP', 'BOM', 'Manufacturing', 'Landed Cost', 'Inventory Valuation']),
('ODOO_ACC', 'Odoo Financial Accounting & Localization', 'الحلول المحاسبية المتقدمة، شجرة الحسابات، التسويات البنكية، والفوترة الإلكترونية والضرائب في أودو', ARRAY['Accounting', 'Odoo Accounting', 'General Ledger', 'Invoicing', 'Tax', 'ZATCA', 'Reconciliation']),
('CASE_STUDIES', 'ERP Real World Case Studies & Troubleshooting', 'تجارب تطبيق واقعية في الشركات، حلول لمشاكل فنية، وأفضل الممارسات الاستشارية في أودو', ARRAY['Case Study', 'Troubleshooting', 'Implementation', 'Consulting', 'Best Practices'])
ON CONFLICT (code) DO NOTHING;

-- 5. Ready-to-use Dashboard View
CREATE OR REPLACE VIEW public.v_daily_project_feed AS
SELECT 
    p.code AS project_code,
    p.title AS project_title,
    lp.author_name,
    lp.author_title,
    ins.relevance_score,
    ins.odoo_feature_or_module,
    ins.tags,
    ins.practical_takeaway,
    lp.post_url,
    lp.published_date,
    ins.created_at AS analyzed_at
FROM public.post_project_insights ins
JOIN public.projects p ON ins.project_id = p.id
JOIN public.linkedin_posts lp ON ins.post_id = lp.id
ORDER BY ins.created_at DESC;
