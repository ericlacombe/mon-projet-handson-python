"""
tests/test_produits.py — Tests F2 « Gérer le catalogue » (produits + catégories), niveau 🥈.

Fichier cible de la catégorie F2 (voir docs/etape5-tests-intermediaire.md).
Lancer depuis la racine :  pytest
"""
from app.modelsSQLAlchemy import Category

# ============================================================
# CATÉGORIE F2 — Gérer le catalogue (produits + catégories) → ce fichier
# ============================================================

def _headers(token):
    """Header Authorization pour un token JWT."""
    return {"Authorization": f"Bearer {token}"}


def _creer_categorie(session_test, name="Informatique"):
    cat = Category(name=name)
    session_test.add(cat)
    session_test.commit()
    return cat


def test_creer_produit_admin_201(client_http, session_test, token_admin):
    """Un admin crée un produit valide → 201."""
    _creer_categorie(session_test)
    r = client_http.post("/api/produits",
                         json={"name": "PC", "price": 999, "stock": 5, "category_id": 1},
                         headers=_headers(token_admin))
    assert r.status_code == 201


def test_creer_produit_sans_token_401(client_http):
    """Sans header Authorization → le décorateur admin_required renvoie 401."""
    r = client_http.post("/api/produits", json={"name": "PC", "price": 999, "category_id": 1})
    assert r.status_code == 401


def test_creer_produit_client_403(client_http, session_test, token_client):
    """Token valide mais rôle 'client' → 403 (authentifié mais pas admin)."""
    _creer_categorie(session_test)
    r = client_http.post("/api/produits",
                         json={"name": "PC", "price": 999, "stock": 5, "category_id": 1},
                         headers=_headers(token_client))
    assert r.status_code == 403


def test_creer_produit_prix_negatif_400(client_http, session_test, token_admin):
    """Contrainte 4.3 : price < 0 → 400 (validation côté route)."""
    _creer_categorie(session_test)
    r = client_http.post("/api/produits",
                         json={"name": "X", "price": -5, "stock": 1, "category_id": 1},
                         headers=_headers(token_admin))
    assert r.status_code == 400


def test_liste_produits_avec_recherche(client_http, session_test, token_admin):
    """GET /api/produits?q=pc → 200 et seul le produit correspondant remonté."""
    _creer_categorie(session_test)
    h = _headers(token_admin)
    client_http.post("/api/produits", json={"name": "PC portable", "price": 999, "stock": 5, "category_id": 1}, headers=h)
    client_http.post("/api/produits", json={"name": "Clavier", "price": 49, "stock": 20, "category_id": 1}, headers=h)
    r = client_http.get("/api/produits?q=pc")          # public : pas besoin de token
    assert r.status_code == 200
    assert len(r.get_json()) == 1 and "PC" in r.get_json()[0]["name"]


def test_creer_categorie_admin_201(client_http, token_admin):
    """Un admin crée une catégorie → 201."""
    r = client_http.post("/api/categories", json={"name": "Informatique"}, headers=_headers(token_admin))
    assert r.status_code == 201


def test_categorie_nom_unique_409(client_http, session_test, token_admin):
    """Contrainte 4.3 : nom de catégorie unique → 2e création = 409."""
    _creer_categorie(session_test, "Info")
    h = _headers(token_admin)
    r = client_http.post("/api/categories", json={"name": "Info"}, headers=h)
    assert r.status_code == 409


def test_categorie_sans_token_401(client_http):
    """POST /api/categories sans token → 401."""
    r = client_http.post("/api/categories", json={"name": "Info"})
    assert r.status_code == 401


def test_categorie_objet_attributs():
    """Test UNITAIRE de l'objet Category : attributs + relation 1—N (4.5)."""
    c = Category(name="Informatique")
    assert c.name == "Informatique"
    assert hasattr(c, "products")            # backref de la relation 1—N
