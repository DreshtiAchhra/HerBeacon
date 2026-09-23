import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowRight, BarChart3, BookOpen, CheckCircle2, ChevronRight, CircleAlert,
  FileText, HeartHandshake, LayoutDashboard, Lightbulb, Menu, MessageSquare,
  Network, ShieldCheck, Sparkles, Upload, X,
} from "lucide-react";
import {
  Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import { analyzeFile, analyzeText } from "./services/api";

const nav = [
  ["overview", "Overview", Sparkles],
  ["intake", "Conversation Intake", MessageSquare],
  ["matrix", "Risk & Escalation Matrix", BarChart3],
  ["patterns", "Behavioural Pattern Hub", Network],
  ["timeline", "Timeline Intelligence", BookOpen],
  ["safety", "Actionable Safety Guide", ShieldCheck],
  ["report", "Executive Report & Export", FileText],
];
const stages = ["Baseline", "Rapport", "Migration", "Isolation", "Manipulation", "Coercion"];

function get(obj, ...keys) {
  return keys.reduce((value, key) => value?.[key], obj);
}

function RiskBadge({ level = "LOW" }) {
  const safe = ["LOW", "MODERATE", "HIGH", "CRITICAL"].includes(String(level).toUpperCase())
    ? String(level).toUpperCase() : "LOW";
  return <span className={`badge badge-${safe.toLowerCase()}`}>{safe}</span>;
}

function Stat({ label, value, note }) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong>{note && <small>{note}</small>}</div>;
}

function Card({ children, className = "" }) {
  return <section className={`card ${className}`}>{children}</section>;
}

function BrandMark() {
  return <div className="brand-mark" aria-hidden="true"><svg viewBox="0 0 48 48" role="img"><defs><linearGradient id="brand-gradient" x1="8" y1="43" x2="39" y2="4" gradientUnits="userSpaceOnUse"><stop offset="0" stopColor="#D95B68" /><stop offset=".5" stopColor="#8A315A" /><stop offset="1" stopColor="#48245F" /></linearGradient><linearGradient id="brand-hair-gradient" x1="12" y1="40" x2="28" y2="10" gradientUnits="userSpaceOnUse"><stop offset="0" stopColor="#F16A6C" /><stop offset="1" stopColor="#8D315A" /></linearGradient></defs><path fill="url(#brand-gradient)" d="M24 3.5 40 9v12.2c0 10.7-6.6 19.2-16 23.3-9.4-4.1-16-12.6-16-23.3V9L24 3.5Z" /><path className="brand-hair" d="M27.4 7.8c-1.1 6.5-3.8 11.8-8 15.9-3.6 3.5-5.4 7.4-5.4 11.6 0 3.7 1.3 6.8 4 9.2l7.4 1.8c-4.1-2.7-6.2-6-6.2-10 0-3.8 1.9-7 4.8-10.5 4.6-5.5 6.2-11.4 5.9-18Z" fill="url(#brand-hair-gradient)" /><path className="brand-profile" d="M27.7 8.4c2.1 2.8 2.9 6 2.5 9.5-.1 1.1.3 2 1 2.4l.5.4c.3.2.3.6 0 .8l-.5.4.6.5c.2.2.2.5-.1.7l-1 .6c-.4 1.3-1.3 2.2-2.7 2.7-1.4.5-2.1 1.6-2.1 3.4 0 3.2 1.8 6 5.3 8.5l-4.7 2.9c-4.6-2.5-6.9-5.9-6.9-10.2 0-4.1 1.9-7.4 4.6-10.9 3.1-4 4.2-8.6 3.5-13.9Z" /></svg></div>;
}

function EmptyState({ title = "Run an analysis to unlock this view." }) {
  return <Card className="empty-state"><CircleAlert size={23} /><strong>{title}</strong><p>Your result will remain available as you move through the workspace.</p></Card>;
}

function SignalChart({ result }) {
  const counts = get(result, "behavioral_patterns", "pattern_counts") || {};
  const data = Object.entries(counts).map(([key, count]) => ({
    name: key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
    count: Number(count) || 0,
  })).filter((item) => item.count > 0);
  if (!data.length) return <p className="muted chart-empty">Signal distribution is not available for this analysis.</p>;
  return <ResponsiveContainer width="100%" height={250}><BarChart data={data} layout="vertical" margin={{ left: 18, right: 20, top: 8, bottom: 8 }}><CartesianGrid stroke="#eee8e3" horizontal={false} /><XAxis type="number" allowDecimals={false} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="name" width={150} axisLine={false} tickLine={false} tick={{ fill: "#746b68", fontSize: 11 }} /><Tooltip cursor={{ fill: "#fbf3f5" }} contentStyle={{ border: "1px solid #E5DED5", borderRadius: 8, fontSize: 12 }} /><Bar dataKey="count" name="Detected cues" fill="#A64D6B" radius={[0, 4, 4, 0]} /></BarChart></ResponsiveContainer>;
}

