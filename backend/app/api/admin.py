from flask import request, jsonify
from flask_security import current_user, login_required
from sqlalchemy import func
from ..extensions import db
from ..models import User, Equipment, Rental, RentalRequest, Report, Category, Role, Notification
from datetime import datetime, date, timedelta
from . import bp

def admin_required():
    if not current_user.is_authenticated or not any(r.name == 'ADMIN' for r in current_user.roles):
        return False
    return True

@bp.route('/admin/stats', methods=['GET'])
@login_required
def admin_stats():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    total_users = User.query.count()
    total_equipment = Equipment.query.count()
    available_equipment = Equipment.query.filter_by(availability_status='available').count()
    active_rentals = Rental.query.filter_by(status='ACTIVE').count()
    completed_rentals = Rental.query.filter_by(status='RETURNED').count()
    total_revenue = db.session.query(func.sum(Rental.total_amount)).scalar() or 0.0
    open_reports = Report.query.filter_by(status='OPEN').count()
    pending_requests = RentalRequest.query.filter_by(status='PENDING').count()
    categories_count = Category.query.count()

    return jsonify({
        'total_users': total_users,
        'total_equipment': total_equipment,
        'available_equipment': available_equipment,
        'active_rentals': active_rentals,
        'completed_rentals': completed_rentals,
        'total_revenue': round(float(total_revenue), 2),
        'open_reports': open_reports,
        'pending_requests': pending_requests,
        'categories_count': categories_count
    }), 200

@bp.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    users = User.query.order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'active': u.active,
            'roles': [r.name for r in u.roles],
            'equipment_count': u.equipment.count(),
            'rentals_count': u.rentals_as_renter.count(),
            'created_at': u.created_at.isoformat() if u.created_at else None
        })
    return jsonify(result), 200

@bp.route('/admin/users/<int:uid>/toggle-status', methods=['PUT'])
@login_required
def admin_toggle_user(uid):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    if uid == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own admin account'}), 400

    u = User.query.get_or_404(uid)
    u.active = not u.active
    db.session.commit()

    action = 'activated' if u.active else 'deactivated'
    return jsonify({'message': f'User {u.username} has been {action}', 'active': u.active}), 200

@bp.route('/admin/equipment', methods=['GET'])
@login_required
def admin_equipment():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    items = Equipment.query.order_by(Equipment.created_at.desc()).all()
    result = []
    for e in items:
        result.append({
            'id': e.id,
            'name': e.name,
            'category_name': e.category.name if e.category else 'Uncategorized',
            'owner_username': e.owner.username if e.owner else 'Unknown',
            'price_per_day': float(e.price_per_day),
            'location': e.location,
            'condition': e.condition,
            'availability_status': e.availability_status,
            'created_at': e.created_at.isoformat() if e.created_at else None
        })
    return jsonify(result), 200

@bp.route('/admin/reports', methods=['GET'])
@login_required
def admin_reports():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    reports = Report.query.order_by(Report.created_at.desc()).all()
    result = []
    for r in reports:
        reporter = db.session.get(User, r.reporter_id)
        reported_user = db.session.get(User, r.reported_user_id) if r.reported_user_id else None
        equip = db.session.get(Equipment, r.equipment_id) if r.equipment_id else None
        result.append({
            'id': r.id,
            'reporter_username': reporter.username if reporter else 'Unknown',
            'reported_username': reported_user.username if reported_user else None,
            'equipment_name': equip.name if equip else None,
            'reason': r.reason,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None
        })
    return jsonify(result), 200

@bp.route('/admin/reports/<int:rid>/resolve', methods=['PUT'])
@login_required
def admin_resolve_report(rid):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    report = Report.query.get_or_404(rid)
    report.status = 'RESOLVED'
    db.session.commit()
    return jsonify({'message': 'Report marked as resolved'}), 200

@bp.route('/admin/run-scheduled-tasks', methods=['POST'])
@login_required
def run_scheduled_tasks():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    # 1. Expire pending requests older than 3 days
    cutoff = datetime.utcnow() - timedelta(days=3)
    expired_requests = RentalRequest.query.filter_by(status='PENDING').filter(RentalRequest.created_at < cutoff).all()
    for req in expired_requests:
        req.status = 'EXPIRED'
        notif = Notification(
            user_id=req.renter_id,
            message=f"Your rental request #{req.id} has expired due to owner inactivity."
        )
        db.session.add(notif)

    # 2. Return reminders: active rentals ending tomorrow
    tomorrow = date.today() + timedelta(days=1)
    upcoming_returns = Rental.query.filter(Rental.status == 'ACTIVE', Rental.end_date == tomorrow).all()
    reminders_sent = 0
    for r in upcoming_returns:
        existing_notif = Notification.query.filter(
            Notification.user_id == r.renter_id,
            Notification.message.like(f"%Rental #{r.id} ends tomorrow%")
        ).first()
        if not existing_notif:
            notif = Notification(
                user_id=r.renter_id,
                message=f"Reminder: Rental #{r.id} for '{r.equipment_item.name if r.equipment_item else 'item'}' ends tomorrow ({r.end_date}). Please prepare to return it."
            )
            db.session.add(notif)
            reminders_sent += 1

    db.session.commit()
    return jsonify({
        'message': 'Scheduled maintenance tasks executed successfully',
        'expired_requests_count': len(expired_requests),
        'reminders_sent_count': reminders_sent
    }), 200
