from joblib import load
import pandas as pd
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel
from typing import Union

class PredictionFeatures(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool


app = FastAPI(
    title='The getaround API',
    description=''' This API allows user to predict rental prices based on car characteristics through the \'/predict\' endpoint through the POST method.

    Here is an example of request through a bash terminal :

    curl -X POST <API URL> \
    -H "Content-Type: application/json" \
    -d '{"model_key":"Renault","mileage":77334,"engine_power":256,"fuel":"diesel","paint_color":"black","car_type":"coupe","private_parking_available":true,"has_gps":false,"has_air_conditioning":true,"automatic_car":false,"has_getaround_connect":false,"has_speed_regulator":true,"winter_tires":false}'

    This should return :

    The predicted price is: 190.02305595828443

    ''',
    openapi_tags={
        'name': '/predict',
        'description': 'Use pre-trained ML model (on getaround provided database) to predict rental prices based on car characteristics'
    }
)


@app.get('/')
async def root():
    message = '''If you are looking to estimate car prices from their features, you are in the right place.'''
    return message

@app.post('/predict')
async def predict(input_data: PredictionFeatures, request: Request):
    ''' Return predicted price according to car features'''

    body = await request.json()
    print(f"Received request body: {body}")

    # Log or debug Pydantic-validated input_data
    print(f"Parsed input data (Pydantic): {input_data.dict()}")

    try:
        predictor = load('./model/model_reg.pkl')
        transformer = load('./model/transformer.pkl')
        user_data = pd.DataFrame([input_data.dict()])

        print(f"Data prepared for transformation: {user_data}")

        X = transformer.transform(user_data)
        print(f"Transformed data: {X}")

        X_pred = predictor.predict(X)
        print(f"Prediction: {X_pred}")

        return {'The predicted price is': X_pred[0]}
    
    except Exception as e:
        print(f"Error during processing: {e}")
        return {"error": str(e)}


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)