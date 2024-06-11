import pytest
import requests
from models import User, engine, Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000/api/users'

Session = sessionmaker(bind=engine)


@pytest.fixture(scope='module')
def setup_db():
    # Создание тестовой базы данных
    Base.metadata.create_all(engine)
    db_session = Session()

    # Добавление тестовых данных
    user1 = User(surname="Doe", name="John", age=30, position="Manager", speciality="IT",
                 address="123 Main St", email="john.doe@example.com", hashed_password="hashed_password_1", modified_date=datetime.now())
    user2 = User(surname="Smith", name="Alice", age=25, position="Developer", speciality="Web",
                 address="456 Elm St", email="alice.smith@example.com", hashed_password="hashed_password_2", modified_date=datetime.now())

    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    yield

    # Очистка базы данных после тестов
    Base.metadata.drop_all(engine)
    db_session.close()


def test_get_all_users(setup_db):
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_by_id(setup_db):
    response = requests.get(f'{BASE_URL}/1')
    assert response.status_code == 200
    user = response.json()
    assert user['id'] == 1
    assert user['surname'] == "Doe"


def test_get_user_by_invalid_id(setup_db):
    response = requests.get(f'{BASE_URL}/999')
    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'


def test_add_user(setup_db):
    new_user = {
        'surname': "Khan",
        'name': "Ali",
        'age': 35,
        'position': "Engineer",
        'speciality': "Electrical",
        'address': "789 Oak St",
        'email': "ali.khan@example.com",
        'hashed_password': "hashed_password_3"
    }
    response = requests.post(BASE_URL, json=new_user)
    assert response.status_code == 201
    assert response.json()['success'] == 'User added'

    # Проверка, что пользователь действительно добавлен
    response = requests.get(f'{BASE_URL}/3')
    assert response.status_code == 200
    user = response.json()
    assert user['id'] == 3
    assert user['surname'] == "Khan"


def test_add_user_with_existing_email(setup_db):
    # Некорректный запрос: email уже существует
    new_user = {
        'surname': "Doe",
        'name': "Jane",
        'age': 28,
        'position': "Designer",
        'speciality': "Graphics",
        'address': "246 Pine St",
        'email': "john.doe@example.com",
        'hashed_password': "hashed_password_4"
    }
    response = requests.post(BASE_URL, json=new_user)
    assert response.status_code == 400
    assert response.json()['error'] == 'Email already exists'


def test_delete_user(setup_db):
    response = requests.delete(f'{BASE_URL}/2')
    assert response.status_code == 200
    assert response.json()['success'] == 'User deleted'

    # Проверка, что пользователь действительно удален
    response = requests.get(BASE_URL)
    users = response.json()
    assert len(users) == 2  # один пользователь был удален


def test_delete_user_invalid_id(setup_db):
    response = requests.delete(f'{BASE_URL}/999')
    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'


def test_edit_user(setup_db):
    updated_user = {
        'surname': "Updated Smith",
        'name': "Updated Alice",
        'age': 26,
        'position': "Senior Developer",
        'speciality': "Web",
        'address': "456 Elm St",
        'email': "alice.smith@example.com",
        'hashed_password': "hashed_password_6"
    }
    response = requests.put(f'{BASE_URL}/3', json=updated_user)
    assert response.status_code == 200
    assert response.json()['success'] == 'User updated'

    # Проверка, что пользователь действительно обновлен
    response = requests.get(f'{BASE_URL}/3')
    user = response.json()
    assert user['surname'] == "Updated Smith"
    assert user['age'] == 26


def test_edit_user_invalid_id(setup_db):
    updated_user = {
        'surname': "Non-existent User",
        'name': "Non-existent User",
        'age': 30,
        'position': "Manager",
        'speciality': "IT",
        'address': "123 Main St",
        'email': "missing.user@example.com",
        'hashed_password': "hashed_password_7"
    }
    response = requests.put(f'{BASE_URL}/999', json=updated_user)
    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'


def test_edit_user_invalid_data(setup_db):
    # Некорректный запрос: нет данных
    updated_user = {}
    response = requests.put(f'{BASE_URL}/1', json=updated_user)
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid input'
