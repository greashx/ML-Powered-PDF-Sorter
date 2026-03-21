import os
import pandas as pd
import fitz  # PyMuPDF

base_path = "C:\\Users\\4mine\\Desktop\\FilesML"

data = []

def get_page_count(file_path):
    try:
        doc = fitz.open(file_path)
        count = doc.page_count
        doc.close()
        return count
    except:
        return 1  # Default to 1 if the PDF is corrupted or encrypted

for root, dirs, files in os.walk(base_path):

    for name in files:
        print(f"Found file: {name}")
        if name.endswith(".pdf"):
            category = root.split("\\")[-1]

            data.append({"filename": name, "category": category,
                         "size": os.path.getsize(os.path.join(root, name)),
                         "has_numbers": any(char.isdigit() for char in name),
                         "name_length": len(name),
                         "num_spaces": name.count(' '),
                         "num_underscores": name.count('_'),
                         "word_count": len(name.replace('_', ' ').split()),
                         "digit_ratio": sum(c.isdigit() for c in name) / len(name),
                         "page_count": get_page_count(os.path.join(root, name))
                         })

df = pd.DataFrame(data)
# another feature for exercise files
academic_keywords = ['week', 'lec', 'slide', 'ch', 'assgn', 'prob', 'sol', 'ex', 'mock', 'homework', 'hw', 'exercise']
df['has_keyword'] = df['filename'].str.lower().apply(lambda x: 1 if any(k in x for k in academic_keywords) else 0)

personal_keywords = ['personal', 'private', 'id', 'passport', 'original', 'pass', 'visa', 'card', 'invoice' ]
df['is_personal'] = df['filename'].str.lower().apply(lambda x: 1 if any(k in x for k in personal_keywords) else 0)
special_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=", "{", "}", "[", "]", "|", ";", ":", "'", '"']
# This counts how many special characters are in each filename
df['special_char_count'] = df['filename'].apply(lambda x: sum(1 for char in x if char in special_chars))
print(df)
df.to_csv("fileData.csv", index=False)

print(f"Success! Saved {len(df)} labeled files to CSV.")
print(df['category'].value_counts())

df = pd.read_csv('fileData.csv')

print(df.head())