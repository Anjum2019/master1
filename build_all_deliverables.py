import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header_styled(doc, text, level=1, color_rgb=(13, 59, 102)):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.name = 'Calibri'
    if level == 1:
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(*color_rgb)
        # Add bottom border or underline effect via XML
        pPr = p._p.get_or_add_pPr()
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="0D3B66"/></w:pBdr>')
        pPr.append(pBdr)
    elif level == 2:
        run.font.size = Pt(12.5)
        run.font.color.rgb = RGBColor(30, 80, 140)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(50, 50, 50)
    return p

def add_bullet_point(doc, title, body):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_title = p.add_run(title)
    run_title.bold = True
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(10)
    run_title.font.color.rgb = RGBColor(30, 41, 59)
    
    run_body = p.add_run(body)
    run_body.font.name = 'Calibri'
    run_body.font.size = Pt(10)
    run_body.font.color.rgb = RGBColor(51, 65, 85)
    return p

# =========================================================================
# 1. BUILD RESUME DOCX
# =========================================================================
def build_resume_docx():
    doc = docx.Document()
    
    # Page Setup: Standard Letter, 0.6 inch margins
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.6)
        s.bottom_margin = Inches(0.6)
        s.left_margin = Inches(0.6)
        s.right_margin = Inches(0.6)

    # Name and Title Block
    header_table = doc.add_table(rows=1, cols=1)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = header_table.cell(0, 0)
    set_cell_background(cell, "0D3B66")
    set_cell_margins(cell, top=200, bottom=200, left=240, right=240)
    
    hp = cell.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hrun1 = hp.add_run("SENIOR BUSINESS ANALYST | ENTERPRISE AI SOLUTIONS\n")
    hrun1.bold = True
    hrun1.font.name = 'Calibri'
    hrun1.font.size = Pt(16)
    hrun1.font.color.rgb = RGBColor(255, 255, 255)
    
    hrun2 = hp.add_run("Reporting Transformation • Financial Forecasting & Operations • Agentic AI Prototyping\n")
    hrun2.font.name = 'Calibri'
    hrun2.font.size = Pt(11)
    hrun2.font.color.rgb = RGBColor(209, 227, 255)
    
    hrun3 = hp.add_run("Mumbai / Thane / Palghar, Maharashtra, India  •  7+ Years Experience at Capgemini India")
    hrun3.font.name = 'Calibri'
    hrun3.font.size = Pt(9.5)
    hrun3.font.color.rgb = RGBColor(255, 255, 255)

    doc.add_paragraph().paragraph_format.space_before = Pt(4)

    # Executive Profile
    add_header_styled(doc, "PROFESSIONAL PROFILE & POSITIONING", level=1)
    p_prof = doc.add_paragraph()
    p_prof.paragraph_format.space_before = Pt(3)
    p_prof.paragraph_format.space_after = Pt(6)
    p_prof.paragraph_format.line_spacing = 1.15
    r_prof = p_prof.add_run(
        "Accomplished Senior Business Analyst with 7+ years of progressive enterprise experience at Capgemini India, "
        "specializing in reporting platforms, financial forecasting transformation, and multi-tier data migration. "
        "Pioneers a high-impact enterprise profile: positioning business analysis as the foundational bridge between "
        "complex reporting bottlenecks and agentic AI automation. Possesses deep functional mastery over Power BI dashboards, "
        "SQL data models, financial variance analysis, and service-desk defect triage, paired with practical capabilities in "
        "prototyping Python/Gradio AI agents (Dashboard Insights, Reporting Investigation, and Market Intelligence). "
        "Adept at translating complex executive requirements into airtight functional specifications and leading cross-functional "
        "teams to eliminate reporting latency and uphold bulletproof data integrity."
    )
    r_prof.font.name = 'Calibri'
    r_prof.font.size = Pt(10)
    r_prof.font.color.rgb = RGBColor(51, 65, 85)

    # Core Competencies Table
    add_header_styled(doc, "CORE COMPETENCIES & TECHNICAL EXPERTISE", level=1)
    skill_table = doc.add_table(rows=5, cols=2)
    skill_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    skill_data = [
        ("Business Analysis & Requirements", "Requirements Gathering, BRD/FRD Documentation, Business Logic Mapping, Process Modeling, Functional Walkthroughs, User Acceptance Testing (UAT) Coordination"),
        ("Financial & Variance Analysis", "Financial Reporting, Forecast vs. Actuals Modeling, Revenue & Cost Variance Attribution, EBITDA Tracking, WIP Aging & Billing Leakage Prevention"),
        ("Enterprise AI Agent Prototyping", "Agentic Workflow Design, Dashboard Insights Agent, Autonomous Reporting Investigation Assistant, Web Summarisation Agent, Python, Gradio UI, Prompt Scaffolding"),
        ("Reporting & Data Architecture", "Power BI DAX & Data Modeling, SQL Schema Analysis (Azure SQL/T-SQL), Data Reconciliation, Discrepancy Triage (Report vs DB Layer), Data Quality Assurance"),
        ("Quality Assurance & Leadership", "Test Planning & Defect Management (Jira/ServiceNow), Cross-Functional Stakeholder Alignment, Data Migration Validation, Continuous Process Optimization")
    ]
    for row_idx, (col1, col2) in enumerate(skill_data):
        c1, c2 = skill_table.cell(row_idx, 0), skill_table.cell(row_idx, 1)
        c1.width = Inches(2.2)
        c2.width = Inches(5.1)
        set_cell_background(c1, "F1F5F9" if row_idx % 2 == 0 else "FFFFFF")
        set_cell_background(c2, "F8FAFC" if row_idx % 2 == 0 else "FFFFFF")
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(col1)
        r1.bold = True
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(13, 59, 102)
        
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(col2)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_before = Pt(4)

    # Featured Enterprise AI Agent Solutions
    add_header_styled(doc, "FEATURED ENTERPRISE AGENTIC AI PROTOTYPES", level=1)
    
    add_bullet_point(doc, "Dashboard Insights Agent (Python, Gradio, Pandas): ", 
                     "Architected an autonomous KPI analysis agent that ingests enterprise portfolio datasets, computes net variances against budgets, detects underlying margin/cost drivers, and delivers structured executive briefings with prioritized operational recommendations.")
    
    add_bullet_point(doc, "Autonomous Reporting Investigation Assistant (ARIA): ", 
                     "Designed an enterprise support triage assistant addressing the friction between Power BI visuals and SQL backends. Compares expected vs. actual values, isolates fault layers (DAX filter context vs. SQL joins vs. ETL cutoff), produces executable SQL validation scripts, and writes production-ready Jira tickets and stakeholder memos, reducing diagnostic MTTR by ~70%.")

    add_bullet_point(doc, "Enterprise Website & Market Intelligence Summariser: ", 
                     "Constructed a strategic intelligence agent that extracts public/intranet URLs, eliminates web noise, and parses dense regulatory and corporate reports into 5 executive dimensions: Snapshot, Key Findings, Operational Implications, Governance Risks, and Actionable Steps.")

    doc.add_paragraph().paragraph_format.space_before = Pt(4)

    # Professional Experience
    add_header_styled(doc, "PROFESSIONAL EXPERIENCE", level=1)
    
    # Header for Capgemini
    p_comp = doc.add_paragraph()
    p_comp.paragraph_format.space_before = Pt(4)
    p_comp.paragraph_format.space_after = Pt(2)
    r_cname = p_comp.add_run("CAPGEMINI INDIA PVT. LTD.")
    r_cname.bold = True
    r_cname.font.name = 'Calibri'
    r_cname.font.size = Pt(12)
    r_cname.font.color.rgb = RGBColor(13, 59, 102)
    r_ctitle = p_comp.add_run("  |  Consultant  |  Jan 2019 – Present (7+ Years)")
    r_ctitle.bold = True
    r_ctitle.font.name = 'Calibri'
    r_ctitle.font.size = Pt(10.5)
    r_ctitle.font.color.rgb = RGBColor(71, 85, 105)

    # Role 1
    add_header_styled(doc, "1. Business Analyst — Reporting & Insights Platform (Jan 2026 – Present)", level=2)
    add_bullet_point(doc, "Requirements Engineering & Specifications: ", "Spearhead gathering and translating complex business requirements into functional specifications, business logic matrices, and data flow diagrams for enterprise Power BI dashboards and SQL-based data models.")
    add_bullet_point(doc, "Financial KPI & Portfolio Insights: ", "Evaluate multi-million-dollar portfolio metrics across revenue, delivery cost, and EBITDA, creating actionable insights and visualizations for delivery managers and C-suite leadership.")
    add_bullet_point(doc, "Reporting Issue Triage & SQL Isolation: ", "Lead root-cause triage across IT service desk tickets, diagnosing whether reporting discrepancies originate in Power BI DAX calculation context, SQL view logic, or scheduled ETL refresh lags.")
    add_bullet_point(doc, "Functional Walkthroughs & Knowledge Transfer: ", "Conduct structured functional walkthroughs and train global business users on enhanced dashboard features, driving seamless user adoption and high data literacy.")

    # Role 2
    add_header_styled(doc, "2. Business Analyst — Forecasting Transformation (June 2024 – Dec 2025)", level=2)
    add_bullet_point(doc, "Forecasting Process Transformation: ", "Engineered the operational migration from legacy monthly flat forecasting to a high-granularity rolling financial forecast model, vastly improving forward visibility.")
    add_bullet_point(doc, "Stakeholder Working Sessions: ", "Facilitated intensive workshops with project managers and finance heads to establish standardized forecasting procedures and drive 100% process compliance.")
    add_bullet_point(doc, "Variance Analysis & Discrepancy Resolution: ", "Performed multi-system reconciliation across internal ERP and reporting platforms, isolating material variances between actual figures and forecasted baselines.")
    add_bullet_point(doc, "Financial Data Integrity: ", "Instituted cross-validation checkpoints between finance and project delivery teams, ensuring reliable financial data governance across multi-quarter horizons.")

    # Role 3 & 4
    add_header_styled(doc, "3. Project Data Migration & Support Specialist & Test Lead (Jan 2023 – May 2024)", level=2)
    add_bullet_point(doc, "End-to-End Migration Leadership: ", "Directed data migration of enterprise project records from legacy tracking systems to a centralized monitoring platform, guaranteeing zero data loss and business continuity.")
    add_bullet_point(doc, "Lifecycle & Budget Maintenance: ", "Administered project lifecycle governance, budget baseline updates, and milestone tracking in compliance with client Master Service Agreements (MSAs).")
    add_bullet_point(doc, "Test Planning & Delivery Management: ", "Spearheaded end-to-end testing cycles as Test Lead, supervising a team of QA engineers, approving test cases, managing defect lifecycles, and driving User Acceptance Testing (UAT).")
    add_bullet_point(doc, "Data Integrity & Discrepancy Investigation: ", "Created automated validation scripts to reconcile migrated balances, identifying and resolving over 250+ data discrepancies across historical billing records.")

    # Role 5 & 6
    add_header_styled(doc, "4. Test Analyst & Financial Operations Analyst (Jan 2019 – Dec 2023)", level=2)
    add_bullet_point(doc, "BI Dashboard Prototyping: ", "Conceptualized and built functional prototypes for internal BI reports and performance dashboards, establishing clear reporting requirements for subsequent technical development.")
    add_bullet_point(doc, "Functional & UAT Testing: ", "Executed exhaustive test suites across core business applications, verifying data models, transaction calculations, and user interface workflows.")
    add_bullet_point(doc, "Financial Operations & WIP Tracking: ", "Managed corporate invoicing, expense tracking, and project code allocations; monitored Work in Progress (WIP) and unbilled balances to prevent revenue leakage.")
    add_bullet_point(doc, "Process Optimization: ", "Streamlined repetitive financial reconciliation workflows, reducing monthly close preparation time by 25%.")

    # Education
    add_header_styled(doc, "EDUCATION & CREDENTIALS", level=1)
    p_edu = doc.add_paragraph()
    p_edu.paragraph_format.space_before = Pt(3)
    p_edu.paragraph_format.space_after = Pt(2)
    r_deg = p_edu.add_run("Bachelor of Engineering (B.E.) in Information Technology\n")
    r_deg.bold = True
    r_deg.font.name = 'Calibri'
    r_deg.font.size = Pt(10.5)
    r_deg.font.color.rgb = RGBColor(13, 59, 102)
    
    r_col = p_edu.add_run("Theem College of Engineering, Palghar (University of Mumbai)  |  July 2013 – May 2017")
    r_col.font.name = 'Calibri'
    r_col.font.size = Pt(9.5)
    r_col.font.color.rgb = RGBColor(71, 85, 105)

    doc.save("/home/user/resume_ai_business_analyst.docx")
    print("Resume DOCX generated successfully at /home/user/resume_ai_business_analyst.docx")

