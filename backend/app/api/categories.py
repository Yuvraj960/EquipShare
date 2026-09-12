from flask import request, jsonify
from flask_security import current_user, login_required
from ..extensions import db
from ..models import Category, Equipment
from . import bp

def is_admin(user):
    return any(r.name == 'ADMIN' for r in user.roles)

@bp.route('/categories', methods=['GET'])
def list_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    result = []
    for c in categories:
        result.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'equipment_count': c.equipment.filter_by(availability_status='available').count(),
            'total_equipment_count': c.equipment.count()
        })
    return jsonify(result), 200

@bp.route('/categories', methods=['POST'])
@login_required
def create_category():
    if not is_admin(current_user):
        return jsonify({'error': 'Admin privileges required'}), 403

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({'error': 'Category already exists'}), 400

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        'message': 'Category created successfully',
        'category': {'id': category.id, 'name': category.name, 'description': category.description}
    }), 201

@bp.route('/categories/<int:cid>', methods=['DELETE'])
@login_required
def delete_category(cid):
    if not is_admin(current_user):
        return jsonify({'error': 'Admin privileges required'}), 403

    category = Category.query.get_or_404(cid)
    # Reassign equipment to null category so items are not orphaned
    Equipment.query.filter_by(category_id=cid).update({'category_id': None})
    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category deleted successfully'}), 200
