# Episteme AI

> **The AI agent that knows what it doesn't know.**

[![License: Custom Evaluation](https://shields.io)](#-licensing--usage-restrictions-read-before-proceeding) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![React](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb.svg)](https://react.dev/) [![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20Compatible-green.svg)](https://build.nvidia.com/)

## Licensing & Usage Restrictions (Read Before Proceeding)

**Episteme AI** is a **Source-Available** project provided exclusively for **local testing, peer evaluation, and verification purposes**. 

* **Allowed:** You are encouraged to clone this repository, configure your NVIDIA NIM API keys, and run the 790-sample calibration benchmark locally to verify our empirical results.
* **Prohibited:** You **cannot** use this source code, framework architecture, data plots, or logic for your own academic papers, corporate research projects, independent studies, or public benchmarking publications. 

If you wish to utilize Episteme AI or its decoupled dual-pass inference architecture for research purposes, you must request explicit written permission. Please see the [Citation & Research Inquiries](#-citation--research-inquiries) section below to request a formal research license.

---

## Overview
Modern Large Language Models (LLMs) suffer from a critical design flaw: **confident hallucination**. They deliver factual inaccuracies with the exact same linguistic certainty as verified truth. 

**Episteme AI** solves this by introducing a metacognitive layer. Instead of relying on post-hoc guardrails, Episteme AI forces the model to continuously evaluate its own internal certainty state, embedding active humility directly into the user experience.

---

## Core Features
* **Active Humility & Calibrated Syntax:** Formats outputs using calibrated language based on internal probability estimates, openly admitting when it lacks confidence.
* **Explicit Confidence Metrics:** Maps raw token probabilities directly to real-time, user-facing UI meters.
* **Concurrent Edge-Case Auditing:** Asynchronously hunts for scenarios where a generated answer might fail, without blocking the primary text stream.
* **Uncertainty Logging:** Automatically flags and logs low-confidence interactions to isolate core model weaknesses, directly informing future fine-tuning pipelines.

---

## System Architecture
Episteme AI leverages a decoupled architecture engineered for real-time streaming inference paired with asynchronous secondary evaluation.

* **Frontend:** React + Vite for a highly responsive, low-latency UI.
* **Backend API:** A lightweight Flask API Engine handling dual-pass orchestration and routing.
* **Compute Layer:** NVIDIA Inference Microservice (NIM) pool to extract and process raw token probabilities with minimal latency.

### Data Pipeline Flow
1. **Immediate Stream:** The backend pushes a primary JSON payload (containing calibrated text and initial metadata) to the frontend instantly.
2. **Asynchronous Audit:** Concurrently, background workers compute deep edge-case risk assessments while the user is actively reading the initial stream.

---

## Quick Start

### Prerequisites
* Python 3.10+
* Node.js 18+
* An OpenAI or NVIDIA NIM compatible API key (that supports `logprobs`)

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/Prahalad-ship-it/knowable-
cd knowable-

# Set up the Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up the Frontend
cd ../frontend
npm install
npm run dev
```

---

## 📝 Citation & Research Inquiries

If you are an academic or corporate researcher interested in building upon the Episteme AI architecture, or if you wish to cite our calibration data (`openai/gpt-oss-20b` baseline crisis metrics) in your work, please use the following temporary citation layout. 

The formal technical paper is currently being finalized for publication.

```bibtex
@misc{epistemeai2026,
  author = {Prahalad},
  title = {Episteme AI: A Decoupled Dual-Pass Inference Architecture for Mitigating Confident Hallucinations},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub Repository},
  howpublished \(= {\url{https://github.com/Prahalad-ship-it/knowable-}} \)}
```

### 📧 Requesting a Research License
To request permission to use this architecture for comparative benchmarks or extended research studies, please open a GitHub Issue with the tag `[Research Inquiry]` or contact the author directly via the email listed on your GitHub profile.
