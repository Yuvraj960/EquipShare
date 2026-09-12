from flask import request, jsonify
from flask_security.utils import verify_password, hash_password
from flask_security import current_user, login_user, logout_user, login_required
from ..extensions import db
from ..models import User, Role
from . import bp
import uuid

def serialize_user(user):
    role_names = [r.name for r in user.roles]
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'active': user.active,
        'roles': role_names,
        'isAdmin': 'ADMIN' in role_names,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }

@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not email or not username or not password:
        return jsonify({'error': 'Email, username, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already registered'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already taken'}), 400

    user = User(
        email=email,
        username=username,
        password=hash_password(password),
        fs_uniquifier=str(uuid.uuid4()),
        active=True
    )

    # Assign USER role by default
    user_role = Role.query.filter_by(name='USER').first()
    if not user_role:
        user_role = Role(name='USER', description='Regular user')
        db.session.add(user_role)
        db.session.flush()
    user.roles.append(user_role)

    db.session.add(user)
    db.session.commit()

    login_user(user)
    token = user.get_auth_token()

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': serialize_user(user)
    }), 201

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.active:
        return jsonify({'error': 'Your account has been deactivated. Please contact an admin.'}), 403

    login_user(user)
    token = user.get_auth_token()

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': serialize_user(user)
    }), 200

@bp.route('/auth/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/auth/me', methods=['GET'])
@login_required
def me():
    data = serialize_user(current_user)
    data['equipment_count'] = current_user.equipment.count()
    data['rentals_made_count'] = current_user.rentals_as_renter.count()
    data['rentals_received_count'] = current_user.rentals_as_owner.count()
    data['requests_pending_count'] = current_user.rental_requests_made.filter_by(status='PENDING').count()
    return jsonify(data), 200

@bp.route('/auth/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json() or {}
    new_username = data.get('username', '').strip()
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()

    if new_username and new_username != current_user.username:
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != current_user.id:
            return jsonify({'error': 'Username already taken'}), 400
        current_user.username = new_username

    if new_password:
        if not current_password or not verify_password(current_password, current_user.password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        current_user.password = hash_password(new_password)

    db.session.commit()
    return jsonify({
        'message': 'Profile updated successfully',
        'user': serialize_user(current_user)
    }), 200
