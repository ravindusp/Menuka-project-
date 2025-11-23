import streamlit as st
import google.generativeai as genai
import json
from utils import check_typosquatting

# --- Page Config ---
st.set_page_config(page_title="PhishingGuard AI", page_icon="🛡️")

# --- Sidebar: API Key ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

# --- Main UI ---
st.title("🛡️ PhishingGuard AI")
st.markdown("### Advanced AI Phishing Detection")

sender_address = st.text_input("Sender Address", placeholder="e.g., security@paypaI.com")
email_subject = st.text_input("Email Subject", placeholder="e.g., Urgent: Account Suspended")
email_body = st.text_area("Email Body", height=150, placeholder="e.g., Dear Customer, click here to unlock...")

def analyze_with_llm(sender, subject, body, typo_alert):
    """
    Analyzes the email using Gemini API and returns a structured JSON response.
    """
    prompt = f"""
    You are a world-class cybersecurity expert specialized in phishing detection.
    Analyze the following email metadata and content to determine if it is a phishing attempt.

    Sender: {sender}
    Subject: {subject}
    Body: {body}

    System Alert: {typo_alert if typo_alert else "None"}

    Your task is to provide a comprehensive analysis in JSON format with the following fields:
    - "score": An integer from 0 to 100 representing the probability of phishing (0 = Safe, 100 = Definitely Phishing).
    - "is_phishing": A boolean (true if score > 50).
    - "explanation": A concise explanation of your findings.
    - "risk_factors": A list of strings highlighting specific red flags (e.g., "Urgency", "Mismatched Domain", "Typosquatting").

    Return ONLY valid JSON. Do not include markdown formatting like ```json ... ```.
    """

    model_names = ['gemini-2.5-flash', 'gemini-1.5-flash']

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            # Clean response text to ensure it's valid JSON
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            return json.loads(text)
        except Exception as e:
            # If it's the last model to try, raise the error
            if model_name == model_names[-1]:
                raise e
            continue

if st.button("Analyze Email"):
    if not sender_address or not email_body:
        st.warning("Please enter at least the Sender Address and Email Body.")
    else:
        # 1. Typosquatting Check (Python-based)
        typo_alert = check_typosquatting(sender_address)

        if typo_alert:
            st.error(typo_alert)

        # 2. LLM Analysis
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar to perform the analysis.")
        else:
            with st.spinner("AI Analyst is investigating..."):
                try:
                    result = analyze_with_llm(sender_address, email_subject, email_body, typo_alert)

                    score = result.get("score", 0)
                    is_phishing = result.get("is_phishing", False)
                    explanation = result.get("explanation", "No explanation provided.")
                    risk_factors = result.get("risk_factors", [])

                    st.subheader("Phishing Probability")
                    st.progress(score / 100.0)

                    st.write(f"**Score: {score}/100**")

                    if is_phishing:
                        st.error("🚨 High Risk of Phishing Detected!")
                    else:
                        st.success("✅ Looks Legitimate (Low Risk)")

                    st.divider()
                    st.markdown("### 🤖 AI Analysis Report")
                    st.info(explanation)

                    if risk_factors:
                        st.markdown("**Risk Factors Detected:**")
                        for factor in risk_factors:
                            st.markdown(f"- {factor}")

                except json.JSONDecodeError:
                    st.error("Error: Failed to parse AI response. The model might be overloaded or returned invalid format.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
