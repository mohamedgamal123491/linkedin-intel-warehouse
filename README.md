# 🚀 LinkedIn Intelligence Warehouse (AI + Odoo + Accounting + Costing)

مستودع بيانات ذكي ومؤتمت (Personal Data Warehouse) يقوم بفحص بوستات لينكدإن يومياً، وتصنيفها وتحليلها آلياً باستخدام الذكاء الاصطناعي (**Gemini API**)، وتخزينها مهيكلة داخل **Supabase (PostgreSQL)** لمتابعة المشاريع والاهتمامات المتخصصة.

---

## 🎯 المشاريع المدعومة (Domain Taxonomy)

يتم تصنيف أي بوست مفيد تلقائياً إلى واحد من المشاريع الأربعة:
1. **`AI_ERP` (AI & Odoo Integration):** وكلاء الذكاء الاصطناعي (AI Agents)، أتمتة الفواتير ومطابقة أوامر الشراء (3-Way Matching)، والربط مع أودو عبر XML-RPC.
2. **`COSTING` (Cost Accounting & Manufacturing):** حساب التكاليف المعيارية والفعلية، مصاريف الشحن والجمارك (Landed Costs)، تكاليف أوامر التصنيع وBOM، وتقييم المخزون (AVCO/FIFO).
3. **`ODOO_ACC` (Odoo Financial Accounting):** شجرة الحسابات، التسويات البنكية، فروق تقييم العملات الأجنبية، الفوترة الإلكترونية والضرائب.
4. **`CASE_STUDIES` (ERP Troubleshooting & Best Practices):** تجارب تطبيق عملية، حلول مشاكل واقعية في المصانع والشركات، ودروس مستفادة من الاستشاريين.

---

## 🏗️ المعمارية الهندسية (Architecture)

```
[ مصادر لينكدإن ]
       │
       ▼
[ Pipeline / GitHub Actions ] ── (يومياً عبر Cron)
       │
       ▼
[ Gemini 2.5 Flash Engine ] ── (استخراج Structured JSON + الوسوم + الخلاصة العملية)
       │
       ▼
[ Supabase Data Warehouse ]
   ├── جدول projects
   ├── جدول linkedin_posts
   ├── جدول post_project_insights
   └── العرض الموحد v_daily_project_feed
```

---

## 📊 لوحة المتابعة اليومية (Supabase View)

يمكن استعراض البيانات مباشرة من خلال فتح **Supabase Table Editor** واختيار الـ View:
👉 `v_daily_project_feed`

يعرض لك الجدول:
- **Project Title:** اسم المشروع المتخصص.
- **Author & Title:** كاتب البوست ومسماه الوظيفي.
- **Relevance Score:** نسبة أهمية البوست (0 - 100%).
- **Tags:** الهاشتاجات الذكية المستخرجة.
- **Practical Takeaway:** خلاصة عملية مباشرة وتطبيقية لاستشاري أودو والمدير المالي.
- **Post URL:** رابط البوست الأصلي للرجوع إليه.

---

## ⚙️ التثبيت والتشغيل المحلي (Local Setup)

1. **تثبيت الحزم المطلوبة:**
```bash
pip install -r requirements.txt
```

2. **ضبط المتغيرات في ملف `.env`:**
```env
SUPABASE_URL=https://topmkrzlbckamtjbjtmc.supabase.co
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
```

3. **تشغيل الأتمتة:**
```bash
python pipeline.py
```

---

## 🤖 التشغيل التلقائي عبر GitHub Actions

يحتوي هذا المستودع على Workflow جاهز في `.github/workflows/daily_automation.yml` يعمل تلقائياً كل يوم في تمام الساعة 6:00 صباحاً بتوقيت UTC بدون الحاجة لفتح جهازك.

كل ما تحتاجه هو إضافة الـ Secrets في إعدادات مستودع GitHub:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GEMINI_API_KEY`
