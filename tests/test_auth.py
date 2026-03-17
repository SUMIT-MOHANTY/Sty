import unittest
from app import create_app, db
from app.models.user import User
from flask import url_for

class TestAuthBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test user
        self.user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login to your Account', response.data)

    def test_login_success(self):
        response = self.client.post('/login',
            data={
                'email': 'test@example.com',
                'password': 'password123',
                'remember': False
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, Test', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login',
            data={
                'email': 'test@example.com',
                'password': 'wrongpassword',
                'remember': False
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login unsuccessful', response.data)

if __name__ == '__main__':
    unittest.main()
