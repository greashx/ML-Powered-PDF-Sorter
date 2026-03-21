import os
import shutil
import pandas as pd
import joblib
import fitz  # PyMuPDF
from datetime import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
SOURCE_DIR = "C:\\Users\\.\\Downloads"  # Change this to your actual path
MODEL_PATH = "file_classifier_model.pkl"
ENCODER_PATH = "label_encoder.pkl"
LOG_FILE = os.path.join(SOURCE_DIR, "classification_log.csv")

# Load the model
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
        # Extract text from first 3 pages to estimate word count
        text = ""
        for page in doc[:3]:
            text += page.get_text()
        word_count = len(text.split())
        doc.close()

        size_mb = stats.st_size / (1024 * 1024)

        # Construct the feature dictionary exactly as trained
        features = {
            'size': stats.st_size,
            'has_numbers': int(any(char.isdigit() for char in fname)),
            'name_length': len(fname),
            'num_spaces': fname.count(' '),
            'num_underscores': fname.count('_'),
            'word_count': word_count,
            'digit_ratio': sum(c.isdigit() for c in fname) / len(fname) if len(fname) > 0 else 0,
            'page_count': page_count,
            'has_keyword': int(any(k in fname.lower() for k in ['report', 'final', 'draft'])),
            'is_personal': int(any(k in fname.lower() for k in ['cv', 'resume', 'tax', 'passport'])),
            'special_char_count': sum(not c.isalnum() and c not in [' ', '.', '_'] for c in fname),
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
        # Note: 'is_large' was likely the 12th feature in your set.
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

    for filename in os.listdir(SOURCE_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(SOURCE_DIR, filename)

            # Feature Extraction
            X_new = get_pdf_features(file_path)
            if X_new is None: continue

            # Prediction
            pred_encoded = model.predict(X_new)
            category = le.inverse_transform(pred_encoded)[0]

            # File Movement
            dest_folder = os.path.join(SOURCE_DIR, category)
            os.makedirs(dest_folder, exist_ok=True)

            try:
                shutil.move(file_path, os.path.join(dest_folder, filename))
                status = "Moved"
                print(f"✅ [{category}] {filename}")
            except Exception as e:
                status = f"Error: {e}"
                print(f"❌ Failed to move {filename}")

            # Breadcrumb Logging
            log_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filename, category, status]])
            log_data.to_csv(LOG_FILE, mode='a', header=False, index=False)
            files_processed += 1

    print(f"\nDone! Processed {files_processed} files. Check {LOG_FILE} for details.")


if __name__ == "__main__":
    run_cleanup()




