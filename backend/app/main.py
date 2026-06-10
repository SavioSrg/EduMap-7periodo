"""EduMap API — FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PredictRequest, PredictResponse
from .predictor import predict

app = FastAPI(title="EduMap API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "online"}


@app.post("/predict", response_model=PredictResponse)
def post_predict(req: PredictRequest) -> PredictResponse:
    return predict(req)