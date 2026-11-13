"""
tests/test_security.py — Tests F1 (login) + F4 (sécurité JWT), niveau 🥈.

Fichier cible des catégories F1 et F4 (voir docs/etape5-tests-intermediaire.md).
Lancer depuis la racine :  pytest
"""
import jwt
from datetime import datetime, timedelta, timezone

from app.security import SECRET_KEY, ALGO


# ============================================================
# CATÉGORIE F1 — Gérer les comptes (authentification) → ce fichier
# ============================================================

def test_login_ok_renvoie_token(client_http, session_test):
    """Un utilisateur existant + bon mot de passe → 200 + token JWT présent."""
    from werkzeug.security import generate_password_hash
    from app.modelsSQLAlchemy import User
    session_test.add(User(email="a@b.c", password_hash=generate_password_hash("secret"),
                          first_name="A", last_name="B", role="client"))
    session_test.commit()
    r = client_http.post("/api/auth/login", json={"email": "a@b.c", "password": "secret"})
    assert r.status_code == 200
    assert "token" in r.get_json()          # le token est bien présent dans la réponse


def test_login_mauvais_mot_de_passe_401(client_http, session_test):
    """Bon email mais mauvais mot de passe → 401 (même message si email inconnu)."""
    from werkzeug.security import generate_password_hash
    from app.modelsSQLAlchemy import User
    session_test.add(User(email="a@b.c", password_hash=generate_password_hash("secret"),
                          first_name="A", last_name="B", role="client"))
    session_test.commit()
    r = client_http.post("/api/auth/login", json={"email": "a@b.c", "password": "faux"})
    assert r.status_code == 401             # mauvais identifiants → 401


# ============================================================
# CATÉGORIE F4 — Sécuriser les accès (401/403) → ce fichier
# ============================================================

def test_token_invalide_401(client_http):
    """Un token truqué (mauvaise signature) est refusé → 401."""
    r = client_http.post("/api/produits", json={"name": "PC"},
                         headers={"Authorization": "Bearer <token_truque>"})
    assert r.status_code == 401


def test_token_expire_401(client_http):
    """Un token signé mais EXPIRÉ (exp passée) est refusé → 401."""
    # On forge un token expiré (signé avec la bonne clé, exp dans le passé)
    token_expire = jwt.encode(
        {"user_id": 1, "role": "admin", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
        SECRET_KEY, algorithm=ALGO)
    r = client_http.post("/api/produits", json={"name": "PC"},
                         headers={"Authorization": f"Bearer {token_expire}"})
    assert r.status_code == 401
