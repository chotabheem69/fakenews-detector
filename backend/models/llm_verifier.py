"""
Multi-Provider LLM Fact-Checking and Verification Engine.
Supports FreeLLMAPI, OpenAI-compatible APIs (OpenRouter, Groq, Ollama), and Google Gemini.
"""

import os
import re
import json
import logging
import requests
from typing import Dict, Any, Optional
from backend.config import LLM_PROVIDER, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

GEMINI_CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

DEFAULT_FREELLMAPI_URL = "https://api.freellmapi.com/v1"

def clean_base_url(url: Optional[str]) -> str:
    """Normalize base URL to avoid trailing slashes."""
    u = (url or LLM_BASE_URL or DEFAULT_FREELLMAPI_URL).strip()
    return u.rstrip("/")

def verify_llm_api_key(
    api_key: str, 
    provider: str = "freellmapi", 
    base_url: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test if an API key connects successfully for the selected provider.
    """
    key = api_key.strip()
    if not key:
        return {"valid": False, "message": "API key cannot be empty."}

    prov = (provider or "freellmapi").lower()

    # 1. Google Gemini Provider
    if prov == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                return {"valid": True, "message": "Connected successfully to Google Gemini API!"}
            else:
                data = res.json()
                err = data.get("error", {}).get("message", "Invalid Gemini key")
                return {"valid": False, "message": f"Gemini error: {err}"}
        except Exception as e:
            return {"valid": False, "message": f"Connection error: {str(e)}"}

    # 2. FreeLLMAPI & OpenAI-Compatible Providers
    base = clean_base_url(base_url)
    target_model = model or "llama-3.1-70b"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    # First attempt: query models endpoint
    try:
        models_url = f"{base}/models"
        res = requests.get(models_url, headers=headers, timeout=8)
        if res.status_code == 200:
            return {"valid": True, "message": f"Connected to {prov.upper()} via {base}!"}
    except Exception:
        pass

    # Second attempt: lightweight 1-token completion test
    try:
        chat_url = f"{base}/chat/completions"
        test_payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 3
        }
        res = requests.post(chat_url, headers=headers, json=test_payload, timeout=10)
        if res.status_code == 200:
            return {"valid": True, "message": f"Verified key successfully on {prov.upper()} ({target_model})!"}
        else:
            try:
                err_json = res.json()
                err_msg = err_json.get("error", {}).get("message", res.text[:120])
            except Exception:
                err_msg = res.text[:120]
            return {"valid": False, "message": f"Provider returned status {res.status_code}: {err_msg}"}
    except Exception as e:
        return {"valid": False, "message": f"Could not reach {base}: {str(e)}"}


def analyze_with_llm(
    title: str,
    content: str,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    bert_verdict: str = "UNCERTAIN",
    credibility_score: float = 50.0
) -> Dict[str, Any]:
    """
    Perform deep forensic fact-checking with the selected LLM provider.
    """
    prov = (provider or LLM_PROVIDER or "freellmapi").lower()
    key = (api_key or LLM_API_KEY or os.getenv("GEMINI_API_KEY", "")).strip()

    if not key:
        return {
            "enabled": False,
            "verdict": None,
            "explanation": "No LLM API Key provided. Add your FreeLLMAPI or Gemini key in Settings or .env to enable Deep AI Fact-Checking.",
            "claims_breakdown": [],
            "logical_fallacies": [],
            "reputable_search_queries": []
        }

    system_instruction = (
        "You are VeritasAI, a world-class investigative journalist and forensic misinformation analyst. "
        "Your task is to analyze news headlines and articles to identify false claims, deceptive phrasing, "
        "conspiracy theories, fabricated statistics, or verify accurate reporting."
    )

    prompt = f"""
Analyze the following news item for factual accuracy, credibility, and misinformation.

ARTICLE TITLE: {title}
ARTICLE CONTENT:
{content[:2500]}

BASELINE NLP/BERT DETECTOR ESTIMATE:
Verdict: {bert_verdict} (Score: {credibility_score}/100)

Return your forensic analysis strictly in the following JSON format:
{{
    "verdict": "REAL" or "FAKE" or "UNCERTAIN" or "SATIRE",
    "gemini_credibility_score": <number between 0.0 and 100.0>,
    "summary_verdict": "<short 1-2 sentence executive verdict>",
    "detailed_reasoning": "<clear paragraph explaining why it is credible, misleading, or fabricated>",
    "claims_analysis": [
        {{
            "claim": "<specific statement extracted from article>",
            "status": "VERIFIED" or "DISPROVEN" or "UNSUBSTANTIATED",
            "explanation": "<brief factual debunk or confirmation>"
        }}
    ],
    "logical_fallacies": ["<fallacy 1 e.g. False Cause, Cherry Picking, Appeal to Emotion>", "..."],
    "recommended_sources": ["<Trusted outlet or database to cross-reference e.g. Reuters, NASA, WHO>"],
    "cross_reference_search_query": "<exact Google search query user can search to verify this news>"
}}
Only return raw valid JSON. Do not include markdown code block quotes.
"""

    # ROUTE 1: Google Gemini API
    if prov == "gemini":
        return _call_gemini_api(system_instruction, prompt, key, bert_verdict)

    # ROUTE 2: FreeLLMAPI / OpenAI-Compatible Provider
    return _call_openai_compatible_api(
        system_instruction=system_instruction,
        prompt=prompt,
        key=key,
        base_url=clean_base_url(base_url),
        model=model or LLM_MODEL or "llama-3.1-70b",
        provider_name=prov,
        bert_verdict=bert_verdict
    )


def _call_openai_compatible_api(
    system_instruction: str,
    prompt: str,
    key: str,
    base_url: str,
    model: str,
    provider_name: str,
    bert_verdict: str
) -> Dict[str, Any]:
    """Call FreeLLMAPI or any OpenAI-compatible endpoint."""
    chat_url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1200
    }

    try:
        res = requests.post(chat_url, headers=headers, json=payload, timeout=24)
        if res.status_code != 200:
            logger.error(f"{provider_name} returned status {res.status_code}: {res.text}")
            return {
                "enabled": False,
                "error": f"LLM provider ({provider_name}) returned status {res.status_code}",
                "explanation": f"API request failed with status {res.status_code}. Response: {res.text[:140]}"
            }

        data = res.json()
        raw_text = data["choices"][0]["message"]["content"].strip()
        parsed = _parse_json_response(raw_text, bert_verdict)
        parsed["model_used"] = f"{provider_name.upper()} ({model})"
        return parsed

    except Exception as e:
        logger.error(f"Error calling {provider_name}: {e}")
        return {
            "enabled": False,
            "error": str(e),
            "explanation": f"Could not perform verification via {provider_name}: {str(e)}"
        }


def _call_gemini_api(
    system_instruction: str,
    prompt: str,
    key: str,
    bert_verdict: str
) -> Dict[str, Any]:
    """Call Google Gemini API with fallback across model names."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1000
        }
    }

    try:
        response_data = None
        last_err = ""
        used_model = "gemini-2.5-flash"
        for model_name in GEMINI_CANDIDATE_MODELS:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            res = requests.post(endpoint, headers=headers, json=payload, timeout=18)
            if res.status_code == 200:
                response_data = res.json()
                used_model = model_name
                break
            else:
                last_err = f"{res.status_code}: {res.text}"

        if not response_data:
            return {
                "enabled": False,
                "error": f"Gemini API call failed: {last_err}",
                "explanation": "Gemini API request failed. Please check your API key quota or validity."
            }

        raw_text = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = _parse_json_response(raw_text, bert_verdict)
        parsed["model_used"] = f"Google Gemini ({used_model})"
        return parsed

    except Exception as e:
        return {
            "enabled": False,
            "error": str(e),
            "explanation": f"Could not perform Gemini verification: {str(e)}"
        }


def _parse_json_response(raw_text: str, default_verdict: str) -> Dict[str, Any]:
    """Helper to parse JSON from LLM output with markdown stripping."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        parsed["enabled"] = True
        return parsed
    except json.JSONDecodeError:
        # Fallback if LLM returned text instead of pure JSON
        return {
            "enabled": True,
            "verdict": default_verdict,
            "summary_verdict": "Forensic audit completed.",
            "detailed_reasoning": raw_text[:500],
            "claims_analysis": [],
            "logical_fallacies": []
        }