# =========================================================================
# 2. BUILD ENTERPRISE AGENTIC PROJECTS GUIDE DOCX
# =========================================================================
def build_projects_guide_docx():
    doc = docx.Document()
    
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.7)
        s.right_margin = Inches(0.7)

    # Document Title Block
    header_table = doc.add_table(rows=1, cols=1)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = header_table.cell(0, 0)
    set_cell_background(cell, "0D3B66")
    set_cell_margins(cell, top=240, bottom=240, left=260, right=260)
    
    hp = cell.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hrun1 = hp.add_run("ENTERPRISE AGENTIC AI SOLUTIONS GUIDE & PORTFOLIO\n")
    hrun1.bold = True
    hrun1.font.name = 'Calibri'
    hrun1.font.size = Pt(17)
    hrun1.font.color.rgb = RGBColor(255, 255, 255)
    
    hrun2 = hp.add_run("The AI Agent Angle: How Business Analysts Define, Prototype, and Deploy Enterprise Solutions\n")
    hrun2.font.name = 'Calibri'
    hrun2.font.size = Pt(11)
    hrun2.font.color.rgb = RGBColor(209, 227, 255)
    
    hrun3 = hp.add_run("Strategic Career Blueprint • Architecture Designs • Business ROI • Interview Mastery")
    hrun3.font.name = 'Calibri'
    hrun3.font.size = Pt(9.5)
    hrun3.font.color.rgb = RGBColor(255, 255, 255)

    doc.add_paragraph().paragraph_format.space_before = Pt(8)

    # Section 1: Executive Positioning Strategy
    add_header_styled(doc, "1. THE STRATEGIC ANGLE: WHY POSITION AS AN AI-ENABLED BUSINESS ANALYST?", level=1)
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(
        "In the enterprise market, there is a severe disconnect between raw AI engineering and business value. "
        "AI engineers build models, but they rarely understand general ledger reconciliations, revenue recognition rules, "
        "DAX filter context, or the operational impact of a $500k reporting discrepancy on a quarterly executive review. "
        "Conversely, traditional business analysts spend 40% of their time on repetitive manual tasks: investigating support "
        "tickets, reconciling SQL vs. Power BI numbers, writing weekly variance commentary, and copying data between systems.\n\n"
        "Your most credible and lucrative direction is NOT to present yourself as an AI engineer who trains foundation models. "
        "It is to position yourself as an AI-Enabled Senior Business Analyst & Solutions Consultant who understands reporting "
        "problems intimately, defines the exact business requirements, and prototypes working agentic AI solutions in Python/Gradio. "
        "This positioning makes you indispensable: you speak fluent business and finance, you understand enterprise data pipelines, "
        "and you build functional AI prototypes that technical teams can scale and executives can immediately understand."
    )
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

    # Section 2: Deep Dive into Project 1
    add_header_styled(doc, "2. PROJECT 1: DASHBOARD INSIGHTS AGENT (EXECUTIVE KPI RESOLVER)", level=1)
    add_bullet_point(doc, "Enterprise Problem Statement: ", 
                     "Executive leadership reviews dozens of Power BI dashboard pages weekly. While dashboards present numbers, they do not explain the 'why' behind variances or prescribe corrective action. Business analysts often spend 6-8 hours prior to each executive steering meeting manually calculating margins, isolating underperforming business units, and writing PowerPoint narrative summaries.")
    add_bullet_point(doc, "Agentic Architecture & Workflow: ", 
                     "The Dashboard Insights Agent ingests structured reporting extracts (CSV/Excel/SQL View). It automatically identifies metric dimensions (Target vs. Actual, Budget vs. Cost, Margin %, EBITDA), calculates variances, applies tolerance thresholds (e.g. 5% variance flag), and executes natural language reasoning to generate an Executive KPI Briefing, Variance Attribution Matrix, Driver Hypotheses, and Prioritized Management Next Steps.")
    add_bullet_point(doc, "Business Analyst's Role & Contribution: ", 
                     "Designed business logic matrices, established tolerance thresholds, created the prompt templates, and built the interactive Gradio prototype in Python, enabling delivery executives to perform self-service variance analysis in real time.")
    add_bullet_point(doc, "Quantified Enterprise ROI: ", 
                     "Saves 6-8 hours of manual preparation per reporting cycle; reduces executive review preparation latency by 85%; eliminates calculation errors in leadership slide decks.")

    # Section 3: Deep Dive into Project 2
    add_header_styled(doc, "3. PROJECT 2: AUTONOMOUS REPORTING INVESTIGATION ASSISTANT (ARIA)", level=1)
    add_bullet_point(doc, "Enterprise Problem Statement: ", 
                     "When business stakeholders notice that a front-end Power BI report diverges from an ERP or source database (e.g. Q3 revenue missing $550k), ticket triage takes 4-12 hours. Business analysts, service desk staff, and SQL developers bounce tickets back and forth to determine if the fault is in Power BI DAX formulas, SQL view joins, or ETL batch lag.")
    add_bullet_point(doc, "Agentic Architecture & Workflow: ", 
                     "ARIA operates as an automated diagnostic triage engine. It takes the reported symptoms, expected amount, actual amount, and filter context. It evaluates a multi-layer decision tree, calculates variance severity (P1/P2/P3), isolates the probable layer of fault (Power BI DAX vs. SQL Data Warehouse vs. ETL), automatically generates executable SQL diagnostic scripts, and drafts a ready-to-use Jira defect ticket and an executive stakeholder email update.")
    add_bullet_point(doc, "Business Analyst's Role & Contribution: ", 
                     "Codified 7+ years of Capgemini reporting and testing triage heuristics into a structured diagnostic engine; authored the SQL verification templates and Jira acceptance criteria standards.")
    add_bullet_point(doc, "Quantified Enterprise ROI: ", 
                     "Reduces support defect triage time (MTTR) by 70%; prevents duplicate developer investigations; ensures transparent, proactive communication with finance executives within minutes of ticket receipt.")

    # Section 4: Deep Dive into Project 3
    add_header_styled(doc, "4. PROJECT 3: WEBSITE & MARKET INTELLIGENCE SUMMARISATION AGENT", level=1)
    add_bullet_point(doc, "Enterprise Problem Statement: ", 
                     "Business analysts and strategy teams spend extensive hours reading 40-page regulatory filings (SEC, IFRS, ESG), competitor financial announcements, and technology whitepapers to evaluate market shifts and adjust forecasting assumptions.")
    add_bullet_point(doc, "Agentic Architecture & Workflow: ", 
                     "Accepts any web URL or raw text, strips boilerplate navigation/scripts using BeautifulSoup, isolates core paragraphs, and executes an analytical synthesis pipeline. Produces 5 standardized enterprise sections: Executive Snapshot, Core Findings, Strategic & Operational Implications, Risk & Governance Considerations, and Actionable Next Steps.")
    add_bullet_point(doc, "Business Analyst's Role & Contribution: ", 
                     "Designed the analytical information architecture to ensure the output aligns with executive briefing standards rather than generic consumer summaries; integrated human-in-the-loop review capabilities.")
    add_bullet_point(doc, "Quantified Enterprise ROI: ", 
                     "Cuts external research and document analysis time by 75%; allows instant synthesis of competitor earnings releases and regulatory disclosures.")

    # Section 5: Enterprise Governance & Security
    add_header_styled(doc, "5. ENTERPRISE GOVERNANCE, SECURITY & HUMAN-IN-THE-LOOP DESIGN", level=1)
    p_gov = doc.add_paragraph()
    p_gov.paragraph_format.line_spacing = 1.15
    r_gov = p_gov.add_run(
        "To deploy AI agents successfully in conservative enterprise environments (such as Tier-1 Banks, Healthcare, and Public Sector), "
        "governance and compliance must be built in from day one:\n"
        "1. Deterministic Calculation Guardrails: All mathematical computations (variance $, variance %, EBITDA) are computed using "
        "deterministic Python/Pandas logic, never hallucinated by an LLM.\n"
        "2. Data Privacy & Confidentiality: The system operates on anonymized or local data schemas, ensuring no proprietary financial "
        "records are transmitted to unauthorized public model endpoints.\n"
        "3. Human-in-the-Loop Review: Agentic outputs (Jira tickets, stakeholder emails, executive briefings) are structured as drafts "
        "requiring Business Analyst validation before being broadcast to leadership.\n"
        "4. Auditability & Lineage: Every diagnostic SQL query generated includes explicit metadata, ticket references, and execution rationale."
    )
    r_gov.font.name = 'Calibri'
    r_gov.font.size = Pt(10)

    # Section 6: Interview Masterclass & Talking Scripts
    add_header_styled(doc, "6. INTERVIEW SCRIPTS & STRATEGIC POSITIONING MASTERCLASS", level=1)
    
    add_bullet_point(doc, "Question: 'Tell me about yourself.'\n",
                     "\"I am a Senior Business Analyst with over 7 years of enterprise experience at Capgemini, specializing in financial forecasting, reporting platforms, and data migration. Throughout my career, I've gathered requirements, designed Power BI and SQL data models, and conducted variance analysis for multi-million-dollar portfolios. What distinguishes my profile is how I apply agentic AI to these exact enterprise challenges: rather than waiting for external data science teams, I prototype Python and Gradio-based AI agents—such as Dashboard Insights and Autonomous Reporting Investigation assistants—that automate reporting triage, accelerate KPI analysis, and bridge the gap between business leadership and technical development.\"")

    add_bullet_point(doc, "Question: 'Why shouldn't we hire a specialized AI Engineer instead?'\n",
                     "\"If your goal is training transformer architectures from scratch, you need an AI research engineer. But if your goal is solving reporting bottlenecks, reconciling financial data, and accelerating business decisions, an AI engineer doesn't understand DAX filter contexts, unbilled WIP aging, or why an ERP variance impacts quarterly forecasting. I bring 7+ years of deep enterprise domain knowledge in reporting and financial operations, coupled with the ability to define, prototype, and govern agentic AI solutions that solve tangible business problems on day one.\"")

    doc.save("/home/user/enterprise_agentic_solutions_guide.docx")
    print("Projects Guide DOCX generated successfully at /home/user/enterprise_agentic_solutions_guide.docx")

if __name__ == "__main__":
    build_resume_docx()
    build_projects_guide_docx()
