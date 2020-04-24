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

app.next_patient_id = 0
app.patients = {}
app.sesions = {}
app.secret_key = 'secret34222hahahAKakkaLSLSOPJDOJFFFF!123#B?P'  # 64 characters 'secret' key
app.users = {"trudnY": "PaC13Nt"}

MESSAGE_UNAUTHORIZED = "Log in to access this page."


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


def check_cookie(session_token: str = Cookie(None)):
    if session_token not in app.sessions:
        session_token = None
    return session_token


@app.get("/welcome")
def welcome(request: Request, response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    username = app.sessions[session_token]
    return templates.TemplateResponse("welcome.html", {"request": request, "user": username})


def login_check_cred(credentials: HTTPBasicCredentials = Depends(security)):
    correct = False
    for username, password in app.users.items():
        correct_username = secrets.compare_digest(credentials.username, username)
        correct_password = secrets.compare_digest(credentials.password, password)
        if (correct_username and correct_password):
            correct = True
    if not correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    session_token = sha256(
        bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding='utf8')).hexdigest()
    app.sessions[session_token] = credentials.username
    return session_token


@app.post("/login")
def login(response: Response, session_token: str = Depends(login_check_cred)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/welcome"
    response.set_cookie(key="session_token", value=session_token)


@app.post("/logout")
def logout(response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    app.sessions.pop(session_token)


class PatientRq(BaseModel):
    name: str
    surname: str


@app.post("/patient")
def add_patient(response: Response, rq: PatientRq, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    pid = f"id_{app.next_patient_id}"
    app.patients[pid] = rq.dict()
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{pid}"
    app.next_patient_id += 1


@app.get("/patient")
def get_all_patients(response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    if len(app.patients) != 0:
        return app.patients
    response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/patient/{pid}")
def get_patient(pid: str, response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    if pid in app.patients:
        return app.patients[pid]
    response.status_code = status.HTTP_204_NO_CONTENT


@app.delete("/patient/{pid}")
def remove_patient(pid: str, response: Response, session_token: str = Depends(check_cookie)):
    if session_token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return MESSAGE_UNAUTHORIZED
    app.patients.pop(pid, None)
    response.status_code = status.HTTP_204_NO_CONTENT
