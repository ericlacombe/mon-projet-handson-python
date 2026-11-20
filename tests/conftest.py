"""
tests/conftest.py — configuration + fixtures COMMUNES à tous les tests (pytest la charge avant tout).

Pourquoi un conftest.py ? Pour ne pas répéter la même mise en place dans chaque fichier de test.

- SECRET_KEY de test : posée ici pour que app/security.py s'importe même sans .env
  (les vrais secrets restent dans .env, jamais commité) ;
- session_test  : base SQLite EN MÉMOIRE (jetable à chaque test) + la session de test branchée
                  dans routes/auth.py ET routes/produits.py → la vraie base digimarket.db
                  n'est JAMAIS touchée par les tests ;
- client_http   : client HTTP de test (app.test_client() = « curl simulé » de Flask) ;
- token_admin / token_client : tokens JWT obtenus via un vrai login (fixture qui crée
                  l'utilisateur en base de test puis appelle POST /api/auth/login).
"""
# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
# os : lire/écrire les variables d'environnement (ici poser SECRET_KEY de test AVANT
#      d'importer app.security, sinon KeyError à l'import)
import os

# Clé de test bidon (32+ caractères comme recommandé) — PAS la vraie clé (.env, .gitignore)
os.environ.setdefault("SECRET_KEY", "cle_de_test_pour_pytest_32_caracteres_min")

# pytest : le lanceur de tests — fournit @pytest.fixture (fonctions exécutées avant chaque test)
import pytest
# create_engine : crée le moteur SQLite EN MÉMOIRE (sqlite:///:memory: = base en RAM, jetable)
from sqlalchemy import create_engine
# sessionmaker : fabrique de sessions (conversations avec la base de test)
from sqlalchemy.orm import sessionmaker
# generate_password_hash : hache un mot de passe (création des comptes de test, comme au register)
from werkzeug.security import generate_password_hash

# app : l'application Flask (créée dans app/app.py) — app.test_client() sert de client HTTP de test
from app.app import app
# Base (métadonnée des tables, pour create_all/drop_all) + modèles User, Category
from app.modelsSQLAlchemy import Base, User, Category
# auth_module / prod_module = les modules routes/*.py importés sous ce nom.
# Ils servent de « poignée » : on va remplacer LEUR session (celle de db.py, liée à la
# vraie base digimarket.db) par une session de test en mémoire — comme ça, les
# session.add/commit des routes écrivent dans la base de TEST, jamais dans la vraie base.
import app.routes.auth as auth_module
import app.routes.produits as prod_module


@pytest.fixture
def session_test():
    """Base SQLite EN MÉMOIRE (sqlite:///:memory:) + session de test branchée dans les routes.

    Pourquoi en mémoire ? Un test ne doit JAMAIS toucher la vraie base digimarket.db :
    chaque test part d'une base vide et la détruit après (drop_all) → tests isolés,
    reproductibles, sans effet de bord.
    """
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
    """Client HTTP de test : app.test_client() simule un navigateur/curl (appels GET/POST…)
    sans lancer de serveur — chaque appel = une vraie requête HTTP dans l'app Flask."""
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
    """Token JWT d'un ADMIN : crée l'admin en base de test, appelle POST /api/auth/login,
    renvoie le token (à mettre en header Authorization: Bearer <token>)."""
    _creer_user(session_test, "admin@x.fr", "admin123", "admin")
    r = client_http.post("/api/auth/login", json={"email": "admin@x.fr", "password": "admin123"})
    assert r.status_code == 200
    return r.get_json()["token"]


@pytest.fixture
def token_client(client_http, session_test):
    """Token JWT d'un simple CLIENT (rôle 'client') : sert à tester le 403 (rôle insuffisant)."""
    _creer_user(session_test, "client@x.fr", "client123", "client")
    r = client_http.post("/api/auth/login", json={"email": "client@x.fr", "password": "client123"})
    assert r.status_code == 200
    return r.get_json()["token"]
