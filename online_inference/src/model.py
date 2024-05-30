import pickle

import pandas as pd
from sklearn.pipeline import Pipeline

from src.constants import BLOOD_LABEL, BLOOD_NAME, NOT_BLOOD_NAME
from src.data_model import BloodDonationRow


class PredictionModel:

    def __init__(self, path_to_file: str) -> None:
        with open(path_to_file, "rb") as f:
            self.model: Pipeline = pickle.load(f)

    def predict(self, data_model: BloodDonationRow) -> str:
        prediction_row = data_model.dict()
        series = pd.Series(prediction_row)
        df = pd.DataFrame(data=[series])
        prediction = self.model.predict(df)
        return BLOOD_NAME if prediction[0] == BLOOD_LABEL else NOT_BLOOD_NAME
