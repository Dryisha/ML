import pickle
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from src.constants import MODEL_NAME

EXPERIMENT_NAME = "BloodLR1"

FILEPATH = "data/transfusion.csv"

COLS = ["recency_months", "frequency_times", "monetary_cc_blood", "time_months", "donated_blood"]
NUMERIC_COLS = ["recency_months", "frequency_times", "monetary_cc_blood", "time_months"]
TARGET = "donated_blood"

df = pd.read_csv(FILEPATH)
df = df.loc[:, COLS]
y = df[TARGET]

train_X, test_X, train_y, test_y = train_test_split(
            df.drop(columns=[TARGET]), y, test_size=0.3, random_state=42,
        shuffle=True, stratify=y
)

transforms = ColumnTransformer(
    [
        ("normalizer", Pipeline(
            [
                ("impute", SimpleImputer(strategy="mean")),
                ("norm", StandardScaler())
            ]
        ), NUMERIC_COLS)
    ]
)

pipeline = Pipeline([
    ("transforms", transforms),
    ("model", LogisticRegression(n_jobs=-1))
])

pipeline.fit(train_X, train_y)
pred = pipeline.predict(test_X)
print("accuracy_score", accuracy_score(test_y, pred))


with open(MODEL_NAME, "wb") as f:
    pickle.dump(pipeline, f)
