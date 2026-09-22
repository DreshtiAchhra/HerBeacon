from pathlib import Path
import streamlit as st
import pandas as pd
from ai.pipeline import HerBeaconAnalysisEngine

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

st.set_page_config(page_title="HerBeacon | Safety Intelligence", page_icon="🕊️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root { --wine:#6B1E3F; --rose:#A64D6B; --gold:#D6A84F; --ivory:#FAF7F2; --ink:#252525; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--ivory); color:var(--ink); }
[data-testid="stSidebar"] {
    background: #321027;
    border-right: 1px solid #54203F;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.35rem 1rem; }
[data-testid="stSidebar"] * { color:#fff !important; }

/* Dashboard-style sidebar navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap: 7px; }
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 10px 12px;
    margin: 0;
    transition: background .18s ease, border-color .18s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:hover {
    background: #4b1c39;
    border-color: #67304f;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: #6B1E3F;
    border-color: #A64D6B;
    box-shadow: 0 5px 16px #17071455;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label p {
    font-size: .94rem;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label > div:first-child {
    margin-right: 10px;
}
.sidebar-brand { padding: 8px 5px 20px; margin-bottom: 12px; }
.sidebar-brand-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: .04em;
    line-height: 1.2;
}
.sidebar-brand-subtitle {
    color: #E8B9CE !important;
    font-size: .72rem;
    letter-spacing: .12em;
    margin-top: 7px;
}
.sidebar-motto {
    color: #E8B9CE !important;
    font-size: .86rem;
    line-height: 1.65;
    font-weight: 500;
}
.sidebar-note { color: #BFA9B8 !important; font-size: .72rem; line-height: 1.6; }
.sidebar-divider { border-top: 1px solid #54203F; margin: 25px 0 20px; }
.hero { background:linear-gradient(120deg,#41172d,#6B1E3F 65%,#8c3c5b); padding:2rem 2.2rem; border-radius:22px; color:white; margin-bottom:1.3rem; box-shadow:0 12px 30px #6b1e3f20; }
.hero h1 { font-family:'Playfair Display',serif; font-size:2.55rem; margin:0; color:white; }
.hero p { margin:.35rem 0 0; color:#f5e5eb; font-size:1.02rem; }
.eyebrow { text-transform:uppercase; letter-spacing:.18em; font-size:.72rem; color:#e6c2d0; font-weight:700; }
.section-title { font-family:'Playfair Display',serif; color:#541a34; font-size:1.6rem; margin:.5rem 0 .9rem; }
.metric-card { background:#fff; border:1px solid #eadde1; border-radius:16px; padding:1rem 1.1rem; min-height:110px; box-shadow:0 5px 18px #35142608; }
.metric-label { color:#786873; font-size:.82rem; font-weight:600; }
.metric-value { color:#541a34; font-size:1.75rem; font-weight:700; margin-top:.25rem; }
.panel { background:#fff; border:1px solid #eadde1; border-radius:16px; padding:1.2rem 1.35rem; margin:.55rem 0; }
.small-muted { color:#786873; font-size:.86rem; }
div.stButton > button[kind="primary"] { background:#6B1E3F; border:0; color:white; border-radius:10px; padding:.65rem 1.2rem; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { background:#f1e6e9; border-radius:10px 10px 0 0; padding:10px 18px; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return HerBeaconAnalysisEngine()

engine = get_engine()

with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div style="font-size:2.15rem; margin-bottom:8px;">🕊️</div>
            <div class="sidebar-brand-title">HERBEACON</div>
            <div class="sidebar-brand-subtitle">SAFER CONVERSATIONS</div>
        </div>
    """, unsafe_allow_html=True)

    nav_items = {
        "Overview": "▦   Overview",
        "Conversation Analysis": "▣   Conversation Analysis",
        "Escalation Engine": "↗   Escalation Engine",
        "Behavioural Patterns": "◈   Behavioural Patterns",
        "Risk Timeline": "◷   Risk Timeline",
        "Safety Recommendations": "♡   Safety Recommendations",
        "Analysis Report": "▤   Analysis Report",
    }
    selected_label = st.radio(
        "NAVIGATION",
        list(nav_items.values()),
        label_visibility="collapsed",
        key="herbeacon_sidebar_navigation",
    )
    page = next(name for name, label in nav_items.items() if label == selected_label)

    st.markdown("""
        <div class="sidebar-divider"></div>
        <div class="sidebar-motto">
            Detect the Pattern.<br>
            Understand the Risk.<br>
            Act Before Harm.
        </div>
        <br>
        <div class="sidebar-note">
            Prototype for safety awareness.<br>
            Not a legal or clinical determination.
        </div>
    """, unsafe_allow_html=True)

if "analysis_result" not in st.session_state: st.session_state.analysis_result = None
if "source_label" not in st.session_state: st.session_state.source_label = "No conversation analyzed yet"

st.markdown("<div class='hero'><div class='eyebrow'>WOMEN SAFETY • SOCIAL IMPACT</div><h1>HerBeacon</h1><p>Detect the Pattern. Understand the Risk. Act Before Harm.</p><p style='font-size:.88rem;margin-top:.85rem'>We don’t detect suspicious people; we detect suspicious behavioural patterns.</p></div>", unsafe_allow_html=True)

result = st.session_state.analysis_result

def metric(label, value):
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)

def panel(title, body):
    st.markdown(f"<div class='panel'><div style='font-weight:700;color:#541a34;font-size:1.05rem;margin-bottom:.45rem'>{title}</div>{body}</div>", unsafe_allow_html=True)

def safe_get(obj, *keys, default=None):
    for key in keys:
        if not isinstance(obj, dict): return default
        obj = obj.get(key)
        if obj is None: return default
    return obj

def risk_color(level):
    val = str(level).lower()
    if "high" in val or "critical" in val: return "🔴"
    if "moderate" in val or "medium" in val: return "🟠"
    if "low" in val: return "🟢"
    return "⚪"

if page == "Conversation Analysis":
    st.markdown("<div class='section-title'>Analyze a conversation</div>", unsafe_allow_html=True)
    st.write("Upload a `.txt` conversation, paste text, or select a dataset example. Analysis runs through the existing HerBeacon engine.")
    mode = st.radio("Input method", ["Paste conversation", "Upload .txt file", "Choose dataset sample"], horizontal=True)
    raw_text = ""
    upload = None
    sample_path = None
    if mode == "Paste conversation":
        raw_text = st.text_area("Conversation text", height=250, placeholder="Paste the conversation here…")
    elif mode == "Upload .txt file":
        upload = st.file_uploader("Choose a text file", type=["txt"])
        if upload:
            try: raw_text = upload.getvalue().decode("utf-8", errors="replace")
            except Exception: raw_text = ""
    else:
        samples = sorted(DATA_DIR.rglob("*.txt")) if DATA_DIR.exists() else []
        if samples:
            labels = [str(p.relative_to(ROOT)) for p in samples]
            chosen = st.selectbox("Dataset conversation", labels)
            sample_path = ROOT / chosen
            st.caption(f"Selected: {chosen}")
            try: raw_text = sample_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e: st.error(f"Could not read sample: {e}")
        else:
            st.info("No dataset `.txt` files were found in the project’s data folder. You can paste or upload a conversation instead.")
    with st.expander("Privacy & responsible use"):
        st.write("Use only conversations you have permission to analyze. This prototype provides pattern-based decision support; a score is not proof of fraud or a judgment about a person.")
    if st.button("Run conversation analysis", type="primary", disabled=not raw_text.strip()):
        try:
            with st.spinner("Analyzing conversation with HerBeacon engine…"):
                if sample_path is not None:
                    analysis = engine.analyze_file(sample_path)
                    label = sample_path.name
                else:
                    label = upload.name if upload else "Pasted conversation"
                    analysis = engine.analyze_text(raw_text, conversation_id=label)
                st.session_state.analysis_result = analysis
                st.session_state.source_label = label
            st.success("Analysis complete. Open the dashboard sections from the sidebar.")
        except Exception as e:
            st.error(f"Analysis could not be completed: {e}")
            st.exception(e)
    if result:
        st.markdown("### Current analysis snapshot")
        ra = result.get("risk_assessment", {})
        a,b,c = st.columns(3)
        with a: metric("Risk score", f"{ra.get('risk_score','—')}")
        with b: metric("Risk level", f"{risk_color(ra.get('risk_level'))} {ra.get('risk_level','—')}")
        with c: metric("Messages", result.get("metadata",{}).get("total_messages","—"))

elif page == "Overview":
    st.markdown("<div class='section-title'>Your safety intelligence overview</div>", unsafe_allow_html=True)
    if not result:
        a,b,c = st.columns(3)
        with a: metric("Analysis status", "Ready")
        with b: metric("Engine", "Connected")
        with c: metric("Conversation", "Not loaded")
        panel("Welcome to HerBeacon", "Start in <b>Conversation Analysis</b> to paste a conversation, upload a text file, or choose a dataset sample. Your results will appear across the dashboard.")
        st.markdown("#### How it works")
        cols = st.columns(3)
        for col, n, title, desc in zip(cols,["01","02","03"],["Detect patterns","Understand escalation","Explore safety actions"],["Surface behavioural cues across the conversation.","Review risk progression and the sequence of signals.","Read context-aware recommendations and verification steps."]):
            with col: panel(f"{n} · {title}", desc)
    else:
        ra = result.get("risk_assessment",{}); md = result.get("metadata",{}); bp = result.get("behavioral_patterns",{}); esc = result.get("escalation_analysis",{})
        cols=st.columns(4)
        with cols[0]: metric("Risk score", ra.get("risk_score","—"))
        with cols[1]: metric("Risk level", f"{risk_color(ra.get('risk_level'))} {ra.get('risk_level','—')}")
        with cols[2]: metric("Messages analyzed", md.get("total_messages",0))
        with cols[3]: metric("Behavioural cues", bp.get("total_cues_detected",0))
        panel("Current conversation", f"<b>{st.session_state.source_label}</b><br><span class='small-muted'>Mode: {result.get('analysis_mode','—')} · Speakers: {', '.join(map(str,md.get('speakers',[]))) or '—'}</span>")
        panel("Risk summary", str(ra.get("summary") or "No summary was returned by the engine."))
        panel("Escalation snapshot", f"<b>{esc.get('max_stage_name','—')}</b><br>{esc.get('narrative','No escalation narrative available.')}")

elif page == "Escalation Engine":
    st.markdown("<div class='section-title'>Escalation engine</div>", unsafe_allow_html=True)
    if not result: st.info("Analyze a conversation first to view escalation results.")
    else:
        e=result.get("escalation_analysis",{})
        x,y,z=st.columns(3)
        with x: metric("Highest stage", e.get("max_stage_name","—"))
        with y: metric("Escalation score", e.get("escalation_score","—"))
        with z: metric("Velocity", e.get("velocity","—"))
        panel("Escalation narrative", e.get("narrative") or "No narrative returned.")
        panel("Funnel status", str(e.get("funnel_status","Not available")))
        panel("Active stages", ", ".join(map(str,e.get("active_stages",[]))) or "No active stages listed.")
        transitions=e.get("stage_transitions",[])
        if transitions:
            st.markdown("#### Stage transitions")
            st.dataframe(pd.json_normalize(transitions), use_container_width=True, hide_index=True)

elif page == "Behavioural Patterns":
    st.markdown("<div class='section-title'>Behavioural patterns</div>", unsafe_allow_html=True)
    if not result: st.info("Analyze a conversation first to view detected patterns.")
    else:
        b=result.get("behavioral_patterns",{})
        x,y=st.columns(2)
        with x: metric("Cues detected", b.get("total_cues_detected",0))
        with y: metric("Flagged messages", b.get("flagged_message_count",0))
        counts=b.get("pattern_counts",{})
        if counts:
            st.markdown("#### Pattern frequency")
            chart_df=pd.DataFrame({"Pattern":list(counts.keys()),"Occurrences":list(counts.values())}).set_index("Pattern")
            st.bar_chart(chart_df)
            st.dataframe(chart_df, use_container_width=True)
        else: panel("Pattern frequency", "No pattern counts were returned.")
        panel("Detected pattern labels", ", ".join(map(str,b.get("patterns_detected",[]))) or "No labels listed.")
        st.markdown("#### Evidence snippets")
        evidence=b.get("evidence",[])
        if evidence:
            for i,item in enumerate(evidence,1):
                panel(f"Evidence {i}", str(item))
        else: st.caption("No evidence snippets were returned by the engine.")
        breakdown=b.get("speaker_breakdown",{})
        if breakdown:
            st.markdown("#### Speaker breakdown")
            st.json(breakdown)

elif page == "Risk Timeline":
    st.markdown("<div class='section-title'>Risk timeline</div>", unsafe_allow_html=True)
    if not result: st.info("Analyze a conversation first to view its risk timeline.")
    else:
        t=result.get("risk_timeline",{})
        x,y,z=st.columns(3)
        with x: metric("Initial score", t.get("initial_risk_score","—"))
        with y: metric("Peak score", t.get("peak_risk_score","—"))
        with z: metric("Final score", t.get("final_risk_score","—"))
        panel("Trajectory", str(t.get("trajectory_type","Not available")))
        cps=t.get("checkpoints",[])
        if cps:
            try:
                frame=pd.json_normalize(cps)
                numeric=[c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
                if numeric: st.line_chart(frame[numeric])
                st.dataframe(frame,use_container_width=True,hide_index=True)
            except Exception: st.write(cps)
        milestones=t.get("milestones",[])
        if milestones:
            st.markdown("#### Milestones")
            for i,m in enumerate(milestones,1): panel(f"Milestone {i}", str(m))
        phase=t.get("phase_analysis")
        if phase: panel("Phase analysis", str(phase))

elif page == "Safety Recommendations":
    st.markdown("<div class='section-title'>Safety recommendations</div>", unsafe_allow_html=True)
    if not result: st.info("Analyze a conversation first to view recommendations.")
    else:
        s=result.get("safety_recommendations",{})
        panel("Priority", str(s.get("priority","Not specified")))
        panel("Primary action", str(s.get("primary_action","No primary action returned.")))
        for heading,key in [("Recommended actions","actions"),("Verification steps","verification_steps"),("Support resources","support_resources")]:
            st.markdown(f"#### {heading}")
            items=s.get(key,[])
            if items:
                for item in items:
                    text=str(item)
                    st.markdown(f"- {text}")
            else: st.caption("No items returned by the engine.")

elif page == "Analysis Report":
    st.markdown("<div class='section-title'>Analysis report</div>", unsafe_allow_html=True)
    if not result: st.info("Analyze a conversation first to generate a report.")
    else:
        st.caption(f"Report for: {st.session_state.source_label}")
        st.json(result, expanded=False)
        report_text = __import__('json').dumps(result, indent=2, ensure_ascii=False, default=str)
        st.download_button("Download report as JSON", data=report_text, file_name="herbeacon_analysis_report.json", mime="application/json")
        st.info("Interpretation note: outputs are prototype decision-support signals, not proof of wrongdoing. Review the underlying conversation and use human judgment.")

st.markdown("<div style='text-align:center;color:#8a7480;font-size:.78rem;margin-top:2.5rem;padding:1rem'>HERBEACON · Safer Conversations, Brighter Tomorrows · Hackathon prototype</div>", unsafe_allow_html=True)
