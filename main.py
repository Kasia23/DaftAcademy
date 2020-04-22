from typing import Dict
import secrets

from fastapi import FastAPI, Request, Response, status, Cookie, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse

from pydantic import BaseModel
from hashlib import sha256

from functools import wraps

app = FastAPI()
security = HTTPBasic()

app.counter = -1
app.patient_dict = {}
app.sesions = {}
app.secret_key = 'secret34222hahahAKakkaLSLSOPJDOJFFFF!123#B?P'  # 64 characters 'secret' key
app.user = {'login': 'trudnY', 'password': 'PaC13Nt'}


def token_required(func):
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        if not request.cookies.get('session_token'):
            return RedirectResponse(url='/', status_code=status.HTTP_401_UNAUTHORIZED)
        return func(request, *args, **kwargs)
    return wrapper


@app.get('/')
def hello_world():
    return {'message': 'Hello World during the coronavirus pandemic!'}


@app.get('/welcome')
@token_required
def welcome(request: Request):
    return {'message': 'Welcome!'}


@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, app.user['login'])
    correct_password = secrets.compare_digest(credentials.password, app.user['password'])

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    session_token = sha256(str.encode(f"{credentials.username}{credentials.password}{app.secret_key}")).hexdigest()
    response = RedirectResponse(url='/welcome', status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=session_token)
    return response


@app.get("/logout")
@token_required
def logout(request: Request):
    #response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response = Response()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    response.delete_cookie("session_token")
    return response


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
@token_required
def patient(request: Request, rq: PatientRq):
    'indeksy pacjentów w bazie nadawane są od numeru 0'
    app.counter += 1
    app.patient_dict[app.counter] = rq
    return PatientResp(id=app.counter, patient=rq)


@app.get('/patient/{pk}')
@token_required
def get_patient(request: Request, pk: int, response: Response):
    patient = app.patient_dict.get(pk)
    if not patient:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {'message': f'Nie znaleziono pacjenta o indeksie {pk}'}
    return patient
