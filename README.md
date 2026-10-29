# 🛡️ VeritasAI — Fake News & Misinformation Detector

VeritasAI is an artificial intelligence platform designed to detect, analyze, and debunk fake news, deceptive media, and hyper-partisan misinformation. It combines **BERT (Bidirectional Encoder Representations from Transformers)** for deep sequence classification, a multi-factor **NLP Stylometric Engine**, and an optional **Google Gemini Deep Fact-Checking Agent** for forensic claim verification.

---

## ✨ Standout Features

- **🧠 Dual-Engine Hybrid Architecture:**
  - **Local BERT Classifier:** Fast, privacy-preserving transformer sequence classification running locally.
  - **Google Gemini Deep AI Audit:** Performs semantic claim extraction, checks historical facts, identifies logical fallacies (cherry-picking, appeal to emotion, false dilemmas), and generates a forensic verdict.
- **🔍 Explainable AI (XAI) Token Inspector:**
  - Dynamically highlights in-text red flags: sensationalism, clickbait engagement triggers, conspiracy markers, and uncharacteristic all-caps shouting.
- **📊 Multi-Factor Credibility Scoring:**
  - **Truth Probability Score (0–100%)**
  - **Sensationalism Index** (evaluates emotional hyperbole)
  - **Clickbait Level** (detects baiting headline templates)
  - **Bias & Conspiracy Index** (flags known conspiracy tropes)
  - **Source Attribution Quality** (evaluates presence of named sources, academic journals, or verified news wire services)
- **🌐 Web URL Article Scraper:**
  - Automatically extracts headlines, body copy, and evaluates domain reputation (e.g. wire services vs flagged satire/hoax domains).
- **⚖️ Side-by-Side Comparison Tool:**
  - Compare two versions or conflicting reports side by side to see how linguistic framing affects credibility scores.
- **📈 Analytics & History Dashboard:**
  - Persistent SQLite storage for audit trails, search/delete capabilities, and Chart.js distribution charts.
- **🎨 Modern UI/UX:**
  - Built with responsive design, glassmorphism, instant 1-click test benchmarks, and seamless Dark/Light mode switching.

---

## 🔑 How to Add Your API Key (FreeLLMAPI, Gemini, or OpenAI-Compatible)

VeritasAI works immediately offline with the built-in BERT & NLP classifier. To enable **Deep AI Fact-Checking**, you can connect **FreeLLMAPI**, **Google Gemini**, or any **OpenAI-compatible API** (OpenRouter, Groq, Ollama, etc.).

### Method 1: Directly in the Web UI (Easiest)
1. Start the app by running `python run.py`.
2. Click the **Settings Gear Icon (⚙️)** in the top-right navigation bar.
3. Select your provider:
   - **🌟 FreeLLMAPI:** Default endpoint `https://api.freellmapi.com/v1`, Model `llama-3.1-70b` (or any free tier model).
   - **🔷 Google Gemini:** Uses your free Google AI Studio key.
   - **🚀 OpenRouter / Groq / Custom:** Allows entering your custom base URL (e.g. `https://openrouter.ai/api/v1` or `http://localhost:11434/v1`) and target model.
4. Enter your API key.
5. Click **"Test Connection"** — the system will ping the endpoint and confirm connectivity.
6. Click **"Save Credentials"**. The top status badge will immediately display **`BERT + FreeLLMAPI Live`**!

### Method 2: In the `.env` File
1. In the project root, copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and specify your credentials:
   ```env
   # Provider: 'freellmapi', 'gemini', or 'openai_compatible'
   LLM_PROVIDER=freellmapi
   LLM_API_KEY=your_freellmapi_key_here
   LLM_BASE_URL=https://api.freellmapi.com/v1
   LLM_MODEL=llama-3.1-70b
   ```
3. Restart `python run.py`.

### Method 3: Via Environment Variables (Terminal)
- **Windows PowerShell:**
  ```powershell
  $env:LLM_PROVIDER="freellmapi"
  $env:LLM_API_KEY="your_api_key_here"
  $env:LLM_BASE_URL="https://api.freellmapi.com/v1"
  python run.py
  ```
