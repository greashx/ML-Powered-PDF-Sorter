import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib




le = LabelEncoder()
df = pd.read_csv("fileData.csv")
# Encode the category column to numerical values
df['Category_Encoded'] = le.fit_transform(df['category'])
df.to_csv('fileData_Encoded.csv', index=False)

# 5MB is roughly 5,000,000 bytes.
# You can check your actual Book sizes to see if this threshold fits!
df['is_large'] = (df['size'] > 3500000).astype(int)

# Drop the text category and the name (the model can't 'read' names yet)
X = df[['size',
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
        'page_count']]
y = df['Category_Encoded']

# test_size=0.2 means 20% goes to the 'Exam' pile
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# Create and train the Decision Tree Classifier
# Limit the tree to 3 levels of questions
"""
model = DecisionTreeClassifier(max_depth=5,
                               min_samples_leaf=5,
                               class_weight='balanced',
                               random_state=42,
                               )
                               """
model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
# The model 'learns' here

model.fit(X_train, y_train)

# The model takes the test features and gives us its guesses
predictions = model.predict(X_test)


# We use target_names so the report shows "Books" instead of "0"
print(classification_report(y_test, predictions, target_names=le.classes_))

ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, display_labels=le.classes_)
plt.show()

# Save the trained model
joblib.dump(model, 'file_classifier_model.pkl')

# Save the label encoder (CRITICAL for decoding the numbers later)
joblib.dump(le, 'label_encoder.pkl')