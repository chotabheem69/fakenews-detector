"""
VeritasAI NLP & Machine Learning Models Package.
"""
from backend.models.nlp_analyzer import analyze_linguistic_cues
from backend.models.bert_classifier import FakeNewsClassifier, classifier
from backend.models.gemini_verifier import analyze_with_gemini, verify_gemini_api_key
from backend.models.llm_verifier import analyze_with_llm, verify_llm_api_key
from backend.models.url_extractor import extract_article_from_url
from backend.models.dataset_manager import load_ieee_dataset, query_dataset, get_ieee_dataset_stats

__all__ = [
    "analyze_linguistic_cues",
    "FakeNewsClassifier",
    "classifier",
    "analyze_with_gemini",
    "verify_gemini_api_key",
    "analyze_with_llm",
    "verify_llm_api_key",
    "extract_article_from_url",
    "load_ieee_dataset",
    "query_dataset",
    "get_ieee_dataset_stats"
]

