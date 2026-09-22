# HerBeacon

HerBeacon is a behavioural safety platform that helps people understand risky patterns in online conversations.

HerBeacon does not label people or decide whether someone is a scammer. It looks at changes in conversation behaviour, such as pressure, secrecy, isolation, urgency, requests for money, and requests for sensitive information.

The project was created around the problem of catfishing that can lead to debt and financial harm.

## Project message

Safer Conversations, Brighter Tomorrows.

HerBeacon follows three simple ideas.

Detect the pattern.

Understand the risk.

Act before harm.

## What the application does

The application accepts a pasted conversation or a plain text conversation file.

The existing Python analysis engine reviews the conversation and returns:

Risk level and risk score

Behavioural patterns

Risk factor contribution

Risk progression over time

High risk evidence

Conversation milestones

Safety recommendations

The web application presents this information through a clear dashboard with charts, report sections, and practical safety guidance.

## Technology used

The analysis engine is written in Python.

The API is built with FastAPI.

The user interface is built with React and Vite.

Charts are created with Recharts.

PDF reports are created in the browser with html2canvas and jsPDF.

The React application communicates with the Python engine through the FastAPI bridge. The React application does not import or duplicate the Python analysis logic.

## Project structure

The ai folder contains the existing HerBeacon analysis engine.

The backend folder contains the FastAPI bridge.

The frontend folder contains the React and Vite user interface.

The tests folder contains project tests.

The data folder contains local analysis data when it is available.

## Running the project

### Start the backend

Create and activate a Python virtual environment if needed.

Install the Python dependencies.

```text
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

Start the FastAPI server from the project root.

```text
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

The health check is available at:

```text
http://127.0.0.1:8000/api/health
```

### Start the frontend

Open a second terminal and move into the frontend folder.

```text
cd frontend
npm install
npm run dev
```

The web application will be available at:

```text
http://127.0.0.1:5173
```

## Using the dashboard

Open the frontend in a browser.

Choose Conversation Intake from the navigation.

Paste a conversation or upload a plain text file.

Start the analysis.

The dashboard will open after the analysis is complete.

The result is kept during navigation so the charts and report use the same analysis.

The Executive Report section provides a visual PDF report with separate pages for the summary, charts, flagged conversation explanation, key evidence, escalation journey, and safety actions.

## Safety and privacy

HerBeacon is a decision support tool. It does not prove identity, intent, or criminal behaviour.

The results should be reviewed with care and used alongside personal judgement and support from a trusted person or qualified professional.

Do not upload private conversations to an environment unless you have permission and understand how that environment stores and processes data.

## Important development rule

The frontend and API are presentation and integration layers. The analysis logic remains in the ai folder.

New interface features should use the output returned by the existing analysis engine. They should not create fake scores, synthetic evidence, or a second risk calculation.
