"""
FastAPI REST API routes for VeritasAI Fake News Detector.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from backend.config import ENV_FILE, GEMINI_API_KEY, LLM_PROVIDER, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from backend.models.nlp_analyzer import analyze_linguistic_cues
from backend.models.bert_classifier import classifier
from backend.models.llm_verifier import analyze_with_llm, verify_llm_api_key
from backend.models.url_extractor import extract_article_from_url
from backend.models.dataset_manager import load_ieee_dataset, query_dataset, get_ieee_dataset_stats
from backend.database import save_scan, get_history, delete_scan, clear_history, get_stats

router = APIRouter(prefix="/api")

# Pydantic Request Models
class AnalyzeTextRequest(BaseModel):
    title: Optional[str] = ""
    content: str = Field(..., min_length=5, description="Article body text or claim")
    api_key: Optional[str] = None
    provider: Optional[str] = "freellmapi"
    base_url: Optional[str] = None
    model: Optional[str] = None
    enable_deep_factcheck: Optional[bool] = False

class AnalyzeUrlRequest(BaseModel):
    url: str = Field(..., description="Full URL to the news article")
    api_key: Optional[str] = None
    provider: Optional[str] = "freellmapi"
    base_url: Optional[str] = None
    model: Optional[str] = None
    enable_deep_factcheck: Optional[bool] = False

class VerifyKeyRequest(BaseModel):
    api_key: str
    provider: Optional[str] = "freellmapi"
    base_url: Optional[str] = None
    model: Optional[str] = None

class SaveKeyRequest(BaseModel):
    api_key: str
    provider: Optional[str] = "freellmapi"
    base_url: Optional[str] = None
    model: Optional[str] = None

# Sample benchmarks for instant testing
SAMPLE_ARTICLES = [
    {
        "id": "real-1",
        "category": "Science & Space",
        "expected": "REAL",
        "title": "NASA's James Webb Space Telescope Captures Most Detailed View of Early Galaxies",
        "text": "Astronomers using NASA's James Webb Space Telescope have observed a cluster of massive galaxies forming in the early universe, just 600 million years after the Big Bang. According to a study published Thursday in Nature Astronomy, the observations confirm standard cosmological models of stellar nursery formation. Dr. Marcia Rieke, principal investigator for the NIRCam instrument at the University of Arizona, stated that spectroscopic measurements confirmed the high redshifts and elemental compositions of the stellar populations.",
        "source": "Nature / NASA Press Release"
    },
    {
        "id": "fake-1",
        "category": "Health & Pseudoscience",
        "expected": "FAKE",
        "title": "SHOCKING: Boiling Lemon Peels Cures All Cancers, Big Pharma Secret Exposed!",
        "text": "What happens next will blow your mind! Insiders reveal that boiling lemon peels with baking soda creates an alkaline compound that completely destroys 100% of cancer tumors in just 48 hours. The mainstream media and deep state medical elites are desperate to delete this before the public finds out. You won't believe how simple it is! Share this immediately with everyone you love before the pharmaceutical companies force this website down!",
        "source": "Viral Facebook Chain Post"
    },
    {
        "id": "real-2",
        "category": "Economics & Policy",
        "expected": "REAL",
        "title": "Federal Reserve Holds Benchmark Interest Rate Steady Amid Moderate Economic Growth",
        "text": "The Federal Reserve concluded its two-day policy meeting by keeping its benchmark interest rate unchanged at a range of 5.25% to 5.50%. In an official statement issued by the Federal Open Market Committee, officials noted that economic indicators point to resilient household spending and job gains, though inflation remains somewhat elevated above the 2% target. Chair Jerome Powell stated during the press conference that future decisions will be made on a meeting-by-meeting basis dependent on incoming data.",
        "source": "Federal Reserve / Financial Press"
    },
    {
        "id": "fake-2",
        "category": "Conspiracy & Technology",
        "expected": "FAKE",
        "title": "BOMBSHELL: Secret 5G Towers Are Broadcasting Mind-Control Frequencies to Control Elections!",
        "text": "Anonymous officials confirm that newly installed 5G antennas are secretly broadcasting pulsed electromagnetic mind-control waves to alter voter psychology. Insiders have exposed the horrifying truth that scientists have been silenced by government agents. You must disconnect your router immediately! The mainstream media refuses to cover this catastrophic conspiracy!",
        "source": "Anonymous Forum Blog"
    }
]

@router.post("/analyze")
async def analyze_text_endpoint(
    req: AnalyzeTextRequest, 
    x_api_key: Optional[str] = Header(None)
):
    """
    Analyze news text/headline with NLP stylometry, BERT classifier, and optional Gemini LLM audit.
    """
    title = (req.title or "").strip()
    content = req.content.strip()

    if not title and not content:
        raise HTTPException(status_code=400, detail="Either title or content must be provided.")

    effective_api_key = req.api_key or x_api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    # 1. Linguistic & Stylometric NLP Analysis
    nlp_data = analyze_linguistic_cues(content, title=title)

    # 2. BERT Classifier Inference
    bert_result = classifier.predict(title, content, nlp_data)

    # 3. LLM Deep Verification (FreeLLMAPI, OpenAI-compatible, or Gemini)
    llm_data = None
    if req.enable_deep_factcheck or (effective_api_key and len(effective_api_key) > 5):
        llm_data = analyze_with_llm(
            title=title or content[:60],
            content=content,
            provider=req.provider,
            api_key=effective_api_key,
            base_url=req.base_url,
            model=req.model,
            bert_verdict=bert_result["verdict"],
            credibility_score=bert_result["credibility_score"]
        )

    # Reconcile final verdict if LLM gave high-confidence audit
    final_verdict = bert_result["verdict"]
    final_credibility = bert_result["credibility_score"]
    
    if llm_data and llm_data.get("enabled") and "gemini_credibility_score" in llm_data:
        g_score = float(llm_data["gemini_credibility_score"])
        # Blended weighted score: 40% BERT stylometry, 60% LLM factual reasoning
        final_credibility = round((bert_result["credibility_score"] * 0.4) + (g_score * 0.6), 1)
        if final_credibility >= 60.0:
            final_verdict = "REAL"
        elif final_credibility <= 40.0:
            final_verdict = "FAKE"
        else:
            final_verdict = "UNCERTAIN"

    # 4. Save to Database
    model_name = llm_data.get("model_used", "BERT + LLM") if (llm_data and llm_data.get("enabled")) else bert_result["model_used"]
    scan_id = save_scan({
        "title": title or content[:80],
        "content": content,
        "source_type": "text",
        "source_url": "",
        "verdict": final_verdict,
        "credibility_score": final_credibility,
        "confidence": bert_result["confidence"],
        "sensationalism_score": nlp_data["sensationalism_score"],
        "bias_score": nlp_data["bias_score"],
        "source_attribution_score": nlp_data["source_attribution_score"],
        "key_claims": nlp_data["key_claims"],
        "suspicious_tokens": nlp_data["highlight_tokens"],
        "gemini_explanation": (llm_data.get("detailed_reasoning") if llm_data else ""),
        "model_used": model_name
    })

    return {
        "scan_id": scan_id,
        "title": title,
        "verdict": final_verdict,
        "credibility_score": final_credibility,
        "confidence": bert_result["confidence"],
        "bert_details": bert_result,
        "nlp_metrics": nlp_data,
        "gemini_audit": llm_data
    }

@router.post("/analyze-url")
async def analyze_url_endpoint(
    req: AnalyzeUrlRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Scrape article from a URL, then analyze its credibility.
    """
    url = req.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    extraction = extract_article_from_url(url)
    if not extraction.get("success"):
        raise HTTPException(status_code=400, detail=extraction.get("error", "Failed to extract article content."))

    title = extraction.get("title", "")
    content = extraction.get("content", "")

    if len(content) < 30:
        raise HTTPException(status_code=400, detail="The extracted page did not contain sufficient article text.")

    effective_api_key = req.api_key or x_api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    # Run analysis
    nlp_data = analyze_linguistic_cues(content, title=title)
    
    # Adjust attribution based on domain reputation
    if extraction.get("domain_badge") == "reputable":
        nlp_data["source_attribution_score"] = min(98.0, nlp_data["source_attribution_score"] + 30.0)
    elif extraction.get("domain_badge") == "flagged":
        nlp_data["source_attribution_score"] = max(5.0, nlp_data["source_attribution_score"] - 40.0)

    bert_result = classifier.predict(title, content, nlp_data)

    llm_data = None
    if req.enable_deep_factcheck or (effective_api_key and len(effective_api_key) > 5):
        llm_data = analyze_with_llm(
            title=title,
            content=content,
            provider=req.provider,
            api_key=effective_api_key,
            base_url=req.base_url,
            model=req.model,
            bert_verdict=bert_result["verdict"],
            credibility_score=bert_result["credibility_score"]
        )

    final_verdict = bert_result["verdict"]
    final_credibility = bert_result["credibility_score"]
    
    if llm_data and llm_data.get("enabled") and "gemini_credibility_score" in llm_data:
        g_score = float(llm_data["gemini_credibility_score"])
        final_credibility = round((bert_result["credibility_score"] * 0.4) + (g_score * 0.6), 1)
        if final_credibility >= 60.0:
            final_verdict = "REAL"
        elif final_credibility <= 40.0:
            final_verdict = "FAKE"
        else:
            final_verdict = "UNCERTAIN"

    model_name = llm_data.get("model_used", "BERT + LLM") if (llm_data and llm_data.get("enabled")) else bert_result["model_used"]
    scan_id = save_scan({
        "title": title,
        "content": content,
        "source_type": "url",
        "source_url": url,
        "verdict": final_verdict,
        "credibility_score": final_credibility,
        "confidence": bert_result["confidence"],
        "sensationalism_score": nlp_data["sensationalism_score"],
        "bias_score": nlp_data["bias_score"],
        "source_attribution_score": nlp_data["source_attribution_score"],
        "key_claims": nlp_data["key_claims"],
        "suspicious_tokens": nlp_data["highlight_tokens"],
        "gemini_explanation": (llm_data.get("detailed_reasoning") if llm_data else ""),
        "model_used": model_name
    })

    return {
        "scan_id": scan_id,
        "url_details": extraction,
        "title": title,
        "verdict": final_verdict,
        "credibility_score": final_credibility,
        "confidence": bert_result["confidence"],
        "bert_details": bert_result,
        "nlp_metrics": nlp_data,
        "gemini_audit": llm_data
    }

