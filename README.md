# 📡 AI Web Signal Hunter

**Autonomous Web Intelligence & Market Opportunity Discovery Engine**

AI Web Signal Hunter is a production-ready, full-stack Python application that crawls public web discussions, extracts verified market signals using Large Language Models (Groq or Google Gemini), groups recurring themes, and ranks business opportunities using an audited mathematical formula backed by verbatim evidence quotes.

---

## 🌟 Key Features

- **Autonomous Public Web Crawler**:
  - Collects 25+ relevant public web pages across 3+ permitted domains.
  - Full **`robots.txt`** checking (`urllib.robotparser.RobotFileParser`).
  - Politeness delays (0.8s) and custom descriptive `User-Agent`.
  - Canonical URL normalization and cryptographic content-based deduplication (SHA-256).
  - Robust HTML cleaning via BeautifulSoup: strips navigation, scripts, stylesheets, cookie consent modals, and advertising boilerplate.
  - Zero fake data: records exact counts, status codes, and crawl limitations transparently.

- **AI-Powered Signal Extraction**:
  - Supports **Groq API** (`llama-3.3-70b-versatile`) and **Google Gemini API** (`gemini-1.5-flash`).
  - Signal taxonomy:
    - **Pain Points**
    - **Demand Signals**
    - **Feature Requests**
    - **Pricing Concerns**
    - **Competitor Activity**
    - **Irrelevant Content**
  - **Evidence Verification**: Verifies every excerpt against raw crawled text.
  - **Strict Prompt Injection Guard**: Treats all crawled content as untrusted input wrapped in `<untrusted_web_content>` tags.
  - **Pydantic Validation**: Guarantees structured JSON schemas and enforces the max 30 words rule on quotes.
  - Built-in heuristic pattern engine fallback when API keys are unconfigured.

- **Opportunity Discovery & Ranking Index**:
  - Automatically groups signals into recurring market themes.
  - Calculates transparent **Opportunity Scores** (0 to 100):
    $$\text{Opportunity Score} = 0.30 \times \text{Relevance} + 0.25 \times \text{Urgency} + 0.20 \times \text{Confidence} + 0.15 \times \text{Frequency} + 0.10 \times \text{Recency}$$
  - Synthesizes top 5 prioritized Opportunity Briefs with clickable source citations and practical validation next steps.

- **Modern SaaS Dashboard & Findings Ledger**:
  - Built with Streamlit, Plotly, and custom SaaS design.
  - Real-time workflow tracking with execution status.
  - Interactive charts: Category donut chart, Theme score comparison, and Domain coverage.
  - Filterable findings ledger (category, domain, relevance, opportunity score, search text).
  - Deep-dive signal inspector showing verbatim quotes, AI reasoning, and source metadata.

- **Exports & Persistence**:
  - Persistent SQLite storage for research sessions, crawled pages, signals, and briefs.
  - 1-click exports to **CSV**, **JSON**, and **Executive Markdown Reports**.
  - Historical session browser and side-by-side comparison tool.

---

## 🏗️ Architecture

```
ai-web-signal-hunter/
│
├── app.py                     # Streamlit application entry point & router
├── requirements.txt           # Python dependency specifications
├── README.md                  # Comprehensive documentation
├── .env.example               # Template environment configuration
├── .gitignore                 # Git ignore file
├── run_sample_research.py     # End-to-end sample research pipeline runner
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Global settings, weights, and model definitions
│
├── crawler/
│   ├── __init__.py
│   ├── search.py              # Candidate discovery & query generator
│   ├── web_crawler.py         # Polite crawler engine with robots.txt parser
│   └── content_cleaner.py     # HTML cleaning, normalization & deduplication
│
├── ai_engine/
│   ├── __init__.py
│   ├── groq_client.py         # Groq API client with backoff
│   ├── gemini_client.py       # Google Gemini API client
│   ├── signal_extractor.py    # Extraction coordinator & evidence verifier
│   ├── prompts.py             # System & user prompts with untrusted tags
│   └── validators.py          # Pydantic schemas & substring checkers
│
├── analysis/
│   ├── __init__.py
│   ├── signal_grouping.py     # Recurring theme clusterer
│   ├── opportunity_scoring.py # Mathematical opportunity index formula
│   └── opportunity_briefs.py  # Brief synthesizer for Top 5 opportunities
│
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLite CRUD operations
│   └── models.py              # Database schema definitions
│
├── dashboard/
│   ├── __init__.py
│   ├── styles.py              # Modern SaaS CSS stylesheet
│   ├── overview.py            # Main executive dashboard
│   ├── research.py            # New research workflow launcher
│   ├── findings.py            # Filterable findings ledger & inspector
│   ├── history.py             # Historical archives & comparison tool
│   └── settings.py            # API key management & connection diagnostics
│
├── exports/
│   ├── __init__.py
│   └── export_service.py      # CSV, JSON & Markdown generators
│
└── tests/
    ├── __init__.py
    ├── test_cleaner.py        # Cleaner, normalizer & hash tests
    ├── test_scoring.py        # Mathematical formula unit tests
    └── test_validators.py     # Pydantic validation & evidence tests
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-web-signal-hunter
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 API Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your API keys (optional — the app also includes in-UI settings and a deterministic pattern engine for key-free evaluation):

```ini
# Choose default provider: 'groq' or 'gemini'
DEFAULT_AI_PROVIDER=groq

