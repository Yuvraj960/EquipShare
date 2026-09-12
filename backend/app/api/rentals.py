from flask import request, jsonify
from flask_security import current_user, login_required
from ..extensions import db
from ..models import RentalRequest, Rental, Equipment, Notification, Review
from datetime import datetime, date
from . import bp

def calculate_days(start_date, end_date):
    diff = (end_date - start_date).days
    return max(1, diff if diff > 0 else 1)

def is_admin(user):
    return any(r.name == 'ADMIN' for r in user.roles)

@bp.route('/rentals/request', methods=['POST'])
@login_required
def create_request():
    data = request.get_json() or {}
    equipment_id = data.get('equipment_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    message = data.get('message', '').strip()

    if not equipment_id or not start_date_str or not end_date_str:
        return jsonify({'error': 'Equipment ID, start date, and end date are required'}), 400

    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if start_date > end_date:
        return jsonify({'error': 'End date must be after or equal to start date'}), 400

    equip = Equipment.query.get_or_404(equipment_id)

    if equip.owner_id == current_user.id:
        return jsonify({'error': 'You cannot rent your own equipment'}), 400

    if equip.availability_status != 'available':
        return jsonify({'error': f'Equipment is currently {equip.availability_status}'}), 400

    req = RentalRequest(
        equipment_id=equip.id,
        renter_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        message=message,
        status='PENDING'
    )
    db.session.add(req)

    # Notify equipment owner
    notif = Notification(
        user_id=equip.owner_id,
        message=f"New rental request for '{equip.name}' from {current_user.username} ({start_date} to {end_date})"
    )
    db.session.add(notif)
    db.session.commit()

    days = calculate_days(start_date, end_date)
    return jsonify({
        'message': 'Rental request submitted successfully',
        'id': req.id,
        'estimated_days': days,
        'estimated_total': days * equip.price_per_day
    }), 201

@bp.route('/rentals/my-requests', methods=['GET'])
@login_required
def my_requests():
    reqs = RentalRequest.query.filter_by(renter_id=current_user.id).order_by(RentalRequest.created_at.desc()).all()
    result = []
    for r in reqs:
        days = calculate_days(r.start_date, r.end_date)
        result.append({
            'id': r.id,
            'equipment_id': r.equipment_id,
            'equipment_name': r.equipment.name if r.equipment else 'Deleted item',
            'equipment_price': r.equipment.price_per_day if r.equipment else 0,
            'owner_username': r.equipment.owner.username if r.equipment and r.equipment.owner else 'Unknown',
            'start_date': str(r.start_date),
            'end_date': str(r.end_date),
            'message': r.message,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'days': days,
            'total_estimate': days * (r.equipment.price_per_day if r.equipment else 0),
            'rental_id': r.rental.id if r.rental else None
        })
    return jsonify(result), 200

@bp.route('/rentals/requests/<int:rid>/cancel', methods=['PUT'])
@login_required
def cancel_request(rid):
    req = RentalRequest.query.get_or_404(rid)
    if req.renter_id != current_user.id and not is_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    if req.status != 'PENDING':
        return jsonify({'error': f'Cannot cancel request with status {req.status}'}), 400

    req.status = 'CANCELLED'
    db.session.commit()
    return jsonify({'message': 'Request cancelled successfully'}), 200

@bp.route('/rentals/received', methods=['GET'])
@login_required
def received_requests():
    equipment_ids = [e.id for e in Equipment.query.filter_by(owner_id=current_user.id).all()]
    reqs = RentalRequest.query.filter(RentalRequest.equipment_id.in_(equipment_ids)).order_by(RentalRequest.created_at.desc()).all()
    result = []
    for r in reqs:
        days = calculate_days(r.start_date, r.end_date)
        result.append({
            'id': r.id,
            'equipment_id': r.equipment_id,
            'equipment_name': r.equipment.name if r.equipment else 'Deleted Item',
            'renter_id': r.renter_id,
            'renter_username': r.renter.username if r.renter else 'User',
            'renter_email': r.renter.email if r.renter else '',
            'start_date': str(r.start_date),
            'end_date': str(r.end_date),
            'message': r.message,
            'status': r.status,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'days': days,
            'total_estimate': days * (r.equipment.price_per_day if r.equipment else 0),
            'rental_id': r.rental.id if r.rental else None
        })
    return jsonify(result), 200

@bp.route('/rentals/<int:rid>/approve', methods=['PUT'])
@login_required
def approve_request(rid):
    req = RentalRequest.query.get_or_404(rid)
    equip = Equipment.query.get_or_404(req.equipment_id)

    if equip.owner_id != current_user.id and not is_admin(current_user):
        return jsonify({'error': 'Only the equipment owner can approve this request'}), 403

    if req.status != 'PENDING':
        return jsonify({'error': f'Request cannot be approved because status is {req.status}'}), 400

    days = calculate_days(req.start_date, req.end_date)
    total = days * equip.price_per_day

    req.status = 'APPROVED'
    rental = Rental(
        request_id=req.id,
        equipment_id=equip.id,
        owner_id=equip.owner_id,
        renter_id=req.renter_id,
        start_date=req.start_date,
        end_date=req.end_date,
        total_amount=total,
        status='ACTIVE'
    )
    equip.availability_status = 'rented'
    db.session.add(rental)

    # Notify renter
    notif = Notification(
        user_id=req.renter_id,
        message=f"Your request to rent '{equip.name}' has been APPROVED! Total amount: ₹{total}."
    )
    db.session.add(notif)

    db.session.commit()
    return jsonify({'message': 'Request approved and rental activated', 'rental_id': rental.id}), 200

@bp.route('/rentals/<int:rid>/reject', methods=['PUT'])
@login_required
def reject_request(rid):
    req = RentalRequest.query.get_or_404(rid)
    equip = Equipment.query.get_or_404(req.equipment_id)

    if equip.owner_id != current_user.id and not is_admin(current_user):
        return jsonify({'error': 'Only the equipment owner can reject this request'}), 403

    if req.status != 'PENDING':
        return jsonify({'error': f'Request status is already {req.status}'}), 400

    req.status = 'REJECTED'

    # Notify renter
    notif = Notification(
        user_id=req.renter_id,
        message=f"Your rental request for '{equip.name}' was declined by the owner."
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({'message': 'Request rejected'}), 200

@bp.route('/rentals/my-rentals', methods=['GET'])
@login_required
def my_rentals():
    role_filter = request.args.get('role')  # 'renter' or 'owner' or None
    query = Rental.query
    if role_filter == 'owner':
        query = query.filter_by(owner_id=current_user.id)
    elif role_filter == 'renter':
        query = query.filter_by(renter_id=current_user.id)
    else:
        query = query.filter((Rental.renter_id == current_user.id) | (Rental.owner_id == current_user.id))

    rentals = query.order_by(Rental.start_date.desc()).all()
    result = []
    for r in rentals:
        has_reviewed = Review.query.filter_by(rental_id=r.id, reviewer_id=current_user.id).first() is not None
        result.append({
            'id': r.id,
            'request_id': r.request_id,
            'equipment_id': r.equipment_id,
            'equipment_name': r.equipment_item.name if r.equipment_item else 'Deleted Item',
            'equipment_price': r.equipment_item.price_per_day if r.equipment_item else 0,
            'owner_id': r.owner_id,
            'owner_username': r.owner_user.username if r.owner_user else 'Owner',
            'renter_id': r.renter_id,
            'renter_username': r.renter_user.username if r.renter_user else 'Renter',
            'is_renter': r.renter_id == current_user.id,
            'is_owner': r.owner_id == current_user.id,
            'start_date': str(r.start_date),
            'end_date': str(r.end_date),
            'total_amount': float(r.total_amount),
            'status': r.status,
            'returned_at': r.returned_at.isoformat() if r.returned_at else None,
            'has_reviewed': has_reviewed
        })
    return jsonify(result), 200

@bp.route('/rentals/<int:rid>/return', methods=['PUT'])
@login_required
def return_rental(rid):
    rental = Rental.query.get_or_404(rid)
    if rental.owner_id != current_user.id and rental.renter_id != current_user.id and not is_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    if rental.status == 'RETURNED':
        return jsonify({'error': 'Rental is already marked as returned'}), 400

    rental.status = 'RETURNED'
    rental.returned_at = datetime.utcnow()

    equip = db.session.get(Equipment, rental.equipment_id)
    if equip:
        equip.availability_status = 'available'

    # Notify the other party
    recipient_id = rental.owner_id if current_user.id == rental.renter_id else rental.renter_id
    notif = Notification(
        user_id=recipient_id,
        message=f"Equipment '{equip.name if equip else 'item'}' from rental #{rental.id} has been returned."
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({'message': 'Rental returned successfully'}), 200