- **Windows Command Prompt (CMD):**
  ```cmd
  set LLM_PROVIDER=freellmapi
  set LLM_API_KEY=your_api_key_here
  set LLM_BASE_URL=https://api.freellmapi.com/v1
  python run.py
  ```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python run.py
```
This automatically starts the FastAPI backend server and launches your default browser at `http://127.0.0.1:8000`.

---

## 🎓 IEEE DataPort Dataset Resource & Fine-Tuning

The platform is directly integrated with the [IEEE DataPort Fake News Dataset](https://ieee-dataport.org/documents/fake-news-dataset), which curates verified real news wire statements and deceptive viral market stories across politics, public health, finance, and technology.

### 🌟 In-App IEEE Dataset Explorer
- Access the **IEEE Dataset** tab directly inside the website.
- Search and filter authentic wire stories vs viral market hoaxes.
- Inspect linguistic deception markers, word counts, and verified citations.
- Click **"Test in Detector"** on any dataset record to instantly load and analyze it with BERT and FreeLLMAPI/Gemini!

### 🏋️ Fine-Tuning BERT on the IEEE Dataset
To fine-tune BERT on the IEEE DataPort dataset:
```bash
python train_bert.py --data_path data/ieee_fake_news_dataset.csv --epochs 3 --batch_size 16 --output_dir saved_models/bert_fake_news
```
*Note: If you have downloaded an updated or extended CSV from IEEE DataPort, simply save it into `data/` and pass its filename to `--data_path`.*

### Architecture Pipeline
```
Input News Text
      │
      ▼
WordPiece Tokenizer ([CLS] + Tokens + [SEP])
      │
      ▼
12-Layer Bidirectional Transformer (BERT / DistilBERT)
      │
      ▼
[CLS] Pooled Hidden State (768-dimensional vector)
      │
      ▼
Dropout Layer (p=0.3)
      │
      ▼
Linear Classification Head: Linear(768, 2)
      │
      ▼
Softmax Probabilities: [P(Fake), P(Real)]
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Analyze raw text/headline for misinformation |
| `POST` | `/api/analyze-url` | Scrape article from a URL and analyze credibility |
| `GET` | `/api/samples` | Retrieve curated real/fake news benchmarks |
| `GET` | `/api/history` | Retrieve historical scan records |
| `DELETE` | `/api/history/{id}` | Delete a specific scan record |
| `POST` | `/api/history/clear` | Clear all scan history |
| `GET` | `/api/stats` | Aggregate dashboard statistics |
| `POST` | `/api/verify-key` | Test connection to Google Gemini API |
| `POST` | `/api/save-key` | Save Gemini API key to local `.env` |
| `GET` | `/docs` | Interactive Swagger/OpenAPI documentation |

---

## 📁 Project Structure

```
fakenews_detector/
├── backend/
│   ├── config.py              # Configuration and .env loading
│   ├── database.py            # SQLite scan history & analytics
│   ├── main.py                # FastAPI server entrypoint
│   ├── models/
│   │   ├── bert_classifier.py # BERT Sequence Classification engine
│   │   ├── nlp_analyzer.py    # Stylometry & Explainable AI (XAI)
│   │   ├── gemini_verifier.py # Google Gemini deep fact-check agent
│   │   └── url_extractor.py   # Article web scraper & domain checks
│   └── routes/
│       └── api.py             # REST API routes
├── static/
│   ├── index.html             # Single Page Application UI
│   ├── styles.css             # Responsive styling & themes
│   └── app.js                 # Frontend application logic
├── data/                      # Local SQLite database & datasets
├── train_bert.py              # PyTorch fine-tuning script for IEEE dataset
├── run.py                     # 1-click application launcher
├── requirements.txt           # Python package requirements
├── .env.example               # Environment variables template
└── README.md                  # Comprehensive project documentation
```
