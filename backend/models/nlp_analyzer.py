"""
Linguistic and Stylometric NLP Analyzer for Fake News Detection.
Extracts explainable features: Sensationalism, Clickbait, Bias, Attribution, and Stylistic Anomalies.
"""

import re
from typing import Dict, List, Any, Tuple

# Dictionaries of linguistic cues
SENSATIONAL_WORDS = {
    "shocking", "unbelievable", "mind-blowing", "miracle", "bombshell", 
    "explosive", "scandalous", "horrifying", "insane", "bizarre", 
    "catastrophic", "apocalyptic", "terrifying", "monstrous", "astonishing",
    "jaw-dropping", "unreal", "disastrous", "devastating", "panic"
}

CLICKBAIT_PATTERNS = [
    r"you won'?t believe",
    r"what happens next",
    r"before it gets deleted",
    r"share this (now|immediately|before)",
    r"they don'?t want you to know",
    r"will blow your mind",
    r"the truth about",
    r"secret trick",
    r"number \d+ will shock you",
    r"everyone is talking about",
    r"doctors hate this",
    r"the mainstream media is silent"
]

CONSPIRACY_MARKERS = {
    "deep state", "big pharma", "cover-up", "suppressed cure", "hidden truth",
    "globalist agenda", "microchip", "chemtrails", "illuminati", "hoax",
    "staged event", "crisis actors", "plandemic", "puppet masters", "secret elite"
}

VAGUE_ATTRIBUTION = [
    r"sources say",
    r"insiders reveal",
    r"anonymous officials",
    r"experts claim",
    r"studies suggest",
    r"people are saying",
    r"some say that",
    r"many believe",
    r"it has been reported"
]

CREDIBLE_ATTRIBUTION = [
    r"according to (the )?(associated press|reuters|afp|bloomberg|bbc|who|cdc|nasa)",
    r"published in (the journal |nature|science|the lancet|nejm)",
    r"stated during a press conference",
    r"official statement by",
    r"spokesperson (for|said)",
    r"confirmed by university researchers",
    r"in a peer-reviewed study",
    r"department of (justice|defense|health|energy|state)"
]

def analyze_linguistic_cues(text: str, title: str = "") -> Dict[str, Any]:
    """
    Perform deep linguistic feature analysis on news text and title.
    Returns quantitative scores and extracted explainability tokens.
    """
    full_text = f"{title} {text}".strip()
    words = re.findall(r"\b[A-Za-z0-9_-]+\b", full_text)
    total_words = max(len(words), 1)
    
    lowered = full_text.lower()
    
    # 1. Sensationalism Analysis
    found_sensational = [w for w in words if w.lower() in SENSATIONAL_WORDS]
    sensational_density = (len(found_sensational) / total_words) * 100
    sensationalism_score = min(100.0, round(sensational_density * 25.0 + (len(found_sensational) * 8.0), 1))
    
    # 2. Clickbait Pattern Matching
    found_clickbait = []
    for pattern in CLICKBAIT_PATTERNS:
        matches = re.findall(pattern, lowered)
        if matches:
            found_clickbait.append(pattern.replace(r"\b", "").replace("?", ""))
    
    # Extra clickbait penalty if in title
    title_upper_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
    has_question_headline = title.strip().endswith("?")
    
    clickbait_score = min(100.0, round(
        (len(found_clickbait) * 30.0) + 
        (35.0 if title_upper_ratio > 0.4 and len(title) > 10 else 0.0) +
        (20.0 if has_question_headline else 0.0)
    , 1))

    # 3. Conspiracy & Bias Markers
    found_conspiracy = [marker for marker in CONSPIRACY_MARKERS if marker in lowered]
    bias_score = min(100.0, round((len(found_conspiracy) * 30.0) + (sensationalism_score * 0.4), 1))

    # 4. Source Attribution Quality
    vague_count = 0
    for pattern in VAGUE_ATTRIBUTION:
        vague_count += len(re.findall(pattern, lowered))
        
    credible_count = 0
    for pattern in CREDIBLE_ATTRIBUTION:
        credible_count += len(re.findall(pattern, lowered))
        
    # Baseline 50, higher with verified attribution, lower with vague/ghost attribution
    attribution_score = 50.0 + (credible_count * 20.0) - (vague_count * 15.0)
    attribution_score = max(5.0, min(95.0, round(attribution_score, 1)))

    # 5. Stylistic & Punctuation Anomalies
    exclamation_count = full_text.count("!")
    exclamation_ratio = exclamation_count / max(len(re.split(r'[.!?]+', full_text)), 1)
    
    # All-caps words (ignoring short acronyms <= 3 letters)
    caps_words = [w for w in words if len(w) > 3 and w.isupper()]
    caps_ratio = len(caps_words) / total_words
    
    # Lexical Diversity (Type-Token Ratio)
    unique_words = set(w.lower() for w in words)
    lexical_diversity = round((len(unique_words) / total_words) * 100, 1)

    # 6. Flagged tokens and phrases for Explainable Highlight UI
    highlight_tokens = []
    
    for w in set(found_sensational):
        highlight_tokens.append({
            "term": w,
            "category": "sensationalism",
            "description": "Sensationalist / Hyperbolic Term"
        })
    for m in found_conspiracy:
        highlight_tokens.append({
            "term": m,
            "category": "bias",
            "description": "Common Misinformation / Conspiracy Marker"
        })
    for cb in found_clickbait:
        highlight_tokens.append({
            "term": cb,
            "category": "clickbait",
            "description": "Clickbait Engagement Bait"
        })
    for cw in caps_words[:5]:
        highlight_tokens.append({
            "term": cw,
            "category": "shouting",
            "description": "Uncharacteristic ALL-CAPS Shouting"
        })

    # Key Claims Heuristic Extraction
    sentences = [s.strip() for s in re.split(r'[.!?]+', full_text) if len(s.strip()) > 20]
    key_claims = sentences[:3] if sentences else [full_text[:120]]

    return {
        "sensationalism_score": sensationalism_score,
        "clickbait_score": clickbait_score,
        "bias_score": bias_score,
        "source_attribution_score": attribution_score,
        "exclamation_ratio": round(exclamation_ratio, 2),
        "all_caps_words_count": len(caps_words),
        "lexical_diversity": lexical_diversity,
        "highlight_tokens": highlight_tokens,
        "key_claims": key_claims,
        "found_sensational": list(set(found_sensational)),
        "found_conspiracy": found_conspiracy,
        "credible_mentions": credible_count
    }

