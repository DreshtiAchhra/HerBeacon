HerBeacon

Safer Conversations, Brighter Tomorrows.

HerBeacon is a behavioural safety intelligence platform that helps people recognize risky patterns in online conversations before those patterns escalate into financial or emotional harm.

HerBeacon does not attempt to identify, label, or judge people. Instead, it analyzes how a conversation changes over time: trust-building, emotional dependency, secrecy, isolation, urgency, financial pressure, requests for sensitive information, manipulation, and coercion.

> We don't detect suspicious people.
> We detect suspicious behavioural patterns.

The problem

Online relationships can gradually shift from ordinary conversation to manipulation. A conversation may progress through:

```text
Trust → Emotional dependency → Secrecy → Isolation
→ Financial pressure → Urgency / Coercion
```

By the time a financial request becomes obvious, several earlier warning signals may already have appeared. HerBeacon therefore focuses on understanding the behavioural progression of the conversation, not just flagging one suspicious message.

What HerBeacon does

HerBeacon transforms a conversation into an explainable behavioural safety assessment:

```text
Conversation
    ↓
Behavioural analysis
    ↓
Risk assessment
    ↓
Escalation analysis
    ↓
Explainability
    ↓
Safety guidance
```

Users can paste a conversation or upload a plain-text conversation file. The dashboard then presents:

- Risk level and risk score
- Detected behavioural patterns
- Risk-factor contributions
- Risk progression over time
- High-risk evidence from the conversation
- Escalation stages and milestones
- Situation-specific safety recommendations
- A structured executive PDF report

Core intelligence

The analysis engine identifies behavioural categories such as:

- Trust building
- Emotional dependency and love bombing
- Communication migration
- Secrecy
- Isolation
- Financial pressure
- Urgency
- Sensitive-information requests
- Emotional manipulation
- Coercion and threats

These categories describe observed conversation behaviour. They are not proof of a person's identity, intent, or criminal behaviour.

Risk and escalation intelligence

The existing Python engine returns a transparent behavioural risk assessment, supporting risk levels from LOW through CRITICAL, together with the factors and evidence that contributed to it.

HerBeacon also maps conversation progression through six stages:

```text
Baseline
    ↓
Rapport
    ↓
Migration
    ↓
Isolation
    ↓
Manipulation
    ↓
Coercion
```

The interface distinguishes observed stages, partial progression, late-stage escalation, and conversations where no meaningful escalation is detected. This helps users understand where the conversation is now and how it reached that point.

Explainable AI

HerBeacon is designed around evidence-first analysis. Instead of only showing a score, the platform connects:

```text
Behavioural signal
    ↓
Evidence from the conversation
    ↓
Why the signal matters
    ↓
Contribution to the assessment
```

This makes results easier to understand, review, and discuss.

Dashboard views

The React dashboard provides dedicated intelligence views:

- Overview — High-level risk summary, behavioural signals, key evidence, and interpretation.
- Risk & Escalation Matrix — Risk factors, factor contributions, escalation stage, and progression.
- Behavioural Pattern Hub — Detected patterns with severity, confidence, explanations, and evidence.
- Timeline Intelligence — Chronological behavioural signals and risk progression.
- Actionable Safety Guide — Practical safety recommendations based on the observed situation.
- Executive Report & Export — A structured PDF containing the summary, signals, evidence, escalation journey, and safety actions.

Technology stack

AI and analysis

- Python
- Existing HerBeacon behavioural analysis engine

Backend

- FastAPI
- Uvicorn
- Pydantic

Frontend

- React
- Vite
- Recharts
- Tailwind CSS
- Lucide React

Report generation

- html2canvas
- jsPDF

Project structure

```text
HerBeacon/
|-- ai/                         Existing behavioural analysis engine
|-- backend/                    FastAPI bridge
|-- frontend/                   React + Vite interface
|-- tests/                      Project tests
|-- demoData/                   Sample conversation for demonstrations
|-- data/                       Optional local analysis data
|-- requirements.txt            Python engine dependencies
`-- README.md
```

Demo conversation

A sample conversation is included at:

```text
demoData/sample_conversation.txt
```

This allows judges and developers to test the application without downloading the complete dataset. The application can also analyze a user-provided plain-text conversation.

The full development dataset is not required to run the demo application. The project was developed and evaluated using the LoveFraud02 conversation corpus:

> LoveFraud02 — Faber, 2024
> Mendeley Data
> DOI: 10.17632/kmhvb4x5d8.1
> License: CC BY 4.0

The complete corpus is not bundled with this repository.

Running HerBeacon

1. Start the backend

Create and activate a Python virtual environment if needed, then install the dependencies from the project root:

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The backend is available at `http://127.0.0.1:8000`.

Health check:

```text
http://127.0.0.1:8000/api/health
```

2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at `http://127.0.0.1:5173`.

Testing the demo

1. Open the frontend in a browser.
2. Navigate to Conversation Intake.
3. Upload `demoData/sample_conversation.txt` or paste a conversation manually.
4. Start the analysis.
5. Review the risk assessment, behavioural patterns, risk factors, escalation journey, evidence, timeline, safety recommendations, and executive report.

The analysis result is preserved while navigating through the dashboard so each view uses the same engine output.

Safety and privacy

HerBeacon is a decision-support tool. It does not prove:

- Identity
- Criminal behaviour
- Malicious intent
- Whether a person is a scammer

A detected pattern represents an observed behavioural signal within the analyzed conversation. Results should be interpreted carefully alongside personal judgement and appropriate support.

Do not upload private conversations to an environment unless you have permission and understand how that environment stores and processes the data.

Design philosophy

01 — Detect the Pattern

Identify meaningful changes in conversation behaviour.

02 — Understand the Risk

Explain what was observed and how behavioural signals contribute to the assessment.

03 — Act Before Harm

Turn the analysis into practical, situation-specific safety guidance.

Development principle

The AI analysis engine remains the single source of behavioural intelligence. The application must never introduce:

- Fake risk scores
- Synthetic evidence
- Hard-coded analysis results
- A second risk calculation
- Frontend-generated behavioural classifications

All dashboard visualizations, reports, and recommendations must be derived from the actual output of the existing HerBeacon analysis engine.

---

HerBeacon

Safer Conversations, Brighter Tomorrows.

Detect the Pattern. Understand the Risk. Act Before Harm.
