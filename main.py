from typing import Dict
import secrets

from fastapi import FastAPI, Request, Response, status, Cookie, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from hashlib import sha256

from functools import wraps

app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

app.counter = -1
app.patient_dict = {}
app.sessions = []
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
def welcome(request: Request, session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    return templates.TemplateResponse('welcome.html', {'request': request, 'user': app.user['login']})


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
    app.sessions.append(session_token)
    response = RedirectResponse(url='/welcome', status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=session_token)
    return response


@app.post("/logout")
def logout(session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    response = Response()
    response.delete_cookie("session_token")
    response.headers["Location"] = "/"
    response.status_code = status.HTTP_302_FOUND
    return response


@app.api_route('/method', methods=['get', 'post', 'delete', 'put'])
def return_method(request: Request):
    return {'method': request.method}


class PatientRq(BaseModel):
    name: str
    surname: str


class PatientResp(BaseModel):
    id: int
    patient: PatientRq


@app.post("/patient", response_model=PatientResp)
def patient(rq: PatientRq, response: Response, session_token: str = Cookie(None)):
    'indeksy pacjentów w bazie nadawane są od numeru 0'
    if session_token not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    app.counter += 1
    app.patient_dict[app.counter] = rq
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{app.counter}"
    return PatientResp(id=app.counter, patient=rq)


@app.get("/patient")
def patient(session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    return app.patient_dict


@app.get('/patient/{pk}')
def get_patient(pk: int, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    patient = app.patient_dict.get(pk)
    if not patient:
        response.status_code = status.HTTP_204_NO_CONTENT
    return patient


@app.delete('/patient/{pk}')
def get_patient(pk: int, session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    response = Response()
    app.patient_dict.pop(pk, None)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
