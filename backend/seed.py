from app import create_app
from app.extensions import db
from app.models import Role, User, Category, Equipment, RentalRequest, Rental, Review, Notification
from flask_security.utils import hash_password
from datetime import datetime, date, timedelta
import uuid

app = create_app()

with app.app_context():
    db.create_all()

    # 1. Roles
    user_role = Role.query.filter_by(name='USER').first()
    if not user_role:
        user_role = Role(name='USER', description='Regular platform member')
        db.session.add(user_role)

    admin_role = Role.query.filter_by(name='ADMIN').first()
    if not admin_role:
        admin_role = Role(name='ADMIN', description='Platform Administrator')
        db.session.add(admin_role)

    db.session.commit()

    # 2. Users
    def get_or_create_user(email, username, password, is_admin=False):
        u = User.query.filter_by(email=email).first()
        if not u:
            u = User(
                email=email,
                username=username,
                password=hash_password(password),
                fs_uniquifier=str(uuid.uuid4()),
                active=True
            )
            u.roles.append(user_role)
            if is_admin:
                u.roles.append(admin_role)
            db.session.add(u)
        else:
            u.password = hash_password(password)
            u.active = True
            if is_admin and admin_role not in u.roles:
                u.roles.append(admin_role)
        db.session.commit()
        return u

    admin = get_or_create_user('admin@equipshare.test', 'admin', 'admin123', is_admin=True)
    yuvraj = get_or_create_user('yuvraj@equipshare.test', 'yuvraj', 'user123')
    ananya = get_or_create_user('ananya@equipshare.test', 'ananya', 'user123')
    rohit = get_or_create_user('rohit@equipshare.test', 'rohit', 'user123')

    # 3. Categories
    categories_data = [
        ('Cameras & Optics', 'DSLRs, mirrorless cameras, lenses, tripods, and gimbals'),
        ('Laptops & Computing', 'Laptops, GPUs, tablets, and mobile computing gear'),
        ('Audio & Music', 'Microphones, studio monitors, speakers, and musical instruments'),
        ('Projectors & Displays', 'Portable projectors, high-lumen displays, and projection screens'),
        ('Tools & Hardware', 'Power tools, drills, soldering stations, and maker equipment'),
        ('Sports & Outdoor', 'Tents, bicycles, trekking gear, and sports kits'),
        ('Lab & Electronics', 'Oscilloscopes, multimeters, Arduino & Raspberry Pi kits')
    ]

    cat_map = {}
    for name, desc in categories_data:
        c = Category.query.filter_by(name=name).first()
        if not c:
            c = Category(name=name, description=desc)
            db.session.add(c)
            db.session.flush()
        cat_map[name] = c
    db.session.commit()

    # 4. Equipment
    equipment_data = [
        {
            'name': 'Canon EOS 1500D DSLR Camera',
            'category': 'Cameras & Optics',
            'owner': yuvraj,
            'price': 500.0,
            'condition': 'Like New',
            'location': 'Sector 14, Chandigarh',
            'description': '24.1 MP DSLR with 18-55mm IS II Lens, 64GB high speed SD card, extra battery and camera bag included. Perfect for events and portraits.'
        },
        {
            'name': 'Sony Alpha A7 III Full Frame',
            'category': 'Cameras & Optics',
            'owner': ananya,
            'price': 1200.0,
            'condition': 'Excellent',
            'location': 'Connaught Place, New Delhi',
            'description': 'Flagship 24.2 MP full-frame sensor, 4K HDR video, Tamron 28-75mm f/2.8 lens, dual SD slots, 2 extra batteries. Ideal for professional gigs.'
        },
        {
            'name': 'DJI Ronin-SC 3-Axis Gimbal',
            'category': 'Cameras & Optics',
            'owner': rohit,
            'price': 450.0,
            'condition': 'Like New',
            'location': 'Sector 35, Chandigarh',
            'description': 'Lightweight 3-axis stabilizer for mirrorless cameras. ActiveTrack 3.0, easy balancing, focus wheel included.'
        },
        {
            'name': 'Epson Full HD Projector 3000 Lumens',
            'category': 'Projectors & Displays',
            'owner': yuvraj,
            'price': 350.0,
            'condition': 'Good',
            'location': 'Phase 7, Mohali',
            'description': 'Bright 1080p projector with HDMI/VGA cables and remote. Great for university seminars, hackathons, and movie nights.'
        },
        {
            'name': 'Apple MacBook Pro 16-inch M1 Pro',
            'category': 'Laptops & Computing',
            'owner': ananya,
            'price': 1000.0,
            'condition': 'Excellent',
            'location': 'Sector 17, Chandigarh',
            'description': '16GB RAM, 512GB SSD, powerful machine for video editing in Final Cut Pro, software builds, or presentations.'
        },
        {
            'name': 'JBL PartyBox 310 Bluetooth Speaker',
            'category': 'Audio & Music',
            'owner': rohit,
            'price': 600.0,
            'condition': 'Like New',
            'location': 'Panchkula',
            'description': '240W booming sound with dynamic light show, dual mic inputs for karaoke, and built-in wheels with 18-hour battery.'
        },
        {
            'name': 'Bosch Professional Cordless Drill Kit',
            'category': 'Tools & Hardware',
            'owner': yuvraj,
            'price': 200.0,
            'condition': 'Good',
            'location': 'Sector 22, Chandigarh',
            'description': '18V cordless drill with 2 lithium-ion batteries, charger, and 30-piece drill and screwdriver bit set.'
        },
        {
            'name': 'Shure SM7B Vocal Microphone',
            'category': 'Audio & Music',
            'owner': ananya,
            'price': 400.0,
            'condition': 'Like New',
            'location': 'Sector 34, Chandigarh',
            'description': 'Industry standard broadcast and podcast microphone with pop filter and Cloudlifter CL-1 mic activator included.'
        },
        {
            'name': 'Rigol Digital Oscilloscope 100MHz 2-Channel',
            'category': 'Lab & Electronics',
            'owner': rohit,
            'price': 300.0,
            'condition': 'Good',
            'location': 'Mohali Campus',
            'description': 'DS1054Z 50MHz-100MHz digital storage oscilloscope, 4 channels, with passive probes and USB interface for student lab projects.'
        },
        {
            'name': 'Quechua 4-Person Waterproof Camping Tent',
            'category': 'Sports & Outdoor',
            'owner': yuvraj,
            'price': 250.0,
            'condition': 'Like New',
            'location': 'Sector 15, Chandigarh',
            'description': 'Easy 2-second pitch tent, fresh & black technology (blocks 99% light), completely waterproof. Groundsheet and pegs included.'
        }
    ]

    for item in equipment_data:
        existing = Equipment.query.filter_by(name=item['name']).first()
        if not existing:
            e = Equipment(
                name=item['name'],
                category_id=cat_map[item['category']].id,
                owner_id=item['owner'].id,
                price_per_day=item['price'],
                condition=item['condition'],
                location=item['location'],
                description=item['description'],
                availability_status='available'
            )
            db.session.add(e)
    db.session.commit()

    # 5. Seed a sample completed rental and review to illustrate review history
    canon_cam = Equipment.query.filter_by(name='Canon EOS 1500D DSLR Camera').first()
    if canon_cam and not RentalRequest.query.filter_by(equipment_id=canon_cam.id).first():
        req = RentalRequest(
            equipment_id=canon_cam.id,
            renter_id=ananya.id,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=7),
            message='Needed for our college tech fest photography coverage.',
            status='APPROVED'
        )
        db.session.add(req)
        db.session.flush()

        rental = Rental(
            request_id=req.id,
            equipment_id=canon_cam.id,
            owner_id=canon_cam.owner_id,
            renter_id=ananya.id,
            start_date=req.start_date,
            end_date=req.end_date,
            total_amount=3 * canon_cam.price_per_day,
            status='RETURNED',
            returned_at=datetime.utcnow() - timedelta(days=7)
        )
        db.session.add(rental)
        db.session.flush()

        review = Review(
            rental_id=rental.id,
            reviewer_id=ananya.id,
            rating=5,
            comment='The Canon camera was in mint condition and the extra battery was super helpful! Yuvraj was very responsive and easy to coordinate with.'
        )
        db.session.add(review)

        notif = Notification(
            user_id=yuvraj.id,
            message=f"Welcome to EquipShare! Your camera has already received its first 5-star review."
        )
        db.session.add(notif)
        db.session.commit()

    print('Seed successfully populated with categories, users, equipment, rental history, and reviews!')
