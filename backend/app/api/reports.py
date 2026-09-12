from flask import request, jsonify
from flask_security import current_user, login_required
from ..extensions import db
from ..models import Report
from . import bp

@bp.route('/reports', methods=['POST'])
@login_required
def create_report():
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()
    reported_user_id = data.get('reported_user_id')
    equipment_id = data.get('equipment_id')

    if not reason:
        return jsonify({'error': 'Reason for report is required'}), 400

    report = Report(
        reporter_id=current_user.id,
        reported_user_id=reported_user_id,
        equipment_id=equipment_id,
        reason=reason,
        status='OPEN'
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({'message': 'Report submitted successfully. Administrators will review it.', 'id': report.id}), 201
