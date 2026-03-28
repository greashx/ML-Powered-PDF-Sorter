import os
import shutil
import pandas as pd
import joblib
import fitz  # PyMuPDF
from datetime import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
SOURCE_DIR = "C:\\Users\\4mine\\Downloads"  # Change this to your actual path
MODEL_PATH = "file_classifier_model.pkl" # Path to the trained model
ENCODER_PATH = "label_encoder.pkl" # Path to the label encoder
LOG_FILE = os.path.join(SOURCE_DIR, "classification_log.csv")

# Load the model and label encoder
model = joblib.load(MODEL_PATH)
le = joblib.load(ENCODER_PATH)


# ==========================================
# 2. FEATURE EXTRACTION (The 12-Feature Logic)
# ==========================================
def get_pdf_features(filepath):
    """Calculates the 12 specific features for a given PDF."""
    try:
        stats = os.stat(filepath)
        fname = os.path.basename(filepath)



        # Open PDF to get page and word counts
        doc = fitz.open(filepath)
        page_count = len(doc)
        """
        # Extract text from first 3 pages to estimate word count
        text = ""
        for page in doc[:3]:
            text += page.get_text()
        word_count = len(text.split())
        doc.close()
        """


        size_mb = stats.st_size / (1024 * 1024)

        # Construct the feature dictionary exactly as trained
        features = {
            'size': stats.st_size,
            'has_numbers': int(any(char.isdigit() for char in fname)),
            'name_length': len(fname),
            'num_spaces': fname.count(' '),
            'num_underscores': fname.count('_'),
            "word_count": len(fname.replace('_', ' ').split()),
            'digit_ratio': sum(c.isdigit() for c in fname) / len(fname) if len(fname) > 0 else 0,
            'page_count': page_count,
            'has_keyword': int(any(k in fname.lower() for k in ['week', 'lec', 'slide', 'ch', 'assgn', 'prob', 'sol', 'ex', 'mock', 'homework', 'hw', 'exercise'])),
            'is_personal': int(any(k in fname.lower() for k in ['personal', 'private', 'id', 'passport', 'original', 'pass', 'visa', 'card', 'invoice' ])),
            'special_char_count': int(any(k in fname.lower() for k in ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=", "{", "}", "[", "]", "|", ";", ":", "'", '"'])),
            'is_large': 1 if size_mb > 3.5 else 0
        }

        # Ensure columns are in the EXACT order the model expects
        feature_order = [
        'size',
        'name_length',
        'has_numbers',
        'num_spaces',
        'num_underscores',
        'word_count',
        'digit_ratio',
        'is_large',
        'has_keyword',
        'is_personal',
        'special_char_count',
        'page_count'
        ]
        # We return a DataFrame with one row.
        return pd.DataFrame([features])[feature_order]

    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return None


# ==========================================
# 3. THE EXECUTION ENGINE
# ==========================================
def run_cleanup():
    print(f"Starting On-Demand Scan: {SOURCE_DIR}")

    # Initialize Log if it doesn't exist
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=['Timestamp', 'File', 'Category', 'Status']).to_csv(LOG_FILE, index=False)

    files_processed = 0
    CONFIDENCE_THRESHOLD = 0.70  # You can adjust this (0.0 to 1.0)

    for filename in os.listdir(SOURCE_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(SOURCE_DIR, filename)

            # 1. Feature Extraction
            X_new = get_pdf_features(file_path)
            if X_new is None: continue

            # 2. Prediction with Probabilities
            # predict_proba returns a list of probabilities for each category
            probs = model.predict_proba(X_new)[0]
            max_prob = max(probs)

            # 3. Decision Logic
            if max_prob >= CONFIDENCE_THRESHOLD:
                # Trust the model
                pred_encoded = model.predict(X_new)
                category = le.inverse_transform(pred_encoded)[0]
                status = "Moved"
            else:
                # Model is unsure (e.g., only 30% sure)
                category = "To_Review"
                status = f"Low Confidence ({max_prob:.2f})"

            # 4. File Movement
            dest_folder = os.path.join(SOURCE_DIR, category)
            os.makedirs(dest_folder, exist_ok=True)


            try:
                shutil.move(file_path, os.path.join(dest_folder, filename))
                icon = "✅" if category != "To_Review" else "⚠️"
                print(f"{icon} [{category}] {filename} (Conf: {max_prob:.2f})")
            except Exception as e:
                status = f"Error: {e}"
                print(f"❌ Failed to move {filename}")

            # 5. Breadcrumb Logging
            log_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename, category, status]])
            log_data.to_csv(LOG_FILE, mode='a', header=False, index=False)
            files_processed += 1

    print(f"\nDone! Processed {files_processed} files.")


if __name__ == "__main__":
    run_cleanup()




