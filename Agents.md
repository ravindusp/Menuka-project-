Role: You are a Senior Python Developer and Machine Learning Engineer.
Task: Build a complete, local "Phishing Email Detection System" called PhishingGuard Hybrid. This application must use Streamlit for the UI, LightGBM for the local machine learning classification, and Google Gemini API for providing explainable AI summaries.
Architecture Constraints:
Frontend: Streamlit (app.py).
Backend/ML: Scikit-learn (TF-IDF) + LightGBM.
Typosquatting Check: Use Levenshtein distance to detect fake domains (e.g., "gooogle.com" vs "https://www.google.com/search?q=google.com").
Explanation: Use the google.generativeai library to explain suspicious emails.
Data: Since I do not have a CSV ready, the training script must generate a synthetic dataset (small mock dataset) inside the code so I can run it immediately without external files.
Required File Structure & Content:
Please write the full code for the following files. Use code blocks for each file.
requirements.txt
Include: streamlit, pandas, scikit-learn, lightgbm, google-generativeai, python-Levenshtein, joblib.
utils.py (Helper Functions)
clean_text(text): A function to lowercase and clean email text.
check_typosquatting(sender_email): A function that extracts the domain from an email address and checks it against a hardcoded list of high-value targets (Google, PayPal, Amazon, Microsoft, Apple, Netflix). If the Levenshtein distance is 1 or 2, return a warning string.
training.py (The Model Builder)
Create a synthetic Pandas DataFrame with at least 20 examples of Phishing emails and 20 examples of Legitimate emails.
Build a Pipeline: TfidfVectorizer -> LightGBM Classifier.
Train the model on the synthetic data.
Save the model and vectorizer to a models/ folder using joblib.
Print the accuracy score.
app.py (The User Interface)
Setup: Load the saved model and vectorizer from the models/ folder.
Sidebar: Allow the user to input their Gemini API Key here (use st.text_input(type="password")).
Main UI: Three input fields (Sender Address, Email Subject, Email Body).
Logic:
Run check_typosquatting.
Run the ML model prediction.
Display a Gauge or Progress bar for the Phishing Probability.
The "AI Analyst" Section:
IF the Phishing Probability is > 50% OR a Typosquatting alert is found:
Call google.generativeai using the provided API Key.
Prompt Gemini to explain why the email is dangerous based on the text and the metadata.
Display the explanation in a nice box (st.info or st.warning).
Important Instructions:
Handle errors gracefully (e.g., if the model file isn't found, tell the user to run training.py first).
Ensure the directory paths for saving/loading models are consistent.
Write clean, commented code.
