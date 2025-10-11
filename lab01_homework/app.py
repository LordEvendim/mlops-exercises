from fastapi import FastAPI
from api.models.sentiment import PredictRequest, PredictResponse
from interference import load_models, predict_sentiment

app = FastAPI()
lr_model, st_model = load_models()


@app.get("/")
def welcome_root():
    return {"message": "Welcome to the ML API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    # print("getting prediction request")
    prediction = predict_sentiment(lr_model, st_model, request.text)

    return PredictResponse(prediction=prediction)
