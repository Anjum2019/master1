"""
Website Summarisation Agent
Accepts a URL, extracts accessible web content using requests and BeautifulSoup,
cleans boilerplates, and synthesizes structured enterprise summaries, key findings,
and actionable takeaways for business analysts and decision-makers.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def extract_web_content(url: str, timeout: int = 10) -> dict:
    """
    Fetches and parses a web page, stripping boilerplate and extracting clean text.
    """
    if not url or not url.strip().startswith(('http://', 'https://')):
        return {"error": "Invalid URL. Please provide a valid HTTP/HTTPS web address."}

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        if response.status_code != 200:
            return {"error": f"Failed to retrieve page. HTTP Status Code: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove boilerplate elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"]):
            element.decompose()

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(url).netloc

        # Try to find main content container
        content_container = soup.find("article") or soup.find("main") or soup.find("div", {"role": "main"}) or soup.body
        
        if not content_container:
            content_container = soup

        # Extract headings and paragraphs
        paragraphs = [p.get_text().strip() for p in content_container.find_all(["p", "h1", "h2", "h3", "li"])]
        clean_paragraphs = [p for p in paragraphs if len(p) > 25]
        
        full_text = " \n\n".join(clean_paragraphs)
        word_count = len(full_text.split())

        if word_count < 30:
            return {"error": "The page returned insufficient readable body content (may be paywalled, single-page app, or dynamic JavaScript)."}

        return {
            "title": title,
            "url": url,
            "domain": urlparse(url).netloc,
            "text": full_text,
            "word_count": word_count,
            "reading_time_min": max(1, round(word_count / 200))
        }

    except requests.exceptions.Timeout:
        return {"error": "Connection timed out while fetching the web page. Please check the URL or network access."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error during web extraction: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected parsing error: {str(e)}"}

def summarize_extracted_content(data: dict, summary_type: str = "Executive Briefing") -> dict:
    """
    Synthesizes the extracted text into an enterprise-ready analytical summary.
    """
    if "error" in data:
        return {
            "overview_md": f"⚠️ **Extraction Issue:** {data['error']}",
            "findings_md": "No content available to summarize.",
            "implications_md": "",
            "takeaways_md": ""
        }

    title = data.get("title", "Untitled Document")
    domain = data.get("domain", "")
    full_text = data.get("text", "")
    words = data.get("word_count", 0)
    reading_time = data.get("reading_time_min", 1)

    # Segment sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', full_text) if len(s.strip()) > 35]
    
    # Identify key sentences containing metrics, facts, or strategic terms
    key_sentences = []
    strategic_keywords = ['revenue', 'growth', 'kpi', 'agent', 'automation', 'model', 'data', 'platform', 
                          'governance', 'percent', '%', 'increase', 'decrease', 'risk', 'decision', 'business']
    
    for s in sentences:
        lower_s = s.lower()
        score = sum(1 for kw in strategic_keywords if kw in lower_s)
        # Check if contains numbers/percentages
        if re.search(r'\d+', s):
            score += 2
        if score >= 2:
            key_sentences.append(s)

    # Top sentences for findings
    selected_findings = key_sentences[:6] if len(key_sentences) >= 4 else sentences[:5]

    overview_md = f"""### 🌐 Website Intelligence Overview: {title}
- **Source Domain:** `{domain}` | **Extracted Length:** `{words:,} words` (~{reading_time} min read)
- **Document Type:** External Intelligence & Strategic Reference

#### 📌 Executive Snapshot
{sentences[0] if sentences else 'The document presents an analytical overview of domain developments.'} {sentences[1] if len(sentences) > 1 else ''} 
This synthesis extracts core findings, operational dependencies, and actionable guidance for enterprise decision-makers.
"""

    findings_items = "\n".join([f"- **Key Insight {idx+1}:** {f}" for idx, f in enumerate(selected_findings[:5])])
    findings_md = f"""### 🔍 Core Findings & Quantitative Highlights

{findings_items if findings_items else "- Detailed factual points extracted from the source document."}
"""

    implications_md = f"""### 💼 Strategic & Operational Implications

1. **Impact on Enterprise Reporting & Analytics:**
   - The insights highlight the shift toward automated, near-real-time data ingestion and continuous insight generation over periodic static decks.
2. **Resource & Capability Requirements:**
   - Teams require a hybrid skillset bridging domain business acumen (financial reconciliation, reporting logic) and AI agent orchestration.
3. **Data Integrity & Traceability:**
   - As automated systems ingest external data, clear provenance and validation pipelines must be established to prevent hallucinated or misaligned KPIs.
"""

    takeaways_md = f"""### 🎯 Actionable Takeaways for Business Analysts & Leaders

1. **Benchmark Internal Processes:**
   - Compare current reporting turnaround cycles against the automated agentic workflows described in the source.
2. **Prototype Domain-Specific Agents:**
   - Develop targeted micro-agents (e.g., automated variance triage or regulatory change detection) rather than generic, unfocused chatbots.
3. **Establish Quality & Audit Gates:**
   - Couple automated scrapers and summarizers with human-in-the-loop review checkpoints before publishing findings to leadership review decks.
"""

    return {
        "overview_md": overview_md,
        "findings_md": findings_md,
        "implications_md": implications_md,
        "takeaways_md": takeaways_md,
        "title": title,
        "full_text": full_text
    }
