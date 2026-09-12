from datetime import datetime, date, timedelta
from ..extensions import celery, db
from ..models import Rental, Notification

@celery.task
def send_return_reminders():
    today = date.today()
    threshold = today + timedelta(days=1)
    rentals = Rental.query.filter(Rental.status=='ACTIVE', Rental.end_date==threshold).all()
    for rental in rentals:
        msg = f'Reminder: Rental {rental.id} ends tomorrow {rental.end_date}'
        notif = Notification(user_id=rental.renter_id, message=msg)
        db.session.add(notif)
    db.session.commit()
    return f'Sent {len(rentals)} reminders'

@celery.task
def expire_pending_requests():
    from ..models import RentalRequest
    cutoff = datetime.utcnow() - timedelta(days=3)
    requests = RentalRequest.query.filter_by(status='PENDING').filter(RentalRequest.created_at < cutoff).all()
    for req in requests:
        req.status = 'EXPIRED'
    db.session.commit()
    return f'Expired {len(requests)} requests'