# Groq API Configuration (https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Google Gemini API Configuration (https://aistudio.google.com)
GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Crawler Settings
MAX_PAGES_DEFAULT=25
CRAWL_TIMEOUT_SECONDS=12
CRAWL_DELAY_SECONDS=0.8
```

You can also input or change your API keys directly from the **Settings & API Configuration** page inside the running application.

---

## ▶️ Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

The application will be accessible at `http://localhost:8501`.

To run the automated sample crawl pipeline directly from CLI:
```bash
python run_sample_research.py
```

---

## 🧪 Running Unit Tests

Run the full pytest suite:
```bash
pytest -v
```

This tests:
- HTML boilerplate & script removal
- URL canonicalization and tracking parameter stripping
- Content-based cryptographic deduplication
- Opportunity score weighting formula & mathematical boundary conditions
- Pydantic schema validation & max 30 words quote truncation
- Verbatim evidence verification against raw text

---

## 📐 Opportunity Scoring Methodology

The opportunity ranking algorithm transforms subjective web feedback into an objective composite index from **0 to 100**:

$$\text{Opportunity Score} = (0.30 \times \bar{R}) + (0.25 \times \bar{U}) + (0.20 \times \bar{C}) + (0.15 \times F) + (0.10 \times Rec)$$

| Factor | Weight | Description |
|---|---|---|
| **Average Relevance ($\bar{R}$)** | 30% | Direct alignment of discovered friction with the user's research topic. |
| **Average Urgency ($\bar{U}$)** | 25% | Severity of pain points, operational blockers, or imminent demand. |
| **Average Confidence ($\bar{C}$)** | 20% | Confidence in signal accuracy and verbatim quote authenticity. |
| **Frequency Score ($F$)** | 15% | Multi-source reinforcement ($min(100, (\text{sources} / 4) \times 100)$). |
| **Recency Score ($Rec$)** | 10% | Temporal freshness of crawled evidence. |

*Note: AI-generated scores reflect observed public web discourse and should be validated through direct customer interviews.*

---

## 🛡️ Responsible Crawling Practices

1. **Respects `robots.txt`**: Uses Python's `urllib.robotparser` to query each domain's `robots.txt` before fetching.
2. **Polite Request Delays**: Implements non-zero delays (0.8s) between requests.
3. **Identification**: Announces itself via descriptive `User-Agent`.
4. **Public Data Only**: Crawls only publicly indexed web pages without bypassing logins, paywalls, or CAPTCHAs.
5. **No Private/Sensitive Data**: Filters personal accounts, private threads, and non-content markup.

---

## ⚠️ Known Limitations

- **Search Engine Throttling**: Live public search endpoints can occasionally rate-limit automated queries. The engine incorporates retry backoffs and discovery fallback seeds.
- **Dynamic JavaScript SPAs**: Sites requiring client-side JavaScript hydration may render partial text without headless browser execution.
- **LLM Rate Limits**: Free-tier Groq/Gemini keys are subject to TPM/RPM caps; exponential backoff and heuristic fallbacks ensure zero app crashes.

---

## 📄 License
MIT License. Developed for the AI Web Signal Hunter Internship Assignment.
