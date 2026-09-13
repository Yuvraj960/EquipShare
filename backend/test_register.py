import os
os.environ['PYTHONPATH'] = '.'
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    from app.models import User
    inspector = db.inspect(db.engine)
    print('Tables exist?', inspector.get_table_names())
    # try query
    try:
        u = User.query.filter_by(email='test@test.com').first()
        print('Query ok', u)
    except Exception as e:
        print('Error', e)
