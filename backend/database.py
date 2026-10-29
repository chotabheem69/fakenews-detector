"""
Database management for VeritasAI using SQLite.
Stores scan history, credibility scores, metrics, and analytics.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content_preview TEXT,
            source_type TEXT, -- 'text' or 'url'
            source_url TEXT,
            verdict TEXT, -- 'REAL', 'FAKE', 'UNCERTAIN'
            credibility_score REAL, -- 0.0 to 100.0
            confidence REAL, -- 0.0 to 1.0
            sensationalism_score REAL,
            bias_score REAL,
            source_attribution_score REAL,
            key_claims TEXT, -- JSON array
            suspicious_tokens TEXT, -- JSON array
            gemini_explanation TEXT,
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_scan(scan_data: Dict[str, Any]) -> int:
    """Save analysis record into database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    key_claims_json = json.dumps(scan_data.get("key_claims", []))
    suspicious_tokens_json = json.dumps(scan_data.get("suspicious_tokens", []))
    
    cursor.execute("""
        INSERT INTO scans (
            title, content_preview, source_type, source_url,
            verdict, credibility_score, confidence,
            sensationalism_score, bias_score, source_attribution_score,
            key_claims, suspicious_tokens, gemini_explanation, model_used, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_data.get("title", "Untitled Article")[:250],
        scan_data.get("content", "")[:300],
        scan_data.get("source_type", "text"),
        scan_data.get("source_url", ""),
        scan_data.get("verdict", "UNCERTAIN"),
        scan_data.get("credibility_score", 50.0),
        scan_data.get("confidence", 0.5),
        scan_data.get("sensationalism_score", 0.0),
        scan_data.get("bias_score", 0.0),
        scan_data.get("source_attribution_score", 0.0),
        key_claims_json,
        suspicious_tokens_json,
        scan_data.get("gemini_explanation", ""),
        scan_data.get("model_used", "BERT + NLP"),
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ))
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id

def get_history(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Fetch recent scans."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM scans 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        item = dict(r)
        try:
            item["key_claims"] = json.loads(item["key_claims"] or "[]")
        except Exception:
            item["key_claims"] = []
        try:
            item["suspicious_tokens"] = json.loads(item["suspicious_tokens"] or "[]")
        except Exception:
            item["suspicious_tokens"] = []
        result.append(item)
    
    conn.close()
    return result

def delete_scan(scan_id: int) -> bool:
    """Delete a specific scan entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def clear_history() -> None:
    """Delete all scan history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans")
    conn.commit()
    conn.close()

def get_stats() -> Dict[str, Any]:
    """Retrieve aggregate statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM scans")
    total = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as real_cnt FROM scans WHERE verdict = 'REAL'")
    real_cnt = cursor.fetchone()["real_cnt"]
    
    cursor.execute("SELECT COUNT(*) as fake_cnt FROM scans WHERE verdict = 'FAKE'")
    fake_cnt = cursor.fetchone()["fake_cnt"]
    
    cursor.execute("SELECT AVG(credibility_score) as avg_score FROM scans")
    avg_score_row = cursor.fetchone()
    avg_credibility = round(avg_score_row["avg_score"] or 0, 1)
    
    conn.close()
    
    uncertain_cnt = total - (real_cnt + fake_cnt)
    
    return {
        "total_scans": total,
        "real_count": real_cnt,
        "fake_count": fake_cnt,
        "uncertain_count": max(0, uncertain_cnt),
        "real_percentage": round((real_cnt / total * 100), 1) if total > 0 else 0,
        "fake_percentage": round((fake_cnt / total * 100), 1) if total > 0 else 0,
        "avg_credibility_score": avg_credibility
    }