function ContributionChart({ result }) {
  const drivers = get(result, "explainability", "top_risk_drivers") || [];
  const data = drivers.map((driver) => ({
    name: driver.feature_name || "Risk factor",
    points: Number(driver.contribution_points ?? driver.shap_value),
  })).filter((item) => Number.isFinite(item.points));
  if (!data.length) return <p className="muted chart-empty">Contribution data is not available for this analysis.</p>;
  return <ResponsiveContainer width="100%" height={250}><BarChart data={data} layout="vertical" margin={{ left: 12, right: 20, top: 8, bottom: 8 }}><CartesianGrid stroke="#eee8e3" horizontal={false} /><XAxis type="number" axisLine={false} tickLine={false} /><YAxis type="category" dataKey="name" width={165} axisLine={false} tickLine={false} tick={{ fill: "#746b68", fontSize: 11 }} /><Tooltip cursor={{ fill: "#fbf3f5" }} contentStyle={{ border: "1px solid #E5DED5", borderRadius: 8, fontSize: 12 }} /><Bar dataKey="points" name="Contribution points" fill="#D6A84F" radius={[0, 4, 4, 0]} /></BarChart></ResponsiveContainer>;
}

function RiskProgression({ result, height = 280 }) {
  const points = (get(result, "risk_timeline", "checkpoints") || []).map((point) => ({
    turn: point.turn,
    score: Number(point.risk_score),
    level: point.risk_level,
    stage: point.stage_name,
  })).filter((point) => Number.isFinite(point.score));
  if (points.length < 1) return <p className="muted chart-empty">Risk progression data is not available for this analysis.</p>;
  return <ResponsiveContainer width="100%" height={height}><LineChart data={points} margin={{ left: 0, right: 18, top: 10, bottom: 5 }}><CartesianGrid stroke="#eee8e3" vertical={false} /><XAxis dataKey="turn" tickLine={false} axisLine={false} tick={{ fill: "#918682", fontSize: 11 }} /><YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: "#918682", fontSize: 11 }} /><Tooltip contentStyle={{ border: "1px solid #E5DED5", borderRadius: 8, fontSize: 12 }} formatter={(value) => [`${value}/100`, "Risk score"]} labelFormatter={(turn) => `Turn ${turn}`} /><Line type="monotone" dataKey="score" stroke="#6B1E3F" strokeWidth={3} dot={{ r: 4, fill: "#A64D6B", stroke: "#fff", strokeWidth: 2 }} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer>;
}

function Explainability({ result }) {
  const drivers = get(result, "explainability", "top_risk_drivers") || [];
  const safety = get(result, "safety_recommendations") || {};
  const flaggedPatterns = {};
  (result?.messages || []).forEach((message) => (message.patterns || []).forEach((pattern) => {
    const severity = String(pattern.severity || "").toUpperCase();
    if (["HIGH", "CRITICAL", "MODERATE", "MEDIUM", "LOW"].includes(severity)) {
      const key = pattern.pattern_key || pattern.pattern_name;
      if (!flaggedPatterns[key]) flaggedPatterns[key] = { ...pattern, cueCount: 0 };
      flaggedPatterns[key].cueCount += 1;
    }
  }));
  const severityLimit = { MODERATE: 3, MEDIUM: 3, LOW: 3 };
  const severityCounts = {};
  const patternItems = Object.values(flaggedPatterns).filter((pattern) => {
    const severity = String(pattern.severity || "").toUpperCase();
    if (["HIGH", "CRITICAL"].includes(severity)) return true;
    const normalized = severity === "MEDIUM" ? "MODERATE" : severity;
    severityCounts[normalized] = (severityCounts[normalized] || 0) + 1;
    return severityCounts[normalized] <= severityLimit[normalized];
  });
  const items = patternItems.length ? patternItems : drivers.filter((driver) => {
    const severity = String(driver.severity || driver.risk_level || driver.level || "").toUpperCase();
    return ["HIGH", "CRITICAL", "MODERATE", "MEDIUM", "LOW"].includes(severity);
  });
  if (!items.length) return <Card className="empty-state"><Lightbulb size={22} /><strong>Explainability data is not available for this analysis.</strong></Card>;
  return <><div className="explain-grid">{items.map((driver, index) => { const severity = String(driver.severity || "HIGH").toUpperCase(); const badgeLevel = severity === "MEDIUM" ? "moderate" : severity.toLowerCase(); return <Card className="explain-card" key={`${driver.pattern_key || driver.feature_name || driver.factor || "driver"}-${index}`}><div className="explain-heading"><span className="pattern-icon"><Lightbulb size={16} /></span><span className={`badge badge-${badgeLevel}`}>{severity}</span></div><h3>{driver.pattern_name || driver.feature_name || driver.factor || "Risk factor"}</h3><span className="cue-count">{driver.cueCount ? `${driver.cueCount} cue(s) observed` : `Contribution: ${driver.contribution_points ?? driver.shap_value ?? "Not provided"}`}</span><p>{driver.explanation || driver.detail || "Behavioural pattern observed in this conversation."}</p></Card>; })}</div><Card className="action-callout explain-suggestion"><div><span className="eyebrow">Suggested next step</span><p>{safety.primary_action || "Pause before responding and review the conversation with someone you trust."}</p></div></Card></>;
}

