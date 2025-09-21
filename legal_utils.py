import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

risk_words = {
    "high": ["penalty", "termination", "fee", "liability", "fine", "forfeit", "breach"],
    "medium": ["must", "should", "obligation", "data sharing", "required", "consent"]
}

risk_colors = {"Low": "green", "Medium": "orange", "High": "red"}

def get_simple(text):
    prompt = f"""
You are a legal expert for youth. Rewrite the following legal text in clear, concise, and professional plain English. Avoid phrases like 'Okay, here’s...' or 'Simplified Explanation:'. Focus on clarity and brevity.
Text: {text}
"""
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        res = model.generate_content(prompt)
        reply = res.text
        # Extracting explanation (before first bullet or 'Summary')
        lines = reply.split('\n')
        expl = []
        for line in lines:
            if line.strip().startswith("-") or "summary" in line.lower():
                break
            expl.append(line)
        return " ".join(expl).strip() or reply.strip()
    except Exception as e:
        return f"[Error: {e}]"

def get_bullets(text):
    prompt = f"""
You are a legal expert for youth. Summarize the following legal text in 3-5 clear, concise bullet points. Avoid any introductory phrases. Focus on the key obligations, risks, and actions.
Text: {text}
"""
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        res = model.generate_content(prompt)
        reply = res.text
        # Extract bullet points
        bullets = [l.strip("- ") for l in reply.split('\n') if l.strip().startswith("-")]
        return bullets if bullets else [reply.strip()]
    except Exception as e:
        return [f"[Error: {e}]"]

def get_risk(text, simple=None):
    t = (text + " " + (simple or "")).lower()
    for w in risk_words["high"]:
        if w in t:
            return "High", risk_colors["High"]
    for w in risk_words["medium"]:
        if w in t:
            return "Medium", risk_colors["Medium"]
    return "Low", risk_colors["Low"]

def log_entry(inp, expl, risk, bullets):
    try:
        with open("logs.csv", "a") as f:
            f.write(f'"{inp.replace("\"", "'")}","{expl.replace("\"", "'")}","{risk}","{'; '.join(bullets)}"\n')
    except Exception:
        pass
