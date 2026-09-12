from flask import jsonify
from flask_security import current_user, login_required
from ..extensions import db
from ..models import Notification
from . import bp

@bp.route('/notifications', methods=['GET'])
@login_required
def list_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread_count = sum(1 for n in notifications if not n.read)
    return jsonify({
        'notifications': [{
            'id': n.id,
            'message': n.message,
            'read': n.read,
            'created_at': n.created_at.isoformat() if n.created_at else None
        } for n in notifications],
        'unread_count': unread_count
    }), 200

@bp.route('/notifications/<int:nid>/read', methods=['PUT'])
@login_required
def mark_read(nid):
    n = Notification.query.get_or_404(nid)
    if n.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    n.read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200

@bp.route('/notifications/read-all', methods=['PUT'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200

@bp.route('/notifications/<int:nid>', methods=['DELETE'])
@login_required
def delete_notification(nid):
    n = Notification.query.get_or_404(nid)
    if n.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(n)
    db.session.commit()
    return jsonify({'message': 'Notification deleted'}), 200