function EvidenceSection({ result, compact = false }) {
  const severityCounts = {};
  const messages = (result?.messages || []).map((message) => ({
    ...message,
    patterns: (message.patterns || []).filter((pattern) => {
      const severity = String(pattern.severity || "").toUpperCase();
      if (["HIGH", "CRITICAL"].includes(severity)) return true;
      const normalized = severity === "MEDIUM" ? "MODERATE" : severity;
      if (!["MODERATE", "LOW"].includes(normalized)) return false;
      severityCounts[normalized] = (severityCounts[normalized] || 0) + 1;
      return severityCounts[normalized] <= 3;
    }),
  })).filter((message) => message.patterns.length);
  if (!messages.length) return <Card className="empty-state"><Network size={22} /><strong>No key evidence was returned for this analysis.</strong><p>The engine did not provide flagged message-level evidence.</p></Card>;
  return <div className={`evidence-grid ${compact ? "evidence-compact" : ""}`}>{messages.map((message) => <Card className="evidence-card" key={message.message_index}><div className="evidence-meta"><span>Turn {message.message_index ?? "—"}{message.speaker ? ` · ${message.speaker}` : ""}</span><RiskBadge level={(message.patterns || []).some((pattern) => ["HIGH", "CRITICAL"].includes(pattern.severity)) ? "HIGH" : "MODERATE"} /></div><div className="evidence-patterns">{(message.patterns || []).map((pattern) => <span key={`${message.message_index}-${pattern.pattern_key}`} className="evidence-tag">{pattern.pattern_name || pattern.pattern_key}</span>)}</div><blockquote>{(message.patterns || []).flatMap((pattern) => pattern.evidence || []).slice(0, 2).map((evidence) => `“${evidence}”`).join(" · ") || message.message || "Evidence text unavailable."}</blockquote><p>{(message.patterns || [])[0]?.explanation || "Behavioural signal observed in this turn."}</p></Card>)}</div>;
}

function Overview({ onStart, onSafety, result }) {
  return <main>
    <div className="hero">
      <div className="eyebrow">Safer Conversations, Brighter Tomorrows.</div>
      <h1>Detect the pattern.<br /><em>Understand the risk.</em><br />Act before harm.</h1>
      <p>HerBeacon helps make concerning conversational shifts visible — without labeling people. Explore the evidence, understand the pathway, and choose a safer next step.</p>
      <button className="button button-primary" onClick={onStart}>Analyze a conversation <ArrowRight size={17} /></button>
      <div className="hero-note"><ShieldCheck size={16} /> Decision support only · Not a determination of identity or intent</div>
    </div>
    {!result ? <><div className="section-heading"><div><span className="eyebrow">The HerBeacon lens</span><h2>A more human kind of intelligence</h2></div></div><div className="feature-grid">
      {[
        ["Evidence over assumptions", "See the exact turn-level cues behind every signal, with context preserved.", Network],
        ["Explainable by design", "Follow the observable pathway from connection to pressure through a transparent engine.", Lightbulb],
        ["Safety-first next steps", "Receive calm, practical guidance focused on pausing, verifying, and staying supported.", HeartHandshake],
      ].map(([title, text, Icon]) => <Card key={title} className="feature-card"><div className="icon-bubble"><Icon size={20} /></div><h3>{title}</h3><p>{text}</p></Card>)}
    </div></> : <Dashboard result={result} onStart={onStart} onSafety={onSafety} />}
  </main>;
}

