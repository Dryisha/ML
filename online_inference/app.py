from typing import Dict

from fastapi import FastAPI

from src.constants import MODEL_NAME
from src.data_model import PredictionRow
from src.model import PredictionModel

app = FastAPI()
prediction_model = PredictionModel(MODEL_NAME)


@app.post("/predict")
def predict_function(data_model: PredictionRow) -> Dict[str, str]:
    predict = prediction_model.predict(data_model)
    return {"prediction": predict}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)