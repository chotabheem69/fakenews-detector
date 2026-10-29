"""
Backward compatibility layer for Gemini verifier.
Delegates to the unified multi-provider llm_verifier.
"""
from backend.models.llm_verifier import (
    analyze_with_llm as analyze_with_gemini,
    verify_llm_api_key as verify_gemini_api_key
)

__all__ = ["analyze_with_gemini", "verify_gemini_api_key"]