function Dashboard({ result, onStart, onSafety }) {
  const risk = get(result, "risk_assessment") || {};
  const escalation = get(result, "escalation_analysis") || {};
  const signals = get(result, "behavioral_patterns", "total_cues_detected");
  return <div className="dashboard-content"><div className="stats-grid"><Stat label="Risk score" value={`${risk.risk_score ?? "—"}/100`} note={<RiskBadge level={risk.risk_level} />} /><Stat label="Risk level" value={risk.risk_level || "—"} /><Stat label="Escalation stage" value={`Stage ${escalation.max_stage ?? "—"}`} note={escalation.max_stage_name || "Baseline"} /><Stat label="Behavioural signals" value={signals ?? "—"} note="Detected cues" /></div><div className="dashboard-grid"><Card><div className="card-heading"><BarChart3 size={20} /><div><h2>Behavioural Signal Distribution</h2><p className="chart-subtitle">Detected behavioural patterns in the conversation.</p></div></div><SignalChart result={result} /></Card><Card><div className="card-heading"><Lightbulb size={20} /><div><h2>Risk Factor Contribution</h2><p className="chart-subtitle">Factors returned by the explainability engine.</p></div></div><ContributionChart result={result} /></Card></div><div className="section-heading explain-title"><div><span className="eyebrow">Explainable assessment</span><h2>Why was this conversation flagged?</h2><p className="muted">{get(result, "explainability", "narrative") || risk.summary || "The engine returned no additional narrative for this analysis."}</p></div></div><Explainability result={result} /><Card className="chart-card"><div className="card-heading"><Network size={20} /><div><h2>Risk Progression</h2><p className="chart-subtitle">How behavioural risk signals developed throughout this conversation.</p></div></div><RiskProgression result={result} height={300} /></Card><Escalation result={result} /><Card className="action-callout"><div><span className="eyebrow">What you can do now</span><h2>{get(result, "safety_recommendations", "primary_action") || "Review the conversation with someone you trust."}</h2></div><button className="button button-secondary" onClick={onSafety}>View safety guide <ChevronRight size={16} /></button></Card></div>;
}

