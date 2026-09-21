# Smart Competency Diagnostic & Candidate Profile Score Calculator

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.2-orange.svg)](https://xgboost.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The Smart Competency Diagnostic is a state-of-the-art recruitment and candidate evaluation platform powered by an **XGBoost** ranking model, AI multi-provider routing (OpenAI, Gemini, Anthropic), and a high-performance **FastAPI** backend with a modern **React** frontend. This application automates candidate evaluation, offering explainable AI scoring via SHAP and comprehensive fairness auditing.

---

## Demo Screenshots

*(Insert Demo Screenshots Here)*

*Figure 1: Recruiter Dashboard*
*Figure 2: Candidate Evaluation & SHAP Analysis*
*Figure 3: AI Interview Chat*

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Provider AI Routing** | Automatically routes requests to the most efficient AI provider (Gemini, Claude, OpenAI) based on latency and cost. |
| **XGBoost Ranking Model** | Predicts candidate success probability and ranks candidate profiles efficiently. |
| **SHAP Explainability** | Provides feature-level transparency into the ML model's decisions, showing exactly *why* a candidate received a particular score. |
| **Fairness Auditing** | Ensures compliance and ethical AI usage with Disparate Impact Ratio (DIR) and Equal Opportunity (EO) audits. |
| **OCR & Resume Parsing** | Robust PDF/DOCX parsing capabilities leveraging Tesseract OCR and PyMuPDF. |
| **Role-Based Access Control** | Secure JWT authentication with strict isolation between `recruiter` and `candidate` roles. |
| **Skill Graph Evaluation** | Maps candidate skills to an ontology to identify missing but related competencies. |
| **Synthetic Data Generation** | Includes a robust pipeline to generate diverse candidate profiles for model training. |
| **Interactive AI Interviews** | Integrated chatbot to conduct preliminary competency assessments. |
| **Comprehensive Dashboard** | Real-time candidate analytics, ranking tables, and system health monitoring. |

---

## Architecture Diagram

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   React Frontend  +------>+    FastAPI Backend    +------>+ AI Provider Router|
|                   |       |                       |       |                   |
+-------------------+       +-----------+-----------+       +-------------------+
                                        |                             |
                                        v                             |
                            +-----------+-----------+                 v
                            |                       |      (OpenAI / Gemini / Claude)
                            |     XGBoost Model     |
                            |    + SHAP Explainer   |
                            |                       |
                            +-----------------------+
```

---

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
# Install Tesseract OCR
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
cp ../.env.example ../.env
# Edit .env with your API keys
cd ../ml_training
python generate_synthetic_data.py
python train_xgboost.py
cd ../backend
uvicorn main:app --reload --port 8000
```

> The backend and evaluation scripts require the spaCy English model. Install it
> once with `python -m spacy download en_core_web_sm`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker

You can easily run the full stack using Docker Compose:

```bash
docker-compose up --build
```

---

## API Endpoints

| Endpoint | Method | Role Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | None | Check system health |
| `/auth/register` | POST | None | Register a new user |
| `/auth/login` | POST | None | Authenticate user & get JWT |
| `/upload` | POST | Candidate | Upload resume/CV for parsing |
| `/candidates` | GET | Recruiter | List ranked candidates |
| `/candidates/{id}` | GET | Recruiter | Get candidate details & SHAP |
| `/fairness/audit` | GET | Admin | Run fairness evaluation |

---

## AI Provider Configuration

This project supports routing between multiple LLM providers.

### OpenRouter Setup
1. Go to [OpenRouter](https://openrouter.ai/) and create an account.
2. Generate an API key.
3. Add `OPENROUTER_API_KEY=your_key` to `.env`.

### Google AI Studio (Gemini) Setup
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Generate an API key.
3. Add `GEMINI_API_KEY=your_key` to `.env`.

### Provider Routing Logic
The backend dynamically selects the LLM provider based on:
1. Provider availability (circuit breaker pattern).
2. Latency requirements.
3. Token limits and associated cost logic.

---

## Resume Upload Supported Formats

- PDF (`.pdf`) - Parsed via PyMuPDF. Scanned PDFs are processed via Tesseract OCR.
- Word (`.docx`) - Parsed via python-docx.
- Text (`.txt`)

*Note: Ensure Tesseract OCR is installed on the host machine for image-based PDF parsing to function correctly.*

---

## ML Model

### XGBRanker
The core of our evaluation system uses `XGBRanker` to learn the relative importance of candidate features. This list-wise ranking approach is superior to binary classification as it naturally handles candidate ordering.

### Features

The baseline model uses these five structured features:
- `exp_years`
- `skill_match_ratio`
- `num_projects`
- `num_certs`
- `gpa`

Training and evaluation currently use synthetic data: 500 profiles generated
across 8 domains.

### Proxy Label Strategy
Due to the lack of historical hiring data at startup, proxy labels (scores 1-5) are programmatically assigned based on heuristic rules simulating senior technical recruiters.

### Training Data
The model is trained on **500 synthetic profiles** generated across 8 different
domains (e.g., Data Science, Backend Dev, DevOps).

## Real-label v2 evaluation

The v2 pair model is trained only from the Hugging Face
`cnamuangtoun/resume-job-description-fit` labels. Synthetic rows are not used
in validation or test. Run `python ml_training/train_real.py` to reproduce the
split, cached MiniLM features, validation-only tuning, and untouched test
report. The dataset does not declare a license, and its labels are noisy proxy
judgments rather than hiring outcomes.

The final test metrics and ablation ladder are recorded in
`backend/models/trained/v2/report.json` after the evaluation run. The test
split is grouped by both resume and job identifiers; only qualifying job groups
are used for NDCG. Results must be compared with TF-IDF, embedding-only, v1,
and random baselines rather than interpreted as production hiring accuracy.

---

## SHAP Explainability

Black-box models aren't acceptable in hiring. We use **SHAP (SHapley Additive exPlanations)** to break down every score. For any candidate, the backend returns the baseline score plus the marginal contribution of every feature, enabling recruiters to easily interpret the ranking.

---

## Fairness Audit

To prevent algorithmic bias, we implement fairness checks:
- **Disparate Impact Ratio (DIR):** Checks if the selection rate for protected groups is less than 80% of the selection rate for the privileged group.
- **Demographic Parity (DP):** Ensures candidates are shortlisted at the same rate, regardless of demographic attributes.
- **Equal Opportunity (EO):** Checks if the true positive rate is equivalent across groups.

---

## Authentication

We utilize JWT (JSON Web Tokens) for stateless authentication.
- **Candidate:** Can only upload resumes and view their own score.
- **Recruiter:** Can view all profiles, ranking dashboards, and fairness metrics.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | Secret key for JWT | `changeme` |
| `DB_URL` | Database connection string | `sqlite:///./app.db` |
| `OPENROUTER_API_KEY` | OpenRouter API Key | |
| `GEMINI_API_KEY` | Google Gemini API Key | |

---

## Project Structure

```text
ml/
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── models/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── nginx.conf
├── ml_training/
│   ├── generate_synthetic_data.py
│   └── train_xgboost.py
├── tests/
│   ├── test_parser.py
│   └── test_scorer.py
├── Dockerfile.backend
└── docker-compose.yml
```

---

## Acknowledgements

- [XGBoost](https://xgboost.readthedocs.io/)
- [SHAP](https://shap.readthedocs.io/en/latest/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## License

MIT License

Copyright (c) 2024 Smart Competency Diagnostic

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
