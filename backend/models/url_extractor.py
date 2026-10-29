"""
URL Article Extractor and Domain Reputation Evaluator.
Scrapes title, author, body paragraphs, and checks domain reputation.
"""

import re
import requests
from urllib.parse import urlparse
from typing import Dict, Any
from bs4 import BeautifulSoup

KNOWN_REPUTABLE_DOMAINS = {
    "reuters.com": "High Credibility Global Wire Service",
    "apnews.com": "High Credibility Global Wire Service",
    "bbc.com": "High Credibility Public Broadcaster",
    "bbc.co.uk": "High Credibility Public Broadcaster",
    "nature.com": "High Credibility Peer-Reviewed Science",
    "sciencemag.org": "High Credibility Peer-Reviewed Science",
    "who.int": "Official International Health Authority",
    "cdc.gov": "Official Government Health Agency",
    "nasa.gov": "Official Government Space Agency",
    "nytimes.com": "Major News Organization",
    "washingtonpost.com": "Major News Organization",
    "theguardian.com": "Major News Organization",
    "bloomberg.com": "Major Financial News Outlet",
    "wsj.com": "Major Financial News Outlet",
    "npr.org": "High Credibility Public Radio"
}

KNOWN_SATIRE_OR_UNRELIABLE = {
    "theonion.com": "Satire / Parody Publication",
    "babylonbee.com": "Satire / Parody Publication",
    "infowars.com": "Known Misinformation / Conspiracy Source",
    "naturalnews.com": "Known Pseudoscience / Health Misinformation",
    "worldnewsdailyreport.com": "Fabricated Fake News / Hoax Site"
}

def extract_article_from_url(url: str) -> Dict[str, Any]:
    """
    Extract article content from a given web URL.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    # Check domain reputation
    domain_category = "Unknown / Independent Domain"
    domain_badge = "neutral"
    
    for rep_domain, desc in KNOWN_REPUTABLE_DOMAINS.items():
        if domain == rep_domain or domain.endswith("." + rep_domain):
            domain_category = f"Reputable Source: {desc}"
            domain_badge = "reputable"
            break
            
    for fake_domain, desc in KNOWN_SATIRE_OR_UNRELIABLE.items():
        if domain == fake_domain or domain.endswith("." + fake_domain):
            domain_category = f"Flagged Source: {desc}"
            domain_badge = "flagged"
            break

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Extract title
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]
        elif soup.title:
            title = soup.title.string or ""
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Extract body text from article tags or paragraphs
        paragraphs = []
        article_tag = soup.find("article")
        target = article_tag if article_tag else soup.body

        if target:
            for p in target.find_all("p"):
                txt = p.get_text(strip=True)
                # Filter out cookie banners, short copyright notes
                if len(txt) > 35 and not any(kw in txt.lower() for kw in ["cookies", "subscribe", "privacy policy"]):
                    paragraphs.append(txt)

        content = "\n\n".join(paragraphs)
        if not content and target:
            content = target.get_text(separator="\n", strip=True)

        return {
            "success": True,
            "url": url,
            "domain": domain,
            "domain_category": domain_category,
            "domain_badge": domain_badge,
            "title": title.strip() or "Untitled Web Article",
            "content": content[:5000].strip(),
            "word_count": len(content.split())
        }

    except Exception as e:
        return {
            "success": False,
            "url": url,
            "domain": domain,
            "domain_category": domain_category,
            "domain_badge": domain_badge,
            "title": "",
            "content": "",
            "error": f"Failed to extract article: {str(e)}"
        }