function Intake({ onResult }) {
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(kind) {
    setError(""); setBusy(true);
    try {
      if (kind === "text") {
        if (!text.trim()) throw new Error("Add a conversation before starting analysis.");
        onResult(await analyzeText(text, "pasted_conversation"));
      } else {
        if (!file) throw new Error("Choose a plain-text conversation export first.");
        onResult(await analyzeFile(file));
      }
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  return <main>
    <div className="page-intro"><div><span className="eyebrow">Secure conversation intake</span><h1>Bring the context.</h1><p>The engine reads conversational structure and behavioural cues. It does not identify or profile a person.</p></div><div className="privacy-note"><ShieldCheck size={18} /><span>Your conversation is sent only to your configured HerBeacon API.</span></div></div>
    {error && <div className="alert"><CircleAlert size={18} />{error}</div>}
    <div className="intake-grid">
      <Card><div className="card-heading"><MessageSquare size={20} /><h2>Paste conversation</h2></div><p className="muted">Use speaker labels when available for the clearest timeline.</p><textarea value={text} onChange={(e) => setText(e.target.value)} placeholder={"Alice\nHello, how are you?\n\nJordan\nI have something urgent to ask..."} /><div className="form-footer"><span>{text.length.toLocaleString()} characters</span><button className="button button-primary" disabled={busy} onClick={() => submit("text")}>{busy ? "Analyzing…" : "Run analysis"} <ArrowRight size={16} /></button></div></Card>
      <Card><div className="card-heading"><Upload size={20} /><h2>Upload a text file</h2></div><p className="muted">Upload a plain-text conversation export. The existing parser handles its structure.</p><label className="dropzone"><Upload size={28} /><strong>{file ? file.name : "Choose a .txt file"}</strong><span>{file ? `${(file.size / 1024).toFixed(1)} KB ready` : "or drag and drop it here"}</span><input type="file" accept=".txt,text/plain" onChange={(e) => setFile(e.target.files?.[0] || null)} /></label><button className="button button-primary full-width" disabled={busy} onClick={() => submit("file")}>{busy ? "Analyzing…" : "Analyze uploaded file"} <ArrowRight size={16} /></button></Card>
    </div>
  </main>;
}

function Matrix({ result }) {
  if (!result) return <main><PageTitle eyebrow="Risk & escalation matrix" title="Understand the weight of the signals." text="Run an analysis to see the engine's explainable output." /><EmptyState /></main>;
  const risk = get(result, "risk_assessment") || {}, esc = get(result, "escalation_analysis") || {}, exp = get(result, "explainability") || {};
  const drivers = exp.top_risk_drivers || [];
  return <main><PageTitle eyebrow="Risk & escalation matrix" title="Understand the weight of the signals." text="This is a behavioural risk indicator, not a verdict. Every view stays anchored to what the engine observed." /><div className="stats-grid"><Stat label="Risk indicator" value={`${risk.risk_score ?? "—"}/100`} note={<RiskBadge level={risk.risk_level} />} /><Stat label="Escalation index" value={`${esc.escalation_score ?? "—"}/100`} note={esc.velocity || "No escalation"} /><Stat label="Maximum stage" value={esc.max_stage ?? "—"} note={esc.max_stage_name || "Baseline"} /><Stat label="Analysis mode" value={result.analysis_mode || "—"} note="Existing AI engine" /></div><div className="two-col"><Card><div className="card-heading"><BarChart3 size={20} /><h2>Risk indicator</h2></div><div className="big-score">{risk.risk_score ?? "—"}<small>/100</small></div><RiskBadge level={risk.risk_level} /><div className="meter"><span style={{ width: `${Math.min(100, Number(risk.risk_score) || 0)}%` }} /></div><p className="muted">{risk.summary || "No summary available."}</p></Card><Card><div className="card-heading"><Lightbulb size={20} /><h2>Top risk drivers</h2></div>{drivers.length ? drivers.map((driver, index) => <div className="driver" key={`${driver.feature_name}-${index}`}><div><strong>{driver.feature_name || driver.factor || "Risk driver"}</strong><small>{driver.detail || ""}</small></div><b>{driver.contribution_points ?? driver.shap_value ?? "—"}</b></div>) : <p className="muted">No risk drivers were returned for this conversation.</p>}</Card></div><Escalation result={result} /></main>;
}

function Escalation({ result }) {
  const esc = get(result, "escalation_analysis") || {};
  const active = esc.active_stages || [0];
  return <Card className="escalation-card"><div className="section-heading"><div><span className="eyebrow">Observed pathway</span><h2>Escalation stages</h2></div><RiskBadge level={esc.funnel_status === "MULTI_PHASE_FUNNEL" ? "HIGH" : "MODERATE"} /></div><div className="stepper">{stages.map((stage, index) => <div className={`stage ${active.includes(index) ? "stage-active" : ""}`} key={stage}><div className="stage-number">{index}</div><strong>{stage}</strong>{index < stages.length - 1 && <div className="stage-line" />}</div>)}</div><p className="muted">{esc.narrative || "No escalation narrative available."}</p></Card>;
}

function Patterns({ result }) {
  if (!result) return <main><PageTitle eyebrow="Behavioural pattern hub" title="Name the signals, not the person." text="Run an analysis to inspect evidence-backed behavioural patterns." /><EmptyState /></main>;
  const messages = result.messages || [], counts = get(result, "behavioral_patterns", "pattern_counts") || {}, patterns = {};
  messages.forEach((message) => (message.patterns || []).forEach((pattern) => { patterns[pattern.pattern_key] ||= pattern; }));
  return <main><PageTitle eyebrow="Behavioural pattern hub" title="Name the signals, not the person." text="Confidence is contextual, rule-based confidence from the engine — not a probability of identity or intent." /><Card className="chart-card pattern-chart"><div className="card-heading"><BarChart3 size={20} /><div><h2>Behavioural Signal Distribution</h2><p className="chart-subtitle">Actual cues detected by the existing engine.</p></div></div><SignalChart result={result} /></Card><div className="pattern-grid">{Object.entries(patterns).map(([key, pattern]) => <Card key={key} className="pattern-card"><div className="pattern-top"><span className="pattern-icon"><Network size={17} /></span><RiskBadge level={pattern.severity} /></div><h3>{pattern.pattern_name || key}</h3><span className="cue-count">{counts[key] || 0} cue(s) detected</span><p>{pattern.explanation || "No explanation available."}</p>{(pattern.evidence || []).map((evidence) => <blockquote key={evidence}>“{evidence}”</blockquote>)}<div className="confidence"><span>Rule-based confidence</span><b>{Math.round((Number(pattern.detection_confidence) || 0) * 100)}%</b></div></Card>)}</div>{!Object.keys(patterns).length && <Card className="success-card"><CheckCircle2 />No defined behavioural pattern cues were observed in this conversation.</Card>}</main>;
}

function Timeline({ result }) {
  if (!result) return <main><PageTitle eyebrow="Timeline intelligence" title="See how context changes over time." text="Run an analysis to map turn-level signals." /><EmptyState /></main>;
  const timeline = get(result, "risk_timeline") || {};
  return <main><PageTitle eyebrow="Timeline intelligence" title="See how context changes over time." text="Checkpoints use the same central scoring framework as the final conversation indicator." /><div className="stats-grid"><Stat label="Trajectory" value={timeline.trajectory_type || "—"} /><Stat label="Initial" value={`${timeline.initial_risk_score ?? "—"}/100`} /><Stat label="Peak" value={`${timeline.peak_risk_score ?? "—"}/100`} /><Stat label="Final" value={`${timeline.final_risk_score ?? "—"}/100`} /></div><Card className="chart-card"><div className="card-heading"><Network size={20} /><div><h2>Risk Progression</h2><p className="chart-subtitle">Hover checkpoints for actual turn and score details.</p></div></div>  <RiskProgression result={result} height={360} /></Card><div className="section-heading timeline-heading"><div><span className="eyebrow">Evidence second</span><h2>Detailed evidence trail</h2></div></div><Card><div className="timeline">{(timeline.milestones || []).map((milestone, index) => <div className="timeline-row" key={`${milestone.turn}-${index}`}><div className="timeline-dot" /><div className="timeline-copy"><strong>Turn {milestone.turn} · {milestone.stage_name || "Baseline"}</strong><span>{milestone.explanation || ""}</span></div><div className="timeline-score"><b>{milestone.risk_score ?? "—"}/100</b><RiskBadge level={milestone.risk_level} /></div></div>)}</div>{!timeline.milestones?.length && <p className="muted">No milestone evidence was returned for this analysis.</p>}</Card></main>;
}

function Safety({ result }) {
  if (!result) return <main><PageTitle eyebrow="Actionable safety guide" title="Move at the speed of safety." text="Run an analysis to receive context-aware guidance." /><EmptyState /></main>;
  const safety = get(result, "safety_recommendations") || {};
  return <main><PageTitle eyebrow="Actionable safety guide" title="Move at the speed of safety." text="These are practical decision-support steps. You stay in control of what feels safe." /><Card className="directive"><span className="eyebrow">Primary safety directive · {safety.priority || "Review"}</span><h2>{safety.primary_action || "Review the conversation with someone you trust."}</h2></Card><div className="safety-grid">{(safety.actions || []).map((item, index) => <Card key={`${item.headline}-${index}`}><span className="step-label">0{index + 1}</span><h3>{item.headline || "Safety step"}</h3><p>{item.action || ""}</p><small>{item.rationale || ""}</small></Card>)}</div><Card><h2>Verification checklist</h2><ul className="checklist">{(safety.verification_steps || []).map((step) => <li key={step}><CheckCircle2 size={17} />{step}</li>)}</ul></Card></main>;
}

function ReportFooter() {
  return null;
}

function ReportExplainability({ result }) {
  const messages = result?.messages || [];
  const patterns = {};
  messages.forEach((message) => (message.patterns || []).forEach((pattern) => {
    const severity = String(pattern.severity || "").toUpperCase();
    if (!["HIGH", "CRITICAL", "MODERATE", "MEDIUM", "LOW"].includes(severity)) return;
    const key = pattern.pattern_key || pattern.pattern_name;
    if (!patterns[key]) patterns[key] = { ...pattern, evidence: [], cueCount: 0 };
    patterns[key].cueCount += 1;
    patterns[key].evidence.push(...(pattern.evidence || []));
  }));
  const items = Object.values(patterns);
  if (!items.length) return <Card className="empty-state"><strong>No explainable pattern details were returned.</strong></Card>;
  return <div className="report-explain-list">{items.map((pattern) => <Card className="report-explain-item" key={pattern.pattern_key || pattern.pattern_name}><div className="report-explain-head"><div><span className="eyebrow">Pattern</span><h3>{pattern.pattern_name || pattern.pattern_key}</h3></div><RiskBadge level={pattern.severity} /></div><div className="report-explain-flow"><div><span>Evidence</span><blockquote>{pattern.evidence?.slice(0, 1).map((item) => `“${item}”`).join("") || "Evidence text was not returned."}</blockquote></div><div><span>Why it matters</span><p>{pattern.explanation || "This behavioural pattern was observed in the conversation."}</p></div><div><span>Observed</span><strong>{pattern.cueCount} cue(s)</strong></div></div></Card>)}</div>;
}

function ReportEvidence({ result }) {
  const messages = (result?.messages || []).flatMap((message) => (message.patterns || []).filter((pattern) => ["HIGH", "CRITICAL", "MODERATE", "MEDIUM", "LOW"].includes(String(pattern.severity || "").toUpperCase())).map((pattern) => ({ message, pattern })));
  if (!messages.length) return <Card className="empty-state"><strong>No key evidence was returned for this analysis.</strong></Card>;
  return <div className="report-evidence-list">{messages.map(({ message, pattern }, index) => <Card className="report-evidence-row" key={`${message.message_index}-${pattern.pattern_key}-${index}`}><div className="report-evidence-meta"><strong>Turn {message.message_index ?? "—"}</strong><span>{message.speaker || "Conversation participant"}</span><RiskBadge level={pattern.severity} /></div><div><span className="eyebrow">Observed phrase</span><blockquote>{(pattern.evidence || []).slice(0, 1).map((item) => `“${item}”`).join("") || "Phrase evidence was not returned."}</blockquote></div><div><span className="eyebrow">Behavioural pattern</span><strong>{pattern.pattern_name || pattern.pattern_key}</strong><p>{pattern.explanation || "Behavioural signal observed in this turn."}</p></div></Card>)}</div>;
}

function ReportEscalation({ result }) {
  const esc = get(result, "escalation_analysis") || {};
  const active = esc.active_stages || [];
  return <><div className="report-stage-list">{stages.map((stage, index) => <div className={`report-stage-row ${active.includes(index) ? "observed" : ""}`} key={stage}><span className="report-stage-number">{index}</span><strong>{stage}</strong><span>{active.includes(index) ? "Observed stage" : "Not observed in returned output"}</span></div>)}</div><div className="report-escalation-summary"><p><b>Current stage:</b> {esc.max_stage_name || "Baseline"}</p><p><b>Progression:</b> {esc.narrative || "No escalation narrative was returned."}</p></div></>;
}

function Report({ result }) {
  if (!result) return <main><PageTitle eyebrow="Executive report & export" title="Make the insight portable." text="Run an analysis to generate a consolidated report." /><EmptyState /></main>;
  const risk = get(result, "risk_assessment") || {}, patterns = get(result, "behavioral_patterns") || {}, safety = get(result, "safety_recommendations") || {};
  const reportRef = useRef(null);
  const [exporting, setExporting] = useState(false);
  async function downloadPdf() {
    if (!reportRef.current) return;
    setExporting(true);
    const pdf = new jsPDF("p", "mm", "a4");
    const report = reportRef.current.querySelector(".report");
    const sections = report ? Array.from(report.querySelectorAll(".report-page-section")) : [];
    const margin = 10;
    const pageWidth = 190;
    const pageHeight = 277;
    let hasContent = false;

    for (const section of sections) {
      const evidenceRows = Array.from(section.querySelectorAll(".report-evidence-row"));
      if (evidenceRows.length) {
        const heading = section.querySelector(":scope > h3");
        const headingCanvas = heading ? await html2canvas(heading, { backgroundColor: "#FFFFFF", scale: 1, useCORS: true, logging: false }) : null;
        let rowY = margin;
        let pageStarted = false;
        for (const row of evidenceRows) {
          const rowCanvas = await html2canvas(row, { backgroundColor: "#FFFFFF", scale: 1, useCORS: true, logging: false });
          const rowHeight = (rowCanvas.height * pageWidth) / rowCanvas.width;
          const headingHeight = headingCanvas ? (headingCanvas.height * pageWidth) / headingCanvas.width : 0;
          if (!pageStarted || rowY + rowHeight > pageHeight) {
            if (hasContent || pageStarted) pdf.addPage();
            rowY = margin;
            pageStarted = true;
            if (headingCanvas) {
              pdf.addImage(headingCanvas.toDataURL("image/png"), "PNG", margin, rowY, pageWidth, headingHeight);
              rowY += headingHeight + 8;
            }
          }
          pdf.addImage(rowCanvas.toDataURL("image/png"), "PNG", margin, rowY, pageWidth, rowHeight);
          rowY += rowHeight + 4;
          hasContent = true;
        }
        continue;
      }
      const canvas = await html2canvas(section, { backgroundColor: "#FFFFFF", scale: 1, useCORS: true, logging: false });
      const sectionHeight = (canvas.height * pageWidth) / canvas.width;
      if (hasContent) pdf.addPage();
      const scale = Math.min(1, pageHeight / sectionHeight);
      const fittedWidth = pageWidth * scale;
      const fittedHeight = sectionHeight * scale;
      pdf.addImage(canvas.toDataURL("image/png"), "PNG", margin + ((pageWidth - fittedWidth) / 2), margin, fittedWidth, fittedHeight);
      hasContent = true;
    }
    pdf.save("herbeacon-analysis-report.pdf");
    setExporting(false);
  }
  return <main><PageTitle eyebrow="Executive report & export" title="Evidence-oriented analysis report." text="A visual, safety-first summary for reflection, support conversations, or responsible review." /><div className="report-actions"><button className="button button-primary" disabled={exporting} onClick={downloadPdf}>{exporting ? "Preparing PDF…" : "Download PDF"} <FileText size={16} /></button></div><div ref={reportRef} className="report-canvas"><Card className="report"><div className="report-page-section"><div className="report-brand"><span>HERBEACON</span><small>Behavioural safety intelligence</small></div><h2>Evidence-oriented analysis report</h2><div className="report-summary"><Stat label="Risk score" value={`${risk.risk_score ?? "—"}/100`} /><Stat label="Risk level" value={risk.risk_level || "—"} /><Stat label="Cues detected" value={patterns.total_cues_detected ?? "—"} /><Stat label="Trajectory" value={get(result, "risk_timeline", "trajectory_type") || "—"} /></div><div className="report-executive-grid"><div><span className="eyebrow">What was observed</span><p>{risk.summary || "The engine returned no summary."}</p></div><div><span className="eyebrow">Why it matters</span><p>{get(result, "explainability", "narrative") || "Behavioural patterns were reviewed using the existing analysis engine."}</p></div><div><span className="eyebrow">Current stage</span><p>{get(result, "escalation_analysis", "max_stage_name") || "Baseline"}</p></div><div><span className="eyebrow">Immediate action</span><p>{safety.primary_action || "Review the conversation with someone you trust."}</p></div></div><ReportFooter page="1" /></div><div className="report-page-section"><h3>Conversation intelligence</h3><div className="report-chart-grid"><Card><h3>Behavioural Signal Distribution</h3><SignalChart result={result} /></Card><Card><h3>Risk Factor Contribution</h3><ContributionChart result={result} /></Card></div><Card><h3>Risk Progression</h3><RiskProgression result={result} height={300} /></Card><ReportFooter page="2" /></div><div className="report-page-section"><h3>Why was this conversation flagged?</h3><ReportExplainability result={result} /><ReportFooter page="3" /></div><div className="report-page-section"><h3>Key evidence</h3><ReportEvidence result={result} /><ReportFooter page="4" /></div><div className="report-page-section"><h3>Escalation journey</h3><ReportEscalation result={result} /><ReportFooter page="5" /></div><div className="report-page-section"><h3>Situation-specific safety actions</h3><div className="report-safety-grid">{(safety.actions || []).map((item, index) => <Card className={index === 0 ? "priority-safety-card" : ""} key={`${item.headline}-${index}`}><span className="step-label">0{index + 1}</span><h3>{item.headline || "Safety step"}</h3><p>{item.rationale || ""}</p><strong>{item.action || ""}</strong></Card>)}</div><div className="report-next-steps"><span className="eyebrow">Immediate next steps</span>{(safety.verification_steps || []).slice(0, 4).map((step) => <span key={step}>{step}</span>)}</div><ReportFooter page="6" /></div></Card></div></main>;
}

function PageTitle({ eyebrow, title, text }) {
  return <div className="page-title"><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{text}</p></div>;
}

export default function App() {
  const [page, setPage] = useState("overview");
  const [result, setResult] = useState(() => {
    try {
      const saved = window.sessionStorage.getItem("analysis_result");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const [analysisVersion, setAnalysisVersion] = useState(0);
  const current = useMemo(() => nav.find(([id]) => id === page), [page]);
  useEffect(() => {
    try {
      if (result) window.sessionStorage.setItem("analysis_result", JSON.stringify(result));
      else window.sessionStorage.removeItem("analysis_result");
    } catch {
      // Session persistence is an enhancement; analysis remains available in memory.
    }
  }, [result]);
  function navigate(id) { setPage(id); setMobileOpen(false); window.scrollTo({ top: 0, behavior: "smooth" }); }
  function handleAnalysisResult(analysis) {
    setResult(analysis);
    setAnalysisVersion((version) => version + 1);
    navigate("matrix");
  }
  return <div className="app-shell"><aside className={mobileOpen ? "sidebar open" : "sidebar"}><div className="brand"><BrandMark /><div><strong>HerBeacon</strong><span>Behavioural safety intelligence</span></div><button className="icon-button sidebar-close" onClick={() => setMobileOpen(false)}><X size={19} /></button></div><div className="sidebar-rule" /><nav>{nav.map(([id, label, Icon]) => <button key={id} className={page === id ? "nav-item active" : "nav-item"} onClick={() => navigate(id)}><Icon size={18} /><span>{label}</span>{page === id && <ChevronRight size={15} />}</button>)}</nav><div className="sidebar-usp"><span>Core USP</span><p>“We don't detect suspicious people; we detect suspicious behavioural patterns.”</p></div><div className="sidebar-footer"><span className="status-dot" /> Engine bridge ready</div></aside><div className="mobile-bar"><button className="icon-button" onClick={() => setMobileOpen(true)}><Menu size={22} /></button><strong>HerBeacon</strong></div><div className="main-shell"><header className="topbar"><div className="breadcrumb">Workspace <ChevronRight size={14} /> <span>{current?.[1]}</span></div>{result ? <div className="analysis-chip"><span className="status-dot" /> Analysis saved</div> : <div className="analysis-chip muted-chip">No analysis loaded</div>}</header>{page === "overview" && <Overview key={analysisVersion} onStart={() => navigate("intake")} onSafety={() => navigate("safety")} result={result} />}{page === "intake" && <Intake onResult={handleAnalysisResult} />}{page === "matrix" && <Matrix key={analysisVersion} result={result} />}{page === "patterns" && <Patterns key={analysisVersion} result={result} />}{page === "timeline" && <Timeline key={analysisVersion} result={result} />}{page === "safety" && <Safety key={analysisVersion} result={result} />}{page === "report" && <Report key={analysisVersion} result={result} />}</div></div>;
}
