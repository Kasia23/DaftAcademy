from typing import Dict

from fastapi import FastAPI, Request, Response, status

from pydantic import BaseModel


app = FastAPI()
app.counter = -1

PATIENT_DICT = {}


@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.api_route('/method', methods=['get', 'post', 'delete', 'put'])
def return_method(request: Request):
    method = request.method
    return {'method': method}


class PatientRq(BaseModel):
    name: str 
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: Dict


@app.post("/patient", response_model=PatientResp)
def patient(request: PatientRq):
    'indeksy pacjentów w bazie nadawane są od numeru 1'
    app.counter += 1
    PATIENT_DICT[app.counter] = request.dict()
    return PatientResp(id=app.counter, patient=request.dict())


@app.get('/patient/{pk}')
def get_patient(pk: int, response: Response):
    patient = PATIENT_DICT.get(pk)
    if not patient:
        response.status_code = status.HTTP_204_NO_CONTENT
        patient = {'message': f'Nie znaleziono pacjenta o indeksie {pk}'}
    return patient