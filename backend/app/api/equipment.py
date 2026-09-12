from flask import request, jsonify
from flask_security import current_user, login_required
from sqlalchemy import or_, func
from ..extensions import db
from ..models import Equipment, Category, User, Review, Rental, RentalRequest
from datetime import datetime
from . import bp

def is_admin(user):
    return any(r.name == 'ADMIN' for r in user.roles)

def get_equipment_rating_info(eid):
    rentals = Rental.query.filter_by(equipment_id=eid).all()
    rental_ids = [r.id for r in rentals]
    if not rental_ids:
        return {'avg_rating': 0, 'review_count': 0}
    stats = db.session.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(Review.rental_id.in_(rental_ids)).first()

    avg = round(float(stats[0]), 1) if stats and stats[0] is not None else 0
    cnt = stats[1] if stats else 0
    return {'avg_rating': avg, 'review_count': cnt}

def serialize_equipment(e, full=False):
    rating_info = get_equipment_rating_info(e.id)
    data = {
        'id': e.id,
        'name': e.name,
        'description': e.description,
        'condition': e.condition,
        'price_per_day': float(e.price_per_day),
        'location': e.location,
        'availability_status': e.availability_status,
        'owner_id': e.owner_id,
        'owner_username': e.owner.username if e.owner else 'Unknown',
        'category_id': e.category_id,
        'category_name': e.category.name if e.category else 'Uncategorized',
        'created_at': e.created_at.isoformat() if e.created_at else None,
        'avg_rating': rating_info['avg_rating'],
        'review_count': rating_info['review_count']
    }
    if full:
        data['owner_email'] = e.owner.email if e.owner else ''
        rentals = Rental.query.filter_by(equipment_id=e.id).all()
        rental_ids = [r.id for r in rentals]
        reviews = Review.query.filter(Review.rental_id.in_(rental_ids)).order_by(Review.created_at.desc()).all()
        data['reviews'] = [{
            'id': r.id,
            'rating': r.rating,
            'comment': r.comment,
            'reviewer_id': r.reviewer_id,
            'reviewer_username': r.reviewer.username if r.reviewer else 'User',
            'created_at': r.created_at.isoformat() if r.created_at else None
        } for r in reviews]
    return data

@bp.route('/equipment', methods=['GET'])
def list_equipment():
    query = Equipment.query

    # Search term
    search = request.args.get('search') or request.args.get('q')
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Equipment.name.ilike(term),
                Equipment.description.ilike(term),
                Equipment.location.ilike(term)
            )
        )

    # Category filter
    category_id = request.args.get('category_id') or request.args.get('category')
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    # Condition filter
    condition = request.args.get('condition')
    if condition:
        query = query.filter_by(condition=condition)

    # Status filter (default to available unless specified)
    status = request.args.get('status')
    if status:
        if status != 'all':
            query = query.filter_by(availability_status=status)
    else:
        query = query.filter_by(availability_status='available')

    # Price range
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Equipment.price_per_day >= min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Equipment.price_per_day <= max_price)

    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_asc':
        query = query.order_by(Equipment.price_per_day.asc())
    elif sort == 'price_desc':
        query = query.order_by(Equipment.price_per_day.desc())
    elif sort == 'name':
        query = query.order_by(Equipment.name.asc())
    else:
        query = query.order_by(Equipment.created_at.desc())

    items = query.all()
    return jsonify([serialize_equipment(e) for e in items]), 200

@bp.route('/equipment/my', methods=['GET'])
@login_required
def my_equipment():
    items = Equipment.query.filter_by(owner_id=current_user.id).order_by(Equipment.created_at.desc()).all()
    result = []
    for e in items:
        data = serialize_equipment(e)
        data['pending_requests_count'] = e.rental_requests.filter_by(status='PENDING').count()
        data['active_rentals_count'] = e.rentals.filter_by(status='ACTIVE').count()
        result.append(data)
    return jsonify(result), 200

@bp.route('/equipment', methods=['POST'])
@login_required
def create_equipment():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    price_per_day = data.get('price_per_day')

    if not name:
        return jsonify({'error': 'Equipment name is required'}), 400

    try:
        price_per_day = float(price_per_day)
        if price_per_day <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({'error': 'A valid positive price per day is required'}), 400

    category_id = data.get('category_id')
    if category_id:
        try:
            category_id = int(category_id)
            if not Category.query.get(category_id):
                category_id = None
        except ValueError:
            category_id = None

    equip = Equipment(
        owner_id=current_user.id,
        category_id=category_id,
        name=name,
        description=data.get('description', '').strip(),
        condition=data.get('condition', 'Good').strip(),
        price_per_day=price_per_day,
        location=data.get('location', '').strip(),
        availability_status='available'
    )
    db.session.add(equip)
    db.session.commit()

    return jsonify({
        'message': 'Equipment listed successfully',
        'equipment': serialize_equipment(equip, full=True)
    }), 201

@bp.route('/equipment/<int:eid>', methods=['GET'])
def get_equipment(eid):
    e = Equipment.query.get_or_404(eid)
    return jsonify(serialize_equipment(e, full=True)), 200

@bp.route('/equipment/<int:eid>', methods=['PUT'])
@login_required
def update_equipment(eid):
    e = Equipment.query.get_or_404(eid)
    if e.owner_id != current_user.id and not is_admin(current_user):
        return jsonify({'error': 'You do not have permission to edit this listing'}), 403

    data = request.get_json() or {}

    if 'name' in data and data['name'].strip():
        e.name = data['name'].strip()

    if 'price_per_day' in data:
        try:
            p = float(data['price_per_day'])
            if p > 0:
                e.price_per_day = p
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid price per day'}), 400

    if 'category_id' in data:
        cid = data['category_id']
        e.category_id = int(cid) if cid else None

    if 'description' in data:
        e.description = data['description'].strip()

    if 'condition' in data:
        e.condition = data['condition'].strip()

    if 'location' in data:
        e.location = data['location'].strip()

    if 'availability_status' in data:
        if data['availability_status'] in ['available', 'unavailable', 'rented', 'maintenance']:
            e.availability_status = data['availability_status']

    db.session.commit()
    return jsonify({
        'message': 'Equipment updated successfully',
        'equipment': serialize_equipment(e, full=True)
    }), 200

@bp.route('/equipment/<int:eid>', methods=['DELETE'])
@login_required
def delete_equipment(eid):
    e = Equipment.query.get_or_404(eid)
    if e.owner_id != current_user.id and not is_admin(current_user):
        return jsonify({'error': 'You do not have permission to delete this listing'}), 403

    # Check for active rental
    active_rental = Rental.query.filter_by(equipment_id=eid, status='ACTIVE').first()
    if active_rental:
        return jsonify({'error': 'Cannot delete equipment that is currently rented'}), 400

    # Delete associated pending requests and reports
    RentalRequest.query.filter_by(equipment_id=eid).delete()
    db.session.delete(e)
    db.session.commit()

    return jsonify({'message': 'Equipment deleted successfully'}), 200
