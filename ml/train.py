import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import pickle

df = pd.read_csv("faults.csv")
df = df.dropna(subset=["severity"])
df["severity"] = df["severity"].astype(int)

# encode text features as numbers
le_soc = LabelEncoder()
le_part = LabelEncoder()
le_subcat = LabelEncoder()

df["soc_enc"] = le_soc.fit_transform(df["soc"].fillna("unknown"))
df["part_enc"] = le_part.fit_transform(df["part"].fillna("unknown"))
df["subcat_enc"] = le_subcat.fit_transform(df["subcategory"].fillna("unknown"))

X = df[["part_enc", "soc_enc", "subcat_enc", "is_critical"]]
y = df["severity"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))

# save model and encoders
with open("severity_model.pkl", "w") as f:
    pass

import pickle
with open("severity_model.pkl", "wb") as f:
    pickle.dump({"model": model, "le_soc": le_soc, "le_part": le_part, "le_subcat": le_subcat}, f)

print("Model saved to severity_model.pkl")