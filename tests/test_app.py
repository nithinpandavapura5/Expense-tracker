import pytest
from app import create_app, db, bcrypt
from app.models import User, Category

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create default categories
            c1 = Category(name='Food')
            db.session.add(c1)
            db.session.commit()
            yield client

def test_home_page(client):
    """Test that home page redirects to login if not authenticated"""
    response = client.get('/')
    assert response.status_code == 302
    assert b"login" in response.data

def test_register(client):
    """Test user registration"""
    response = client.post('/register', data=dict(
        username='testuser',
        email='test@example.com',
        password='password',
        confirm_password='password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Your account has been created" in response.data

def test_login_logout(client):
    """Test login and logout"""
    # Register first
    client.post('/register', data=dict(
        username='testuser',
        email='test@example.com',
        password='password',
        confirm_password='password'
    ), follow_redirects=True)

    # Login
    response = client.post('/login', data=dict(
        email='test@example.com',
        password='password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Log In" in response.data