@router.get("/samples")
async def get_sample_articles():
    """Returns curated real and fake articles directly from the IEEE DataPort dataset."""
    items = load_ieee_dataset()
    samples = []
    for it in items[:6]:
        samples.append({
            "id": it["id"],
            "category": it["category"],
            "expected": it["verdict"],
            "title": it["title"],
            "text": it["text"],
            "source": it["source"]
        })
    return {"samples": samples}

@router.get("/dataset/items")
async def get_dataset_items(
    category: Optional[str] = "All",
    label: Optional[str] = "All",
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 6
):
    """Browse and search items from the IEEE DataPort Fake News dataset."""
    return query_dataset(category=category, label=label, search=search, page=page, limit=limit)

@router.get("/dataset/stats")
async def get_dataset_statistics():
    """Aggregate dataset statistics for the IEEE DataPort resource."""
    return get_ieee_dataset_stats()

@router.get("/history")
async def get_scan_history(limit: int = 50, offset: int = 0):
    """Fetch scan history records."""
    return {"history": get_history(limit=limit, offset=offset)}

@router.delete("/history/{scan_id}")
async def delete_scan_record(scan_id: int):
    """Delete an item from history."""
    success = delete_scan(scan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return {"success": True, "message": "Record deleted."}

@router.post("/history/clear")
async def clear_all_history():
    """Clear all records from database."""
    clear_history()
    return {"success": True, "message": "History cleared."}

@router.get("/stats")
async def get_overview_statistics():
    """Aggregate statistics for dashboard."""
    return get_stats()

@router.post("/verify-key")
async def verify_key_endpoint(req: VerifyKeyRequest):
    """Check if provided FreeLLMAPI, OpenAI, or Gemini key connects successfully."""
    result = verify_llm_api_key(
        api_key=req.api_key.strip(),
        provider=req.provider or "freellmapi",
        base_url=req.base_url,
        model=req.model
    )
    return result

@router.post("/save-key")
async def save_key_to_env(req: SaveKeyRequest):
    """
    Save the API configuration securely to the project's local .env file.
    """
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key is empty.")
    
    provider = req.provider or "freellmapi"
    base_url = req.base_url or "https://api.freellmapi.com/v1"
    model = req.model or "llama-3.1-70b"

    # Read existing .env
    env_lines = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            env_lines = f.read().splitlines()

    config_dict = {
        "LLM_PROVIDER": provider,
        "LLM_API_KEY": key,
        "LLM_BASE_URL": base_url,
        "LLM_MODEL": model,
        "GEMINI_API_KEY": key if provider == "gemini" else ""
    }

    new_lines = []
    keys_handled = set()
    for line in env_lines:
        matched = False
        for k, v in config_dict.items():
            if line.startswith(f"{k}="):
                new_lines.append(f"{k}={v}")
                keys_handled.add(k)
                matched = True
                break
        if not matched:
            new_lines.append(line)

    for k, v in config_dict.items():
        if k not in keys_handled and v:
            new_lines.append(f"{k}={v}")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

    os.environ["LLM_PROVIDER"] = provider
    os.environ["LLM_API_KEY"] = key
    os.environ["LLM_BASE_URL"] = base_url
    os.environ["LLM_MODEL"] = model
    if provider == "gemini":
        os.environ["GEMINI_API_KEY"] = key

    return {"success": True, "message": f"{provider.upper()} API credentials saved to .env file!"}

