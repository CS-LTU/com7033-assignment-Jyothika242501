import pytest
from stroke_app import create_app, db
from stroke_app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,   # simplify tests
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_and_login(client, app):
    # Register
    resp = client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123"
    }, follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        assert User.query.filter_by(email="test@example.com").first() is not None

    # Login
    resp = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123"
    }, follow_redirects=True)
    assert b"Patients" in resp.data  # redirected to dashboard/patients
