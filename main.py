from typing import Dict

from fastapi import FastAPI, Request, Response, status

from pydantic import BaseModel


app = FastAPI()
app.counter = -1
app.patient_dict = {}


@app.get('/')
def hello_world():
    return {'message': 'Hello World during the coronavirus pandemic!'}


@app.api_route('/method', methods=['get', 'post', 'delete', 'put'])
def return_method(request: Request):
    return {'method': request.method}


class PatientRq(BaseModel):
    name: str 
    surename: str


class PatientResp(BaseModel):
    id: int
    patient: PatientRq


@app.post("/patient", response_model=PatientResp)
def patient(rq: PatientRq):
    'indeksy pacjentów w bazie nadawane są od numeru 0'
    app.counter += 1
    app.patient_dict[app.counter] = rq
    return PatientResp(id=app.counter, patient=rq)


@app.get('/patient/{pk}')
def get_patient(pk: int, response: Response):
    patient = app.patient_dict.get(pk)
    if not patient:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {'message': f'Nie znaleziono pacjenta o indeksie {pk}'}
    return patient
