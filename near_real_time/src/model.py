import pandas as pd
import pickle
from src.constants import BLOOD_NAME, NOT_BLOOD_NAME, BLOOD_LABEL
from sklearn.pipeline import Pipeline
from src.data_model import BloodDonationRow


class PredictionModel:
    def __init__(self, path_to_file: str) -> None:
        with open(path_to_file, "rb") as f:
            self.model: Pipeline = pickle.load(f)

    def predict(self, data_model: BloodDonationRow) -> str:
        if isinstance(data_model, list):
            data_model = data_model[0]
        prdct_row = data_model.dict()
        series = pd.Series(prdct_row)
        df = pd.DataFrame(data=[series])
        prediction = self.model.predict(df)
        return BLOOD_NAME if prediction[0] == BLOOD_LABEL else NOT_BLOOD_NAME