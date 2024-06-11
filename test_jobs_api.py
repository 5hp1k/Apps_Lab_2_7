import pytest
import requests
from models import Job, engine, Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000/api/jobs'

Session = sessionmaker(bind=engine)


@pytest.fixture(scope='module')
def setup_db():
    # Создание тестовой базы данных
    Base.metadata.create_all(engine)
    db_session = Session()

    # Добавление тестовых данных
    job1 = Job(id=1, job="Test Job 1", team_leader=1, work_size=5, collaborators="2,3", start_date=datetime.strptime(
        "2023-01-01", '%Y-%m-%d'), end_date=datetime.strptime("2023-12-31", '%Y-%m-%d'), is_finished=False)
    job2 = Job(id=2, job="Test Job 2", team_leader=2, work_size=10, collaborators="1,3", start_date=datetime.strptime(
        "2023-01-01", '%Y-%m-%d'), end_date=datetime.strptime("2023-12-31", '%Y-%m-%d'), is_finished=True)

    db_session.add(job1)
    db_session.add(job2)
    db_session.commit()

    yield

    # Очистка базы данных после тестов
    Base.metadata.drop_all(engine)
    db_session.close()


def test_get_all_jobs(setup_db):
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_job_by_id(setup_db):
    response = requests.get(f'{BASE_URL}/1')
    assert response.status_code == 200
    job = response.json()
    assert job['id'] == 1
    assert job['job'] == "Test Job 1"


def test_get_job_by_invalid_id(setup_db):
    response = requests.get(f'{BASE_URL}/999')
    assert response.status_code == 404
    assert response.json()['error'] == 'Job not found'


def test_add_job(setup_db):
    new_job = {
        'id': 3,
        'job': "New Test Job",
        'team_leader': 3,
        'work_size': 8,
        'collaborators': "1,2",
        'start_date': "2023-02-01",
        'end_date': "2023-12-31",
        'is_finished': False
    }
    response = requests.post(BASE_URL, json=new_job)
    assert response.status_code == 201
    assert response.json()['success'] == 'Job added'

    # Проверка, что работа действительно добавлена
    response = requests.get(f'{BASE_URL}/3')
    assert response.status_code == 200
    job = response.json()
    assert job['id'] == 3
    assert job['job'] == "New Test Job"


def test_add_job_with_existing_id(setup_db):
    # Некорректный запрос: ID уже существует
    new_job = {
        'id': 1,
        'job': "Duplicate ID Job",
        'team_leader': 3,
        'work_size': 8,
        'collaborators': "1,2",
        'start_date': "2023-02-01",
        'end_date': "2023-12-31",
        'is_finished': False
    }
    response = requests.post(BASE_URL, json=new_job)
    assert response.status_code == 400
    assert response.json()['error'] == 'Id already exists'


def test_add_job_with_invalid_data(setup_db):
    # Некорректный запрос: нет ID
    new_job = {
        'job': "Missing ID Job",
        'team_leader': 3,
        'work_size': 8,
        'collaborators': "1,2",
        'start_date': "2023-02-01",
        'end_date': "2023-12-31",
        'is_finished': False
    }
    response = requests.post(BASE_URL, json=new_job)
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid input'


def test_delete_job(setup_db):
    response = requests.delete(f'{BASE_URL}/2')
    assert response.status_code == 200
    assert response.json()['success'] == 'Job deleted'

    # Проверка, что работа действительно удалена
    response = requests.get(BASE_URL)
    jobs = response.json()
    assert len(jobs) == 2  # одна работа была удалена


def test_delete_job_invalid_id(setup_db):
    response = requests.delete(f'{BASE_URL}/999')
    assert response.status_code == 404
    assert response.json()['error'] == 'Job not found'


def test_edit_job(setup_db):
    updated_job = {
        'job': "Updated Test Job 1",
        'team_leader': 1,
        'work_size': 15,
        'collaborators': "2,3",
        'start_date': "2023-01-01",
        'end_date': "2023-12-31",
        'is_finished': False
    }
    response = requests.put(f'{BASE_URL}/1', json=updated_job)
    assert response.status_code == 200
    assert response.json()['success'] == 'Job updated'

    # Проверка, что работа действительно обновлена
    response = requests.get(f'{BASE_URL}/1')
    job = response.json()
    assert job['job'] == "Updated Test Job 1"
    assert job['work_size'] == 15


def test_edit_job_invalid_id(setup_db):
    updated_job = {
        'job': "Non-existent Job",
        'team_leader': 1,
        'work_size': 15,
        'collaborators': "2,3",
        'start_date': "2023-01-01",
        'end_date': "2023-12-31",
        'is_finished': False
    }
    response = requests.put(f'{BASE_URL}/999', json=updated_job)
    assert response.status_code == 404
    assert response.json()['error'] == 'Job not found'


def test_edit_job_invalid_data(setup_db):
    # Некорректный запрос: нет данных
    updated_job = {}
    response = requests.put(f'{BASE_URL}/1', json=updated_job)
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid input'
