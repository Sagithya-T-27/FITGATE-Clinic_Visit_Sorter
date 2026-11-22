from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# FITGATE Premium workspace — UI layer only. Core classification and safety
# decisions remain in fitgate.py; this app does not diagnose or make clinical decisions.

ROOT = Path(__file__).resolve().parent
VISITS_FILE = ROOT / "visits.csv"
OUTPUT_DIR = ROOT / "outputs"
REVIEWS_FILE = OUTPUT_DIR / "review_status.json"

st.set_page_config(page_title="FITGATE | Clinic & Workplace Desk", page_icon="✳", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#17263c; --muted:#718096; --teal:#087f78; --mint:#e7f5f1; --line:#e7edf1; --paper:#f6f8fa; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--paper); color:var(--ink); }
[data-testid="stSidebar"] { background:#14243a; border-right:1px solid #24364e; }
[data-testid="stSidebar"] * { color:#e8f0f5 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .48rem .65rem; border-radius:9px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#223751; }
.block-container { padding-top:2rem; padding-bottom:3rem; max-width:1500px; }
h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.035em; color:var(--ink); }
h1 { font-weight:800; font-size:2.15rem; }
h2 { font-weight:750; font-size:1.45rem; }
h3 { font-weight:700; font-size:1.08rem; }
.eyebrow { color:var(--teal); text-transform:uppercase; font-size:.70rem; font-weight:800; letter-spacing:.14em; }
.hero { background:linear-gradient(115deg,#14243a 0%,#1b3b52 70%,#126e69 130%); border-radius:20px; padding:28px 30px; color:white; margin-bottom:20px; box-shadow:0 12px 35px rgba(20,36,58,.12); }
.hero h1 { color:white; margin:.35rem 0 .45rem; }
.hero p { color:#c8d8e2; margin:0; max-width:680px; }
.hero .eyebrow { color:#8ce0cb; }
.metric { background:white; border:1px solid var(--line); border-radius:15px; padding:17px 18px; min-height:112px; box-shadow:0 3px 12px rgba(25,45,65,.025); }
.metric-label { color:var(--muted); font-size:.78rem; font-weight:600; }
.metric-value { font-family:'Manrope'; font-size:1.9rem; font-weight:800; color:var(--ink); margin-top:4px; }
.metric-note { color:#8997a6; font-size:.72rem; margin-top:1px; }
.panel { background:white; border:1px solid var(--line); border-radius:16px; padding:19px 20px; }
.pill { display:inline-block; padding:4px 9px; border-radius:20px; font-size:.72rem; font-weight:700; background:#edf2f6; color:#536579; }
.small-muted { color:var(--muted); font-size:.82rem; }
div.stButton > button, div.stDownloadButton > button { border-radius:10px; font-weight:700; min-height:2.55rem; }
div.stButton > button[kind="primary"] { background:#087f78; border-color:#087f78; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
hr { border-color:var(--line); }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


def load_reviews():
    try:
        return json.loads(REVIEWS_FILE.read_text()) if REVIEWS_FILE.exists() else {}
    except Exception:
        return {}


def save_reviews(data):
    OUTPUT_DIR.mkdir(exist_ok=True)
    REVIEWS_FILE.write_text(json.dumps(data, indent=2))


def load_existing_rows():
    if not VISITS_FILE.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(VISITS_FILE).fillna("")
    except Exception as exc:
        st.error(f"Could not read visits.csv: {exc}")
        return pd.DataFrame()


def load_processed_rows():
    # Results from the actual FITGATE backend are cached for the current session.
    rows = st.session_state.get("processed_rows", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def priority_key(value):
    v = str(value).lower()
    if "see_now" in v or "see now" in v or "red" in v:
        return 0
    if "today" in v:
        return 1
    return 2


def badge_label(value):
    v = str(value or "Routine").replace("_", " ").title()
    return v


def metric_card(label, value, note=""):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)


def run_backend():
    """Run FITGATE's existing pipeline without reimplementing its logic."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except Exception:
        pass
    try:
        import fitgate
        from google import genai
    except Exception as exc:
        raise RuntimeError(f"Backend dependency/import problem: {exc}") from exc

    visits = fitgate.load_visits()
    prompt = fitgate.load_prompt()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key not found. Add GEMINI_API_KEY=... to your local .env file.")
    client = genai.Client(api_key=api_key)
    results = []
    progress = st.progress(0, text="Starting FITGATE assessment…")
    for index, visit in enumerate(visits):
        result = fitgate.process_visit(visit, client, prompt)
        results.append(result)
        progress.progress((index + 1) / max(len(visits), 1), text=f"Processing visit {index + 1} of {len(visits)}")
    fitgate.write_reports(results)
    st.session_state.processed_rows = results
    st.session_state.last_run = datetime.now().strftime("%d %b %Y · %I:%M %p")
    return len(results)


def run_script(script):
    path = ROOT / script
    if not path.exists():
        return f"{script} was not found in the project folder."
    proc = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, timeout=180)
    return (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "") + f"\n\nExit code: {proc.returncode}"


# Sidebar identity and navigation
with st.sidebar:
    st.markdown("<div style='padding:8px 4px 22px'><div style='font-family:Manrope;font-size:1.65rem;font-weight:800;letter-spacing:-.06em'>✳ FITGATE</div><div style='font-size:.72rem;color:#a9bdca!important;letter-spacing:.12em;text-transform:uppercase'>Clinic & workplace desk</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.68rem;color:#8da3b3!important;font-weight:800;letter-spacing:.13em;margin:0 0 8px 8px'>WORKSPACE</div>", unsafe_allow_html=True)
    page = st.radio("Navigation", ["Overview", "Worker check-in", "Care queue", "Workplace insights", "Reports", "Quality & safety"], label_visibility="collapsed")
    st.markdown("<div style='height:18px'></div><div style='border-top:1px solid #30445b;padding-top:15px;font-size:.75rem;color:#9db0bf!important'>FITGATE is decision support only.<br/>Clinical decisions remain with qualified staff.</div>", unsafe_allow_html=True)

# Data sources: processed pipeline first, raw file as a transparent fallback.
processed = load_processed_rows()
raw = load_existing_rows()
reviews = load_reviews()
if not processed.empty:
    data = processed.copy()
else:
    data = raw.copy()
    for col, default in [("priority", "Not assessed"), ("category", "Pending"), ("summary", "Not assessed yet"), ("flags", "")]:
        if col not in data.columns:
            data[col] = default

# Header
st.markdown('<div class="eyebrow">FITGATE / OPERATIONS</div>', unsafe_allow_html=True)
if page == "Overview":
    st.markdown('<div class="hero"><div class="eyebrow">A clearer view of worker wellbeing</div><h1>Good day. Your clinic, at a glance.</h1><p>One focused workspace for worker intake, safety-aware queue organisation and occupational health operations.</p></div>', unsafe_allow_html=True)
    total = len(data)
    assessed = len(processed)
    see_now = sum(priority_key(x) == 0 for x in data.get("priority", [])) if total else 0
    today = sum(priority_key(x) == 1 for x in data.get("priority", [])) if total else 0
    reviewed = sum(str(reviews.get(str(x), "")) == "Reviewed" for x in data.get("id", [])) if total else 0
    m = st.columns(4)
    with m[0]: metric_card("WORKER VISITS", total, "Records in current dataset")
    with m[1]: metric_card("SEE NOW FLAGS", see_now, "Requires prompt staff attention")
    with m[2]: metric_card("TODAY PRIORITY", today, "Prioritised for today's review")
    with m[3]: metric_card("REVIEWED", reviewed, "Staff review status recorded")
    st.write("")
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Queue snapshot")
        st.caption("Run the existing FITGATE engine to refresh classifications and reports.")
        if st.button("↻  Run FITGATE assessment", type="primary", use_container_width=True):
            with st.spinner("Running existing FITGATE pipeline…"):
                try:
                    count = run_backend()
                    st.success(f"Assessment completed for {count} visit(s).")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        if st.session_state.get("last_run"):
            st.caption(f"Last run: {st.session_state.last_run}")
        if not data.empty:
            show_cols = [c for c in ["id", "time", "job", "priority", "category", "summary"] if c in data.columns]
            view = data.copy()
            if "priority" in view.columns:
                view["_rank"] = view["priority"].apply(priority_key)
                view = view.sort_values("_rank").drop(columns="_rank")
            st.dataframe(view[show_cols].head(8), use_container_width=True, hide_index=True)
        else:
            st.info("No visits found yet. Start with Worker check-in or add records to visits.csv.")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Quick actions")
        st.write("Register a new worker visit, review the current queue, or run your quality checks.")
        if st.button("＋  Register a worker", use_container_width=True): st.session_state.nav_target = "Worker check-in"
        if st.button("▤  Open care queue", use_container_width=True): st.session_state.nav_target = "Care queue"
        if st.button("✓  Run safety tests", use_container_width=True): st.session_state.nav_target = "Quality & safety"
        st.markdown("<hr><div class='small-muted'>Safety first</div><b style='color:#17263c'>The software organises information; people make care decisions.</b>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.get("nav_target"):
        target = st.session_state.pop("nav_target")
        st.info(f"Use the left navigation to open **{target}**.")

elif page == "Worker check-in":
    st.title("Worker check-in")
    st.write("Capture the visit clearly. This form records the worker's own description; it does not diagnose or determine treatment.")
    if not VISITS_FILE.exists():
        st.warning("visits.csv was not found. Create it with columns: id,time,job,note before adding visits.")
    with st.form("intake_form", clear_on_submit=True):
        a, b = st.columns(2)
        with a:
            worker_id = st.text_input("Worker / visit ID", placeholder="e.g. V021")
            job = st.text_input("Job role", placeholder="e.g. Welder, Driver, Cleaner")
        with b:
            visit_time = st.time_input("Check-in time", value=datetime.now().time().replace(second=0, microsecond=0))
            department = st.text_input("Department (optional)", placeholder="e.g. Production")
        note = st.text_area("What is the worker experiencing?", placeholder="Use the worker's own words. Include when it started and any relevant details.", height=145)
        consent = st.checkbox("I have confirmed this information with the worker and will handle it according to our privacy process.")
        submitted = st.form_submit_button("Save visit to intake register", type="primary", use_container_width=True)
    if submitted:
        if not worker_id.strip() or not job.strip() or not note.strip():
            st.error("Please enter a visit ID, job role and symptom description.")
        elif not consent:
            st.error("Please confirm the privacy and information-handling step before saving.")
        elif not VISITS_FILE.exists():
            st.error("Cannot save: visits.csv does not exist.")
        else:
            try:
                with VISITS_FILE.open("r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or ["id", "time", "job", "note"]
                    existing = list(reader)
                if any(str(row.get("id", "")).strip().lower() == worker_id.strip().lower() for row in existing):
                    st.error("That visit ID already exists. Use a unique ID to avoid duplicate records.")
                else:
                    new_row = {"id": worker_id.strip(), "time": visit_time.strftime("%H:%M"), "job": job.strip(), "note": note.strip()}
                    if "department" in headers: new_row["department"] = department.strip()
                    with VISITS_FILE.open("a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
                        writer.writerow(new_row)
                    st.success(f"Visit {worker_id.strip()} saved to the intake register. Run FITGATE assessment from Overview to process it.")
            except Exception as exc:
                st.error(f"Could not save visit: {exc}")
    st.info("New visits are stored in visits.csv. They are not classified until the existing FITGATE backend is run.")

elif page == "Care queue":
    st.title("Care queue")
    st.write("A readable, filterable view of assessed visits for clinic staff.")
    if data.empty:
        st.info("No visit records are available yet.")
    else:
        c1, c2, c3 = st.columns([1.3, 1, 1])
        query = c1.text_input("Search visits", placeholder="Worker ID, job role or note")
        priorities = sorted(data["priority"].fillna("Not assessed").astype(str).unique()) if "priority" in data else []
        selected_priority = c2.selectbox("Priority", ["All priorities"] + priorities)
        status_filter = c3.selectbox("Review status", ["All", "Not reviewed", "Reviewed"])
        filtered = data.copy()
        if query:
            mask = filtered.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
        if selected_priority != "All priorities" and "priority" in filtered:
            filtered = filtered[filtered["priority"].astype(str) == selected_priority]
        if status_filter != "All" and "id" in filtered:
            wanted = "Reviewed" if status_filter == "Reviewed" else "Not reviewed"
            filtered = filtered[filtered["id"].astype(str).apply(lambda x: reviews.get(x, "Not reviewed")) == wanted]
        if "priority" in filtered:
            filtered = filtered.assign(_rank=filtered["priority"].apply(priority_key)).sort_values("_rank").drop(columns="_rank")
        display_cols = [c for c in ["id", "time", "job", "priority", "category", "summary"] if c in filtered]
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} of {len(data)} visit(s). Priority is generated by the FITGATE backend when assessed.")
        if "id" in filtered and not filtered.empty:
            selected_id = st.selectbox("Open a visit", filtered["id"].astype(str).tolist())
            record = filtered[filtered["id"].astype(str) == selected_id].iloc[0]
            st.markdown("### Visit details")
            l, r = st.columns([1.4, 1])
            with l:
                st.markdown(f"**{selected_id} · {record.get('job', 'Role not recorded')}**")
                st.write(record.get("note", "No note available."))
                st.markdown("**Backend summary**")
                st.write(record.get("summary", "Not assessed yet"))
                if record.get("priority_reason"): st.markdown(f"**Priority reason:** {record.get('priority_reason')}")
                if record.get("flags"): st.warning(f"Flags: {record.get('flags')}")
            with r:
                st.markdown("**Staff review**")
                current = reviews.get(selected_id, "Not reviewed")
                new_status = st.selectbox("Review status", ["Not reviewed", "Reviewed", "Follow-up required"], index=["Not reviewed", "Reviewed", "Follow-up required"].index(current) if current in ["Not reviewed", "Reviewed", "Follow-up required"] else 0, key=f"review_{selected_id}")
                staff_note = st.text_area("Internal review note (avoid unnecessary sensitive details)", key=f"note_{selected_id}", height=90)
                if st.button("Save staff review", type="primary"):
                    reviews[selected_id] = new_status
                    save_reviews(reviews)
                    st.success("Review status saved locally.")
            st.caption("Review status is an operational record only. It does not change FITGATE priority or clinical recommendations.")

elif page == "Workplace insights":
    st.title("Workplace insights")
    st.write("Operational visibility for HR and occupational-health teams. Use aggregate patterns to plan follow-up; do not use this view to make employment decisions.")
    if data.empty:
        st.info("No data available yet.")
    else:
        x, y = st.columns(2)
        with x:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.subheader("Visits by job role")
            if "job" in data:
                counts = data["job"].fillna("Unspecified").value_counts().rename_axis("Job role").reset_index(name="Visits")
                st.bar_chart(counts.set_index("Job role"))
            st.markdown("</div>", unsafe_allow_html=True)
        with y:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.subheader("Assessment categories")
            if "category" in data:
                counts = data["category"].fillna("Unspecified").value_counts().rename_axis("Category").reset_index(name="Visits")
                st.bar_chart(counts.set_index("Category"))
            st.markdown("</div>", unsafe_allow_html=True)
        st.caption("Charts reflect the currently loaded visit dataset. They are descriptive, not diagnostic or predictive.")

elif page == "Reports":
    st.title("Reports & exports")
    st.write("Download the output files produced by the existing FITGATE report writer.")
    queue_file = OUTPUT_DIR / "nurse_queue.csv"
    summary_file = OUTPUT_DIR / "summary.txt"
    a, b = st.columns(2)
    with a:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Nurse queue export")
        if queue_file.exists():
            st.download_button("Download nurse_queue.csv", queue_file.read_bytes(), file_name="nurse_queue.csv", mime="text/csv", use_container_width=True)
        else: st.info("No queue report yet. Run the assessment from Overview first.")
        st.markdown("</div>", unsafe_allow_html=True)
    with b:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Daily summary")
        if summary_file.exists():
            content = summary_file.read_text(encoding="utf-8", errors="replace")
            st.download_button("Download summary.txt", content, file_name="summary.txt", mime="text/plain", use_container_width=True)
            with st.expander("Preview summary"): st.text(content[:12000])
        else: st.info("No summary report yet. Run the assessment from Overview first.")
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Quality & safety":
    st.title("Quality & safety")
    st.write("Run the project's existing evaluation and red-team scripts. These tests help check system behaviour; they do not certify clinical safety.")
    st.warning("FITGATE is a prototype for queue organisation. It is not a medical device, diagnostic system or substitute for clinical triage. Emergency symptoms require immediate human assessment regardless of software output.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Evaluation harness")
        st.caption("Runs eval_harness.py from your project folder.")
        if st.button("Run evaluation", type="primary", use_container_width=True):
            with st.spinner("Running evaluation…"):
                st.session_state.eval_output = run_script("eval_harness.py")
        if st.session_state.get("eval_output"): st.code(st.session_state.eval_output[-12000:])
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Red-team tests")
        st.caption("Runs red_team_test.py from your project folder.")
        if st.button("Run red-team tests", type="primary", use_container_width=True):
            with st.spinner("Running red-team tests…"):
                st.session_state.redteam_output = run_script("red_team_test.py")
        if st.session_state.get("redteam_output"): st.code(st.session_state.redteam_output[-12000:])
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### Safety principles")
    st.markdown("- Worker notes are treated as data, not instructions to the model.\n- Python red-flag rules remain part of the existing backend.\n- The interface does not downgrade or override backend safety outcomes.\n- Staff review status is stored separately and never changes classification.\n- Keep API keys in `.env`; never commit `.env`, real worker records or identifiable health information to GitHub.")

st.markdown("<div style='margin-top:34px;padding-top:14px;border-top:1px solid #e7edf1;color:#8a98a7;font-size:.72rem'>FITGATE · Private operational workspace · Human-led care, safety-aware organisation</div>", unsafe_allow_html=True)
