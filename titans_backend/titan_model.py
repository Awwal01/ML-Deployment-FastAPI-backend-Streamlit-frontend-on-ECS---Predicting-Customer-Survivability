
import pandas as pd
import numpy as np
import json

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import customTransformer
from customTransformer import age_sex_transformer

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(debug=True)


@app.get("/")
async def root():
    return {"message": "hello world"}


class PassengerDetails(BaseModel):
    Pclass: int
    Sex: str
    Age: int


def predict(Pclass=3, Sex='female', Age=18.0):

    model_file = "./modelc.pkl"
    model = joblib.load(model_file)

    data = [[Pclass, Sex, Age]]
    df4 = pd.DataFrame(data, columns=["Pclass", "Sex", "Age"])
    forecast = model.predict(df4)
    if forecast == 0:
        return "Seems they didn't make it"
    else:
        return "Survived"

@app.post("/predict_test")
async def get_predict(data: PassengerDetails):

    input_data = data.json()
    recieved = json.loads(input_data)
    Pclass = recieved["Pclass"]
    Sex = recieved["Sex"]
    Age = recieved["Age"]
    return {'Age': Age, "Sex": Sex, 'Pclass':Pclass}

@app.post("/predict")
async def get_predict(data: PassengerDetails):

    input_data = data.json()
    recieved = json.loads(input_data)
    Pclass = recieved["Pclass"]
    Sex = recieved["Sex"]
    Age = recieved["Age"]

    forecast = predict(Pclass, Sex, Age)
    return {"Survival status": forecast}
