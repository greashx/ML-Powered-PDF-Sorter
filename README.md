
#  AI-Powered PDF Sorter

An automated file organization system that uses **Machine Learning (Random Forest)** to classify and sort PDFs into specific folders based on their metadata and content features.

---
##  How it Works:

Instead of relying on simple name-matching, this tool analyzes **12 distinct features** from each PDF to determine its category:

* **Physical Stats:** File size, page count, and estimated word count.

* **Naming Patterns:** Digit-to-letter ratio, special characters, and underscores.

* **Contextual Keywords:** Scans for academic and personal identifiers within the text.

---

##  Project Structure

|  File                  |  Description                                                                          |
| :--------------------- | :------------------------------------------------------------------------------------ |
| **`trainingModel.py`** |  The training script. Processes labeled data and exports the trained model.           |
| **`organize_pdfs.py`** | The deployment script. Scans folders, extracts features, and moves files.             |
| **`trainingData.py`**  |  Data collection script used to build the initial training dataset (`fileData.csv`).  |
| **`PDF Sorter.bat`**   |  A one-click Windows batch file to run the sorter in its virtual environment.         |

---

##  Setup & Installation

1. **Clone the repository** to your local machine.

2. **Create a Virtual Environment:**

```bash

python -m venv .venv

source .venv/Scripts/activate # On Windows: .venv\Scripts\activate

```

3. **Install Dependencies**:

```bash

pip install pandas scikit-learn pymupdf joblib

```

4. **Configure Paths**: Open `organize_pdfs.py` and update the `SOURCE_DIR` to the folder you want to keep clean (e.g., your Downloads folder).

---

##  Usage

### 1. Training the Model

If you want to **re-train** the model with your own data:

1. Place labeled PDFs into category-named folders.
2. Run `python trainingData.py` to generate the CSV.
3. Run `python trainingModel.py` to train and save `file_classifier_model.pkl`.

### 2. Sorting Files

Simply double-click **`PDF Sorter.bat`** (make sure to change the directory inside of it to the project directory). 
The script will:
- Scan for new PDFs.
- Predict the category (Books, HWs, Lectures, PersonalDocs, etc.).
- Move the file to the corresponding folder.
- **Confidence Guardrail:** Files with low prediction confidence are moved to a `To_Review` folder for safety.

## Logging

Every action is recorded in `classification_log.csv`, allowing you to track where your files went and check the model's confidence scores.