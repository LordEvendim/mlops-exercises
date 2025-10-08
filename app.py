from fastapi import FastAPI
from api.models.iris import PredictRequest, PredictResponse
from interference import load_model
from sklearn.datasets import load_iris

app = FastAPI()
model = load_model()
target_names = load_iris().target_names


@app.get("/")
def welcome_root():
    return {"message": "Welcome to the ML API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    print("getting request", request)

    features = [
        request.sepal_length,
        request.sepal_width,
        request.petal_length,
        request.petal_width,
    ]
    prediction = model.predict([features])[0]

    return PredictResponse(prediction=target_names[prediction])
