from flask import request, jsonify
from flask_security import current_user, login_required
from ..extensions import db
from ..models import Review, Rental, Equipment, Notification
from . import bp

@bp.route('/equipment/<int:eid>/reviews', methods=['GET'])
def get_reviews(eid):
    rentals = Rental.query.filter_by(equipment_id=eid).all()
    rental_ids = [r.id for r in rentals]
    if not rental_ids:
        return jsonify([]), 200

    reviews = Review.query.filter(Review.rental_id.in_(rental_ids)).order_by(Review.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'rental_id': r.rental_id,
        'rating': r.rating,
        'comment': r.comment,
        'reviewer_id': r.reviewer_id,
        'reviewer_username': r.reviewer.username if r.reviewer else 'Anonymous',
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in reviews]), 200

@bp.route('/equipment/<int:eid>/reviews', methods=['POST'])
@login_required
def add_review(eid):
    data = request.get_json() or {}
    rental_id = data.get('rental_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()

    if rental_id is None or rating is None:
        return jsonify({'error': 'Rental ID and rating are required'}), 400

    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    except (TypeError, ValueError):
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    rental = Rental.query.get_or_404(rental_id)
    if rental.equipment_id != eid:
        return jsonify({'error': 'Rental does not match equipment'}), 400

    if rental.renter_id != current_user.id:
        return jsonify({'error': 'Only the renter can review this rental'}), 403

    existing = Review.query.filter_by(rental_id=rental.id, reviewer_id=current_user.id).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this rental'}), 400

    review = Review(
        rental_id=rental.id,
        reviewer_id=current_user.id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)

    # Notify owner
    equip_name = rental.equipment_item.name if rental.equipment_item else 'item'
    notif = Notification(
        user_id=rental.owner_id,
        message=f"{current_user.username} left a {rating}-star review for '{equip_name}': \"{comment[:50]}\""
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        'message': 'Review submitted successfully',
        'review': {
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'reviewer_username': current_user.username,
            'created_at': review.created_at.isoformat() if review.created_at else None
        }
    }), 201
