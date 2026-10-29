"""
VeritasAI Pre-Flight System Verification Script.
Tests all internal modules, database initialization, and classification pipelines.
"""

import sys
from pathlib import Path

def run_tests():
    print("=" * 60)
    print("🛡️  VERITAS AI - SYSTEM INTEGRATION TESTS")
    print("=" * 60)

    # 1. Config Test
    try:
        from backend.config import BASE_DIR, STATIC_DIR, DB_PATH
        print(f"✓ Config loaded: Base directory = {BASE_DIR}")
        print(f"✓ Static assets directory = {STATIC_DIR} (Exists: {STATIC_DIR.exists()})")
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

    # 2. Database Test
    try:
        from backend.database import init_db, save_scan, get_history, get_stats
        init_db()
        print("✓ SQLite Database successfully initialized.")
        stats = get_stats()
        print(f"✓ Database stats query verified (Total records: {stats['total_scans']}).")
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

    # 3. NLP Stylometric Analyzer Test
    try:
        from backend.models.nlp_analyzer import analyze_linguistic_cues
        sample_fake = "SHOCKING: Boiling lemon peels cures cancer in 24 hours! Big Pharma in panic!"
        res = analyze_linguistic_cues(sample_fake, title="Miracle Cure")
        print(f"✓ NLP Analyzer OK - Sensationalism: {res['sensationalism_score']}%, Clickbait: {res['clickbait_score']}%")
        assert res['sensationalism_score'] > 20, "Expected sensationalism detection"
    except Exception as e:
        print(f"✗ NLP Analyzer test failed: {e}")
        return False

    # 4. BERT Classifier Engine Test
    try:
        from backend.models.bert_classifier import classifier
        prediction = classifier.predict("NASA Space Mission", "Astronomers confirm observation of early galaxy formation.", res)
        print(f"✓ Classifier Engine OK - Verdict: {prediction['verdict']}, Credibility: {prediction['credibility_score']}%, Model: {prediction['model_used']}")
    except Exception as e:
        print(f"✗ Classifier Engine test failed: {e}")
        return False

    # 5. LLM Multi-Provider Verifier Test
    try:
        from backend.models.llm_verifier import verify_llm_api_key, analyze_with_llm
        print("✓ Multi-Provider LLM Engine loaded (FreeLLMAPI, OpenAI-compatible, Google Gemini).")
    except Exception as e:
        print(f"✗ LLM Verifier test failed: {e}")
        return False

    # 6. IEEE DataPort Dataset Manager Test
    try:
        from backend.models.dataset_manager import load_ieee_dataset, get_ieee_dataset_stats, query_dataset
        ds_stats = get_ieee_dataset_stats()
        print(f"✓ IEEE DataPort Dataset Engine loaded: {ds_stats['total_articles']} market articles ({ds_stats['real_count']} Real, {ds_stats['fake_count']} Fake).")
    except Exception as e:
        print(f"✗ Dataset manager test failed: {e}")
        return False

    # 7. FastAPI App Test
    try:
        from backend.main import app
        print("✓ FastAPI application & routes successfully loaded.")
        print(f"✓ Number of API endpoints: {len(app.routes)}")
    except Exception as e:
        print(f"✗ FastAPI app loading test failed: {e}")
        return False

    print("=" * 60)
    print("🎉 ALL VERITAS AI COMPONENTS INTEGRATED & READY TO RUN!")
    print("=" * 60)
    print("To launch the website, run:")
    print("   python run.py")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

