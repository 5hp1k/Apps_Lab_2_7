from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import sessionmaker
from models import Job, engine


api = Blueprint('api', __name__)
Session = sessionmaker(bind=engine)
# Получение всех работ


@api.route('/api/jobs', methods=['GET'])
def get_jobs():
    db_session = Session()
    jobs = db_session.query(Job).all()
    db_session.close()

    jobs_list = []
    for job in jobs:
        jobs_list.append({
            'id': job.id,
            'job': job.job,
            'team_leader': job.team_leader,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'start_date': job.start_date.strftime('%Y-%m-%d') if job.start_date else None,
            'end_date': job.end_date.strftime('%Y-%m-%d') if job.end_date else None,
            'is_finished': job.is_finished
        })

    return jsonify(jobs_list)


# Получение одной работы
@api.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    db_session = Session()
    job = db_session.query(Job).filter_by(id=job_id).first()
    db_session.close()

    if job:
        job_data = {
            'id': job.id,
            'job': job.job,
            'team_leader': job.team_leader,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'start_date': job.start_date.strftime('%Y-%m-%d') if job.start_date else None,
            'end_date': job.end_date.strftime('%Y-%m-%d') if job.end_date else None,
            'is_finished': job.is_finished
        }
        return jsonify(job_data)
    else:
        return jsonify({'error': 'Job not found'}), 404


# Добавление работы
@api.route('/api/jobs', methods=['POST'])
def add_job():
    if not request.json or 'id' not in request.json:
        return jsonify({'error': 'Invalid input'}), 400

    job_id = request.json['id']

    db_session = Session()
    existing_job = db_session.query(Job).filter_by(id=job_id).first()

    if existing_job:
        db_session.close()
        return jsonify({'error': 'Id already exists'}), 400

    new_job = Job(
        id=job_id,
        job=request.json.get('job', ""),
        team_leader=request.json.get('team_leader', None),
        work_size=request.json.get('work_size', 0),
        collaborators=request.json.get('collaborators', ""),
        start_date=datetime.strptime(request.json.get(
            'start_date'), '%Y-%m-%d') if 'start_date' in request.json else None,
        end_date=datetime.strptime(request.json.get(
            'end_date'), '%Y-%m-%d') if 'end_date' in request.json else None,
        is_finished=request.json.get('is_finished', False)
    )

    db_session.add(new_job)
    db_session.commit()
    db_session.close()

    return jsonify({'success': 'Job added'}), 201


# Удаление работы
@api.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    db_session = Session()
    job = db_session.query(Job).filter_by(id=job_id).first()

    if not job:
        db_session.close()
        return jsonify({'error': 'Job not found'}), 404

    db_session.delete(job)
    db_session.commit()
    db_session.close()

    return jsonify({'success': 'Job deleted'}), 200


# Редактирование работы
@api.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    db_session = Session()
    job = db_session.query(Job).filter_by(id=job_id).first()

    if not job:
        db_session.close()
        return jsonify({'error': 'Job not found'}), 404

    if not request.json:
        return jsonify({'error': 'Invalid input'}), 400

    job.job = request.json.get('job', job.job)
    job.team_leader = request.json.get('team_leader', job.team_leader)
    job.work_size = request.json.get('work_size', job.work_size)
    job.collaborators = request.json.get('collaborators', job.collaborators)
    job.start_date = datetime.strptime(request.json.get(
        'start_date'), '%Y-%m-%d') if 'start_date' in request.json else job.start_date
    job.end_date = datetime.strptime(request.json.get(
        'end_date'), '%Y-%m-%d') if 'end_date' in request.json else job.end_date
    job.is_finished = request.json.get('is_finished', job.is_finished)

    db_session.commit()
    db_session.close()

    return jsonify({'success': 'Job updated'}), 200
