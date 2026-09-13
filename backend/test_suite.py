import unittest
import json
from app import create_app
from app.extensions import db
from app.models import User, Role, Category, Equipment, Rental, RentalRequest

class EquipShareAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_login_and_token(self):
        resp = self.client.post('/api/auth/login', json={
            'email': 'admin@equipshare.test',
            'password': 'admin123'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('token', data)
        self.assertTrue(data['user']['isAdmin'])
        self.assertEqual(data['user']['username'], 'admin')

    def test_02_categories(self):
        resp = self.client.get('/api/categories')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 5)
        names = [c['name'] for c in data]
        self.assertIn('Cameras & Optics', names)

    def test_03_equipment_listing_and_search(self):
        resp = self.client.get('/api/equipment')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 5)

        # Test search query
        resp = self.client.get('/api/equipment?search=Canon')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data), 1)
        self.assertIn('Canon', data[0]['name'])

    def test_04_auth_me_with_token(self):
        # Login
        login_resp = self.client.post('/api/auth/login', json={
            'email': 'yuvraj@equipshare.test',
            'password': 'user123'
        })
        token = login_resp.get_json()['token']

        # Call /api/auth/me
        resp = self.client.get('/api/auth/me', headers={'Authentication-Token': token})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['username'], 'yuvraj')
        self.assertIn('equipment_count', data)

    def test_05_rental_workflow(self):
        # 1. Login as ananya (renter)
        login_ananya = self.client.post('/api/auth/login', json={
            'email': 'ananya@equipshare.test',
            'password': 'user123'
        })
        ananya_token = login_ananya.get_json()['token']

        # 2. Find equipment owned by yuvraj
        equip = Equipment.query.filter_by(name='Bosch Professional Cordless Drill Kit').first()
        self.assertIsNotNone(equip)

        # 3. Ananya requests equipment
        req_resp = self.client.post('/api/rentals/request', headers={'Authentication-Token': ananya_token}, json={
            'equipment_id': equip.id,
            'start_date': '2026-09-20',
            'end_date': '2026-09-22',
            'message': 'Need drill kit for home bookshelf assembly'
        })
        self.assertEqual(req_resp.status_code, 201)
        req_id = req_resp.get_json()['id']

        # 4. Login as yuvraj (owner)
        login_yuvraj = self.client.post('/api/auth/login', json={
            'email': 'yuvraj@equipshare.test',
            'password': 'user123'
        })
        yuvraj_token = login_yuvraj.get_json()['token']

        # 5. Yuvraj views received requests
        rec_resp = self.client.get('/api/rentals/received', headers={'Authentication-Token': yuvraj_token})
        self.assertEqual(rec_resp.status_code, 200)
        received_ids = [r['id'] for r in rec_resp.get_json()]
        self.assertIn(req_id, received_ids)

        # 6. Yuvraj approves request
        app_resp = self.client.put(f'/api/rentals/{req_id}/approve', headers={'Authentication-Token': yuvraj_token})
        self.assertEqual(app_resp.status_code, 200)
        rental_id = app_resp.get_json()['rental_id']

        # Verify equipment is marked rented
        self.assertEqual(equip.availability_status, 'rented')

        # 7. Ananya checks my-rentals
        my_rentals_resp = self.client.get('/api/rentals/my-rentals', headers={'Authentication-Token': ananya_token})
        self.assertEqual(my_rentals_resp.status_code, 200)
        active_ids = [r['id'] for r in my_rentals_resp.get_json()]
        self.assertIn(rental_id, active_ids)

        # 8. Ananya returns rental
        ret_resp = self.client.put(f'/api/rentals/{rental_id}/return', headers={'Authentication-Token': ananya_token})
        self.assertEqual(ret_resp.status_code, 200)
        self.assertEqual(equip.availability_status, 'available')

        # 9. Ananya leaves review
        rev_resp = self.client.post(f'/api/equipment/{equip.id}/reviews', headers={'Authentication-Token': ananya_token}, json={
            'rental_id': rental_id,
            'rating': 5,
            'comment': 'Worked smoothly and battery was fully charged!'
        })
        self.assertEqual(rev_resp.status_code, 201)

    def test_06_admin_stats_and_tasks(self):
        login_admin = self.client.post('/api/auth/login', json={
            'email': 'admin@equipshare.test',
            'password': 'admin123'
        })
        admin_token = login_admin.get_json()['token']

        # Admin stats
        stats_resp = self.client.get('/api/admin/stats', headers={'Authentication-Token': admin_token})
        self.assertEqual(stats_resp.status_code, 200)
        stats = stats_resp.get_json()
        self.assertGreaterEqual(stats['total_users'], 4)
        self.assertGreaterEqual(stats['total_equipment'], 10)

        # Run scheduled maintenance tasks
        tasks_resp = self.client.post('/api/admin/run-scheduled-tasks', headers={'Authentication-Token': admin_token})
        self.assertEqual(tasks_resp.status_code, 200)
        self.assertIn('expired_requests_count', tasks_resp.get_json())

if __name__ == '__main__':
    unittest.main()
