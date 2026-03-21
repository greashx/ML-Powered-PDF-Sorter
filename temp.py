import os
import pandas as pd

base_path = "C:\\Users\\4mine\\Desktop\\FilesML"

data = []

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
                         "num_underscores": name.count('_')
                         })

df = pd.DataFrame(data)
print(df)
df.to_csv("fileData.csv", index=False)

print(f"Success! Saved {len(df)} labeled files to CSV.")
print(df['category'].value_counts())

df = pd.read_csv('fileData.csv')

print(df.head())