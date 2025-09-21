import streamlit as st
from legal_utils import get_simple, get_risk, get_bullets, log_entry
from fpdf import FPDF
import base64
import io
import PyPDF2
import json

# Chat history management
HISTORY_FILE = 'user_history.json'
if 'chat_history' not in st.session_state:
    try:
        with open(HISTORY_FILE, 'r') as f:
            st.session_state['chat_history'] = json.load(f)
    except Exception:
        st.session_state['chat_history'] = []
import json
# Chat history management
HISTORY_FILE = 'user_history.json'
if 'chat_history' not in st.session_state:
    try:
        with open(HISTORY_FILE, 'r') as f:
            st.session_state['chat_history'] = json.load(f)
    except Exception:
        st.session_state['chat_history'] = []

def save_history(entry):
    st.session_state['chat_history'].append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(st.session_state['chat_history'], f)

def clear_history():
    st.session_state['chat_history'] = []
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)
import io
import PyPDF2
from fpdf import FPDF
import base64
import streamlit as st
from legal_utils import get_simple, get_risk, get_bullets, log_entry
st.set_page_config(page_title="Legal Lens: AI-Powered Legal Document Demystifier", page_icon="📄", layout="centered")

st.markdown("""
    <style>
    body {
        background: #181c24;
    }
    .main-card {
        background: #23272f;
        border-radius: 18px;
        box-shadow: 0 4px 24px 0 #00000033;
        padding: 2.5rem 2rem 2rem 2rem;
        margin-bottom: 2rem;
    }
    .risk-badge {
        display: inline-block;
        padding: 0.4em 1.2em;
        border-radius: 1.2em;
        font-weight: bold;
        font-size: 1.1em;
        margin-top: 0.5em;
        margin-bottom: 1em;
    }
    .risk-low { background: #1e5631; color: #fff; }
    .risk-medium { background: #e1ad01; color: #23272f; }
    .risk-high { background: #b80c09; color: #fff; }
    .section-title {
        font-size: 1.5em;
        font-weight: 700;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        color: #f3f3f3;
        letter-spacing: 0.01em;
    }
    .bullet-list li {
        margin-bottom: 0.5em;
        font-size: 1.1em;
    }
    .stTextArea textarea {
        background: #23272f;
        color: #fff;
        border-radius: 10px;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("<h1 style='color:#f3f3f3; font-size:2.3em; margin-bottom:0.2em;'>📄 Legal Lens</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#b0b0b0; font-size:1.1em; margin-bottom:1.5em;'>AI-Powered Legal Document Demystifier</div>", unsafe_allow_html=True)


# File upload for PDF/TXT
uploaded_file = st.file_uploader("Upload a legal document (PDF or TXT)", type=["pdf", "txt"])
file_text = ""
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_text += page.extract_text() or ""
    elif uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")

# Session state for reset
if 'text_input' not in st.session_state:
    st.session_state['text_input'] = file_text

def reset_form():
    st.session_state['text_input'] = ''
    st.session_state['file_uploader'] = None

col1, col2 = st.columns([4,1])
with col1:
    text = st.text_area("Paste legal text here", value=st.session_state['text_input'], key='text_input', height=180)
with col2:
    st.write("")
    st.write("")
    if st.button("Reset", key="reset_btn", use_container_width=True):
        reset_form()

analyze_clicked = st.button("Analyze", use_container_width=True, key="analyze_btn")
if analyze_clicked and text.strip():
    with st.spinner("Analyzing with AI..."):
        simple = get_simple(text)
        risk, color = get_risk(text, simple)
        bullets = get_bullets(text)

        st.markdown(f"<div class='section-title'>Plain English Explanation</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#e6e6e6; font-size:1.15em; margin-bottom:1.5em;'>{simple}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='section-title'>Bullet Point Summary</div>", unsafe_allow_html=True)
        keywords = [
            'notice', 'risk', 'penalty', 'fee', 'lawsuit', 'termination', 'obligation',
            'liability', 'fine', 'forfeit', 'breach', 'consent', 'required', 'must', 'should', 'data sharing'
        ]
        bullet_lines = []
        for b in bullets:
            clean_b = b.lstrip('-•○* \t').strip()
            for word in keywords:
                clean_b = clean_b.replace(word, f"<b>{word}</b>")
                clean_b = clean_b.replace(word.capitalize(), f"<b>{word.capitalize()}</b>")
            st.markdown(f"- {clean_b}")
            bullet_lines.append(clean_b)
        st.markdown("<div style='margin-bottom:1em;'></div>", unsafe_allow_html=True)

    # Copy Summary button
    summary_text = f"Plain English Explanation:\n{simple}\n\nBullet Point Summary:\n" + "\n".join(f"- {b}" for b in bullet_lines)
    st.code(summary_text, language=None)
    st.button("Copy Summary to Clipboard", on_click=lambda: st.session_state.update({'_clipboard': summary_text}), key="copy_summary_btn")

    # Download as PDF button
    def create_pdf(expl, bullets, risk):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(0, 10, "Legal Lens: AI-Powered Legal Document Demystifier", ln=True, align='C')
        pdf.ln(8)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Plain English Explanation:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, expl)
        pdf.ln(4)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Bullet Point Summary:", ln=True)
        pdf.set_font("Arial", size=12)
        for b in bullets:
            pdf.multi_cell(0, 8, f"- {b}")
        pdf.ln(4)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Risk Level: {risk}", ln=True)
        return pdf

    if st.button("Download as PDF", key="download_pdf_btn"):
        pdf = create_pdf(simple, bullet_lines, risk)
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="legal_lens_summary.pdf">Click here to download your summary PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

    risk_class = 'risk-low' if risk == 'Low' else ('risk-medium' if risk == 'Medium' else 'risk-high')
    st.markdown(f"<div class='section-title'>Risk Level</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='risk-badge {risk_class}'>{risk}</span>", unsafe_allow_html=True)

    log_entry(text, simple, risk, bullets)

    # Save to chat history
    save_history({
        'input': text,
        'explanation': simple,
        'bullets': bullet_lines,
        'risk': risk
    })

# Show chat history
with st.expander("View My Analysis History"):
    if st.session_state['chat_history']:
        for i, entry in enumerate(reversed(st.session_state['chat_history'])):
            st.markdown(f"**Analysis #{len(st.session_state['chat_history'])-i}:**")
            st.markdown(f"<b>Input:</b> {entry['input']}", unsafe_allow_html=True)
            st.markdown(f"<b>Explanation:</b> {entry['explanation']}", unsafe_allow_html=True)
            st.markdown("<b>Bullet Points:</b>", unsafe_allow_html=True)
            for b in entry['bullets']:
                st.markdown(f"- {b}")
            st.markdown(f"<b>Risk Level:</b> {entry['risk']}", unsafe_allow_html=True)
            st.markdown("---")
    if st.button("Clear My History", key="clear_hist_btn"):
            clear_history()
            st.experimental_rerun()
    else:
        st.info("No previous analyses found on this device.")


if not (analyze_clicked and text.strip()):
    st.info("Enter legal text and click Analyze.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#888; margin-top:2em;'>Made for <b>Google GenAI Exchange Hackathon</b> | Team Legal Lens</div>", unsafe_allow_html=True)
