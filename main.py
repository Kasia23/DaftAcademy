from typing import Dict
import secrets

from fastapi import FastAPI, Request, Response, status, Cookie, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pydantic import BaseModel

app = FastAPI()
app.counter = -1
app.patient_dict = {}
security = HTTPBasic()


@app.get('/')
def hello_world():
    return {'message': 'Hello World during the coronavirus pandemic!'}


@app.get('/welcome')
def welcome():
    return {'message': 'Welcome during the coronavirus pandemic!'}


def create_cookie():
    session_token = 'token'
    response.set_cookie(key="session_token", value=session_token)


@app.post("/login")
def login_and_basic_auth(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    response.status_code = 301
    return welcome()


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
