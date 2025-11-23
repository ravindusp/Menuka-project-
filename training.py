import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from utils import clean_text

def create_synthetic_data():
    """
    Creates a synthetic dataset of phishing and legitimate emails.
    """
    data = [
        # --- Phishing Examples (20) ---
        {"text": "Urgent: Your PayPal account has been restricted. Click here to verify now.", "label": 1},
        {"text": "Dear Customer, Your Apple ID has been locked due to suspicious activity. Login to unlock.", "label": 1},
        {"text": "Netflix Payment Failed. Update your payment details immediately to avoid suspension.", "label": 1},
        {"text": "Microsoft Security Alert: Unusual sign-in attempt detected. Verify your account.", "label": 1},
        {"text": "Amazon: You have won a $500 gift card! Claim it now by clicking the link.", "label": 1},
        {"text": "Bank of America: Your account has been temporarily suspended. Please update your info.", "label": 1},
        {"text": "IRS Notification: You have a pending tax refund. Click here to claim.", "label": 1},
        {"text": "Google Drive: You have shared a file with an unknown user. Review access now.", "label": 1},
        {"text": "Wells Fargo: Unauthorized transaction detected. Login to cancel.", "label": 1},
        {"text": "Facebook: Someone tried to reset your password. Was this you?", "label": 1},
        {"text": "DHL Delivery: Your package is on hold. Pay shipping fees to release.", "label": 1},
        {"text": "LinkedIn: You appeared in 5 searches this week. See who is looking.", "label": 1},
        {"text": "Dropbox: Your storage is full. Upgrade now to avoid data loss.", "label": 1},
        {"text": "Zoom: You have a missed meeting invitation. Click to join.", "label": 1},
        {"text": "HR Dept: Urgent payroll update required. Please review attached doc.", "label": 1},
        {"text": "IT Support: Password expiration notice. Change your password immediately.", "label": 1},
        {"text": "CEO: I need you to buy some gift cards for a client. Urgent.", "label": 1},
        {"text": "Verify your email address to continue using our services.", "label": 1},
        {"text": "Final Notice: Your account will be deleted in 24 hours.", "label": 1},
        {"text": "Congratulations! You've been selected for a special offer.", "label": 1},

        # --- Legitimate Examples (Original 20) ---
        {"text": "Meeting agenda for next week's team sync.", "label": 0},
        {"text": "Your Amazon order #12345 has shipped.", "label": 0},
        {"text": "Google Calendar reminder: Dentist appointment tomorrow at 10 AM.", "label": 0},
        {"text": "Invoice for your recent purchase attached.", "label": 0},
        {"text": "Project update: We are on track for the Q3 release.", "label": 0},
        {"text": "Happy Birthday! Hope you have a great day.", "label": 0},
        {"text": "Can we reschedule our call to 3 PM?", "label": 0},
        {"text": "Attached is the report you requested.", "label": 0},
        {"text": "Invitation: Company holiday party.", "label": 0},
        {"text": "Your Netflix subscription has been renewed.", "label": 0},
        {"text": "Feedback on the latest design mockups.", "label": 0},
        {"text": "Please review the attached contract.", "label": 0},
        {"text": "Flight confirmation for your trip to New York.", "label": 0},
        {"text": "LinkedIn: New connection request from John Doe.", "label": 0},
        {"text": "Weekly newsletter: Top tech trends of 2024.", "label": 0},
        {"text": "Reminder: Submit your expense report by Friday.", "label": 0},
        {"text": "Photos from the weekend trip.", "label": 0},
        {"text": "Can you pick up milk on your way home?", "label": 0},
        {"text": "Thank you for your application. We will be in touch.", "label": 0},
        {"text": "Your monthly bank statement is ready to view.", "label": 0},

        # --- New Legitimate Examples (Expanded 30+) ---
        {"text": "Hey, are we still on for lunch today?", "label": 0},
        {"text": "Can you send me the slide deck from the presentation?", "label": 0},
        {"text": "Checking in to see how you are doing.", "label": 0},
        {"text": "Don't forget to walk the dog.", "label": 0},
        {"text": "The game night is scheduled for Saturday at 7 PM.", "label": 0},
        {"text": "Here is the recipe I told you about.", "label": 0},
        {"text": "Did you see the latest episode of that show?", "label": 0},
        {"text": "Confirming our appointment for next Tuesday.", "label": 0},
        {"text": "The package arrived safely, thanks!", "label": 0},
        {"text": "Let me know if you need any help with the move.", "label": 0},
        {"text": "Great job on the presentation yesterday!", "label": 0},
        {"text": "The weather looks good for the picnic.", "label": 0},
        {"text": "Please find the meeting minutes attached.", "label": 0},
        {"text": "Can you review this code when you have a moment?", "label": 0},
        {"text": "Happy Anniversary! Wishing you both the best.", "label": 0},
        {"text": "The kids' school play is this Friday.", "label": 0},
        {"text": "Just wanted to say hi and catch up.", "label": 0},
        {"text": "Reminder: Doctor's appointment at 2 PM.", "label": 0},
        {"text": "The electric bill is due on the 15th.", "label": 0},
        {"text": "I'll be running a bit late, see you soon.", "label": 0},
        {"text": "Let's brainstorm ideas for the marketing campaign.", "label": 0},
        {"text": "Could you please sign the document?", "label": 0},
        {"text": "The tickets for the concert are booked.", "label": 0},
        {"text": "Thanks for the gift, I really love it.", "label": 0},
        {"text": "Can you share the wifi password?", "label": 0},
        {"text": "The plumber is coming tomorrow morning.", "label": 0},
        {"text": "Looking forward to seeing you at the reunion.", "label": 0},
        {"text": "Please confirm your attendance by replying to this email.", "label": 0},
        {"text": "Here are the photos from the party.", "label": 0},
        {"text": "Let's schedule a call to discuss the project details.", "label": 0},
        {"text": "Information regarding your account settings update.", "label": 0},
        {"text": "Your support ticket #999 has been resolved.", "label": 0},
        {"text": "Welcome to our newsletter! Here is what you missed.", "label": 0},
    ]

    df = pd.DataFrame(data)
    df['clean_text'] = df['text'].apply(clean_text)
    return df

def train_model():
    """
    Trains the Phishing Detection Model and saves it.
    """
    print("Generating synthetic data...")
    df = create_synthetic_data()

    X = df['clean_text']
    y = df['label']

    print("Building pipeline...")
    # Pipeline: TF-IDF Vectorizer -> LightGBM Classifier
    # Tuning min_child_samples to handle small dataset
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000)),
        ('clf', LGBMClassifier(random_state=42, verbose=-1, min_child_samples=5))
    ])

    print("Training model...")
    pipeline.fit(X, y)

    # Evaluate on the training set (just for sanity check)
    y_pred = pipeline.predict(X)
    acc = accuracy_score(y, y_pred)
    print(f"Training Accuracy: {acc:.4f}")
    print("\nClassification Report:\n")
    print(classification_report(y, y_pred))

    # Save the model
    os.makedirs("models", exist_ok=True)
    model_path = os.path.join("models", "phishing_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

    return pipeline

if __name__ == "__main__":
    train_model()
