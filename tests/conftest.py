"""
tests/conftest.py — configuration + fixtures communes à tous les tests (pytest la charge avant tout).

- SECRET_KEY de test (les vrais secrets restent dans .env, jamais commité) ;
- client_http   : client HTTP de test + base SQLite EN MÉMOIRE (jetable à chaque test),
                  avec la session de test branchée dans routes/auth.py ET routes/produits.py
                  (la vraie base digimarket.db n'est jamais touchée) ;
- token_admin / token_client : tokens JWT obtenus via register + login.
"""
import os

os.environ.setdefault("SECRET_KEY", "cle_de_test_pour_pytest_32_caracteres_min")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from app.app import app
from app.modelsSQLAlchemy import Base, User, Category
import app.routes.auth as auth_module
import app.routes.produits as prod_module


@pytest.fixture
def session_test():
    """Base SQLite en mémoire + session de test branchée dans les deux modules de routes."""
    engine = create_engine("sqlite:///:memory:")     # base en RAM, rien sur le disque
    Base.metadata.create_all(engine)                  # crée users, categories, products
    S = sessionmaker(bind=engine)()
    # on remplace la session des modules par CELLE DE TEST (base en mémoire)
    auth_module.session = S
    prod_module.session = S
    yield S
    Base.metadata.drop_all(engine)                    # nettoyage après le test


@pytest.fixture
def client_http(session_test):
    """Client HTTP de test (app.test_client = 'navigateur/curl simulé' de Flask)."""
    app.config["TESTING"] = True
    yield app.test_client()


def _creer_user(session_test, email, password, role):
    u = User(email=email, password_hash=generate_password_hash(password),
             first_name="T", last_name="T", role=role)
    session_test.add(u)
    session_test.commit()
    return u


@pytest.fixture
def token_admin(client_http, session_test):
    """Crée un admin en base de test, se loggue, renvoie son token JWT."""
    _creer_user(session_test, "admin@x.fr", "admin123", "admin")
    r = client_http.post("/api/auth/login", json={"email": "admin@x.fr", "password": "admin123"})
    assert r.status_code == 200
    return r.get_json()["token"]


@pytest.fixture
def token_client(client_http, session_test):
    """Crée un client (rôle 'client'), se loggue, renvoie son token JWT."""
    _creer_user(session_test, "client@x.fr", "client123", "client")
    r = client_http.post("/api/auth/login", json={"email": "client@x.fr", "password": "client123"})
    assert r.status_code == 200
    return r.get_json()["token"]
