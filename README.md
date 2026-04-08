# Sentinel v2 — AI-Powered AML Investigation Agent

> **ET Gen AI Hackathon 2026** | Problem Statement 5: Domain-Specialized AI Agents with Compliance Guardrails

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fprithvi-kaizen%2FAnti-Money-Laundering)

##  Hackathon Submission Requirements

This repository contains all required assets for Problem Statement 5:
- **✔️ Source Code & Setup Instructions**: Full Next.js / FastAPI codebase included below.
- **✔️ 3-Minute Pitch Video**: See the suggested script and recording guide in [PITCH_SCRIPT.md](./PITCH_SCRIPT.md).
- **✔️ Architecture Document**: System diagrams, agent roles, and error-handling logic are detailed in [ARCHITECTURE.md](./ARCHITECTURE.md).
- **✔️ Impact Model**: Quantified business impact (OpEx math, throughput gains) is documented in [IMPACT_MODEL.md](./IMPACT_MODEL.md).

---

##  The Problem & Solution
**The Problem**: Manual AML investigation takes 4+ hours per alert, costs $25,000–$50,000 per analyst per year, and has a 38% false positive rate that creates severe investigator fatigue.

**The Solution**: Sentinel combines rule-based compliance guardrails (FATF, FinCEN, OFAC) with Groq-powered AI reasoning (Llama 3.3) to investigate alerts in under 15 minutes with auditable, regulation-cited decisions.

##  Key Innovation: The Guardrail Layer
Unlike pure generative AI systems, Sentinel enforces hard regulatory boundaries that act as an interception middleware. 
If the AI assesses an alert as low-risk but the compliance engine detects FATF jurisdiction exposure, the system overrides the AI and mandates escalation. Every decision is logged and persisted via a tamper-evident SHA-256 audit trail architecture.

##  Tech Stack
- **Frontend**: Next.js 14, Tailwind CSS, D3.js (Force-directed entity graphs).
- **Backend / Agent**: FastAPI, SQLite, NetworkX, Groq SDK (`llama-3.3-70b-versatile`).
- **Data**: Synthetic financial crime dataset designed to test OFAC and FATF constraints.

---

##  Local Setup Instructions

### 1. Backend (FastAPI Core)
```bash
# Set your Groq API key (get it free at console.groq.com)
export GROQ_API_KEY="your_actual_key_here"

# Initialize python environment
cd backend
python -m venv venv
source venv/bin/activate

# Install dependencies and generate synthetic data
pip install -r requirements.txt
python scripts/generate_dataset.py

# Start the Python server
uvicorn main:app --reload --port 8000
```
*(Note: If `GROQ_API_KEY` is not set, a mock fallback engine is used automatically for demo resilience.)*

### 2. Frontend (Next.js Dashboard)
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```

Navigate to [http://localhost:3000](http://localhost:3000) to access the Sentinel v2 Financial Operations Terminal.
