from fastapi.testclient import TestClient
from fastapi import status, Request

from main import app

import pytest

client = TestClient(app)

TEST_PATIENT_LIST = [
    (0, 'Pan', 'Demia'),
    (1, 'Anna', 'Kwarant'),
    (2, 'Błękit', 'Żółtko')
]

class MockPatientResponse:
    @staticmethod
    def patient_json(pk):
        return {
            'name': TEST_PATIENT_LIST[pk][1],
            'surename': TEST_PATIENT_LIST[pk][2]
        }


class TestMainPage:
    def test_hello_world(self):
        response = client.get('/')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}


class TestMethodEndpoint:    
    def test_return_get_method(self, request: Request):
        response = client.get('/method')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'method': 'GET'}

    def test_return_post_method(self, request: Request):
        response = client.post('/method')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'method': 'POST'}
        
    def test_return_put_method(self, request: Request):
        response = client.put('/method')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'method': 'PUT'}
        
    def test_return_delete_method(self, request: Request):
        response = client.delete('/method')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'method': 'DELETE'}


class TestGetPatient:
    @pytest.mark.parametrize("pk", [-5, 0, 1, 2])
    def test_get_patient(self, pk):
        response = client.get(f'/patient/{pk}')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.json() == {'message': f'Nie znaleziono pacjenta o indeksie {pk}'}


class TestPostAndGetPatient:
    @pytest.mark.parametrize('id,name,surename', TEST_PATIENT_LIST)
    def test_patient(self, id, name, surename):
        post_json={'name': f'{name}', 'surename': f'{surename}'}
        response = client.post("/patient", json=post_json)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": id, "patient": post_json}


    @pytest.mark.parametrize("pk", [0, 1, 2])
    def test_get_patient(self, pk):
        response = client.get(f'/patient/{pk}')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == MockPatientResponse.patient_json(pk)