import streamlit as st
import joblib
import os
import google.generativeai as genai
from utils import check_typosquatting, clean_text, is_trusted_domain
from training import train_model

# --- Page Config ---
st.set_page_config(page_title="PhishingGuard Hybrid", page_icon="🛡️")

# --- Load Models ---
@st.cache_resource
def load_models():
    model_path = os.path.join("models", "phishing_model.pkl")

    # If model doesn't exist, train it on the fly (useful for cloud deployment)
    if not os.path.exists(model_path):
        with st.spinner("Model not found. Training Phishing Detection Model..."):
            try:
                model = train_model()
                return model
            except Exception as e:
                st.error(f"Error training model: {e}")
                return None

    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_models()

# --- Sidebar: API Key ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

# --- Main UI ---
st.title("🛡️ PhishingGuard Hybrid")
st.markdown("### Local Machine Learning + Explainable AI")

sender_address = st.text_input("Sender Address", placeholder="e.g., security@paypaI.com")
email_subject = st.text_input("Email Subject", placeholder="e.g., Urgent: Account Suspended")
email_body = st.text_area("Email Body", height=150, placeholder="e.g., Dear Customer, click here to unlock...")

if st.button("Analyze Email"):
    if not sender_address or not email_body:
        st.warning("Please enter at least the Sender Address and Email Body.")
    else:
        # 1. Typosquatting Check
        typo_alert = check_typosquatting(sender_address)

        if typo_alert:
            st.error(typo_alert)

        # 2. ML Model Prediction
        if model:
            # Combine subject and body for prediction
            full_text = f"{email_subject} {email_body}"
            cleaned_text = clean_text(full_text)

            # Get probability
            # Classes are [0, 1] -> index 1 is Phishing
            raw_prob = model.predict_proba([cleaned_text])[0][1]

            # 3. Trusted Domain Adjustment
            trusted_sender = is_trusted_domain(sender_address)
            final_prob = raw_prob

            if trusted_sender:
                # Heavily reduce probability for trusted domains
                # We cap the reduction so it doesn't go below 0
                reduction_factor = 0.40 # Reduce by 40%
                final_prob = max(0.0, raw_prob - reduction_factor)

            st.subheader("Phishing Probability")
            st.progress(final_prob)

            prob_text = f"**Probability: {final_prob * 100:.2f}%**"
            if trusted_sender and raw_prob > final_prob:
                 prob_text += f" (Reduced from {raw_prob * 100:.2f}% due to Trusted Sender)"
            st.write(prob_text)

            is_phishing = final_prob > 0.50

            if is_phishing:
                st.error("🚨 High Risk of Phishing Detected!")
            else:
                st.success("✅ Looks Legitimate (Low Risk)")

            # 4. AI Analyst (Gemini)
            # Trigger if Phishing > 50% OR Typosquatting Detected
            if is_phishing or typo_alert:
                st.divider()
                st.subheader("🤖 AI Security Analyst (Gemini 2.5)")

                if not api_key:
                    st.warning("Please enter your Gemini API Key in the sidebar to get an AI explanation.")
                else:
                    with st.spinner("Consulting Gemini AI..."):
                        try:
                            # Prepare Prompt
                            prompt = f"""
                            You are a cybersecurity expert. Analyze the following suspicious email.

                            Sender: {sender_address}
                            Subject: {email_subject}
                            Body: {email_body}

                            Context:
                            - Machine Learning Phishing Probability: {final_prob * 100:.1f}%
                            - Typosquatting Alert: {typo_alert if typo_alert else "None"}
                            - Trusted Sender: {"Yes" if trusted_sender else "No"}

                            Please explain clearly and concisely why this email is dangerous or suspicious.
                            Highlight specific red flags (urgency, fake domains, grammar, etc.).
                            """

                            # Try using gemini-2.5-flash as requested, fall back to 1.5-flash if not available
                            try:
                                ai_model = genai.GenerativeModel('gemini-2.5-flash')
                                response = ai_model.generate_content(prompt)
                            except Exception:
                                # Fallback
                                try:
                                    ai_model = genai.GenerativeModel('gemini-1.5-flash')
                                    response = ai_model.generate_content(prompt)
                                except Exception as e:
                                    st.error(f"Error calling Gemini API (Model not found or API Error): {e}")
                                    response = None

                            if response:
                                st.info(response.text)

                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
