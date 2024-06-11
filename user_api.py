from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import sessionmaker
from models import User, engine


user_api = Blueprint('user_api', __name__)
Session = sessionmaker(bind=engine)

# Получение всех пользователей


@user_api.route('/api/users', methods=['GET'])
def get_users():
    db_session = Session()
    users = db_session.query(User).all()
    db_session.close()

    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'age': user.age,
            'position': user.position,
            'speciality': user.speciality,
            'address': user.address,
            'email': user.email,
            'modified_date': user.modified_date.strftime('%Y-%m-%d %H:%M:%S') if user.modified_date else None
        })

    return jsonify(users_list)

# Получение одного пользователя


@user_api.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_session = Session()
    user = db_session.query(User).filter_by(id=user_id).first()
    db_session.close()

    if user:
        user_data = {
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'age': user.age,
            'position': user.position,
            'speciality': user.speciality,
            'address': user.address,
            'email': user.email,
            'modified_date': user.modified_date.strftime('%Y-%m-%d %H:%M:%S') if user.modified_date else None
        }
        return jsonify(user_data)
    else:
        return jsonify({'error': 'User not found'}), 404

# Добавление пользователя


@user_api.route('/api/users', methods=['POST'])
def add_user():
    if not request.json or 'email' not in request.json:
        return jsonify({'error': 'Invalid input'}), 400

    email = request.json['email']

    db_session = Session()
    existing_user = db_session.query(User).filter_by(email=email).first()

    if existing_user:
        db_session.close()
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(
        surname=request.json.get('surname', ""),
        name=request.json.get('name', ""),
        age=request.json.get('age', None),
        position=request.json.get('position', ""),
        speciality=request.json.get('speciality', ""),
        address=request.json.get('address', ""),
        email=email,
        hashed_password=request.json.get('hashed_password', ""),
        modified_date=datetime.now()
    )

    db_session.add(new_user)
    db_session.commit()
    db_session.close()

    return jsonify({'success': 'User added'}), 201

# Удаление пользователя


@user_api.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_session = Session()
    user = db_session.query(User).filter_by(id=user_id).first()

    if not user:
        db_session.close()
        return jsonify({'error': 'User not found'}), 404

    db_session.delete(user)
    db_session.commit()
    db_session.close()

    return jsonify({'success': 'User deleted'}), 200

# Редактирование пользователя


@user_api.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    db_session = Session()
    user = db_session.query(User).filter_by(id=user_id).first()

    if not user:
        db_session.close()
        return jsonify({'error': 'User not found'}), 404

    if not request.json:
        return jsonify({'error': 'Invalid input'}), 400

    user.surname = request.json.get('surname', user.surname)
    user.name = request.json.get('name', user.name)
    user.age = request.json.get('age', user.age)
    user.position = request.json.get('position', user.position)
    user.speciality = request.json.get('speciality', user.speciality)
    user.address = request.json.get('address', user.address)
    user.email = request.json.get('email', user.email)
    user.hashed_password = request.json.get(
        'hashed_password', user.hashed_password)
    user.modified_date = datetime.now()

    db_session.commit()
    db_session.close()

    return jsonify({'success': 'User updated'}), 200
