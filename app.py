import sys
import os
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.responses import (RedirectResponse, Response)
import uvicorn
from textSummarizer.pipeline.prediction import PredictionPipeline

text: str = "What is Text Summarization?"

app = FastAPI()

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def training():
    try:
        os.system("python main.py")
        return Response("Training successful !!")
    except Exception as e:
        return Response(f"Error occurred! {e}")
    
@app.post("/predict")
async def predict_route(text):
    try:
        prediction_pipeline = PredictionPipeline()
        summary = prediction_pipeline.predict(text)
        return summary
    except Exception as e:
        raise e
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7070)