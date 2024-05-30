import random
from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, validator

RAW_DATA_FOLDER = Path("raw_data")

class PredictionRow(BaseModel):
    Pregnancies: int
    Glucose: int
    BloodPressure: int
    SkinThickness: int
    Insulin: int
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int
    
    @validator("Glucose", allow_reuse=True, check_fields=False)
    def age_check(cls, v: int) -> int:
        if v >= 0 and v <= 200:
            return v
        raise ValueError("Glucose must be valid")
    
    @validator("DiabetesPedigreeFunction", allow_reuse=True, check_fields=False)
    def age_check(cls, v: float) -> float:
        if v >= 0 and v <= 2.5:
            return v
        raise ValueError("DiabetesPedigreeFunction must be in this range")


result_data = []
for _ in range(1000):
    possible_pregnancies = random.randint(1, 17)
    possible_glucose = random.randint(1, 199)
    possible_blood_pressure = random.randint(0, 122)
    possible_skin_thickness = random.randint(1, 99)
    possible_insulin = random.randint(1, 846)
    possible_bmi = random.uniform(1, 67.1)
    possible_diabetes_pedigree_function = random.uniform(0.08, 2.42)
    possible_age = random.randint(21, 81)
    result_data.append(PredictionRow(Pregnancies=possible_pregnancies, Glucose=possible_glucose, BloodPressure=possible_blood_pressure,
                            SkinThickness=possible_skin_thickness, Insulin=possible_insulin, BMI=possible_bmi, 
                            DiabetesPedigreeFunction=possible_diabetes_pedigree_function, Age=possible_age).dict())
result_df = pd.DataFrame(result_data)
current_date = datetime.now().strftime("%Y-%m-%d")
result_df.to_csv(RAW_DATA_FOLDER / f"{current_date}.csv", index=False)
