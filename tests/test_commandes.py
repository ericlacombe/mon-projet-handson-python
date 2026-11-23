"""
tests/test_commandes.py — Tests F3 « Gérer les commandes » (niveau 🥇).

Conçus à l'étape 5 🥇 (matrice : docs/etape5-tests-confirme.md, fichier cible F3).
Chaque test = 1 scénario + le résultat attendu (code HTTP ou valeur), nommé explicitement.
Lancer depuis la racine :  pytest
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
# pytest : le lanceur de tests (fixtures via conftest.py : session_test, client_http,
#          token_admin, token_client — base en mémoire, jamais digimarket.db)
import pytest

# modèles + fonctions pures testées
from app.modelsSQLAlchemy import Base, Order, OrderItem, Product, Category

# ============================================================
# CATÉGORIE F3 — Gérer les commandes (order, statut, stock) → ce fichier
# ============================================================


# ------------------------------------------------------------------
# Helper : créer une catégorie + un produit en base de test (via l'admin)
# ------------------------------------------------------------------
def _creer_produit(client_http, token_admin, session_test, stock=5, price=10.0):
    """Crée la catégorie 'PC' + un produit via les routes admin → renvoie le product_id."""
    H = {"Authorization": f"Bearer {token_admin}"}
    client_http.post("/api/categories", json={"name": "PC"}, headers=H)
    r = client_http.post("/api/produits",
                         json={"name": "PC Gamer", "price": price, "stock": stock,
                               "category_id": 1},
                         headers=H)
    assert r.status_code == 201            # produit créé en base de test
    return r.get_json()["id"]               # id du produit pour les commandes


# ==================================================================
# TESTS UNITAIRES (fonctions pures 4.9 + cycle de vie 4.6, sans route)
# ==================================================================

# Scénario : en_attente -> validée est autorisé. Attendu : statut changé.
def test_transition_autorisee():
    o = Order(statut="en_attente")
    o.changer_statut("validée")
    assert o.statut == "validée"           # transition appliquée (4.6)

# Scénario : validée -> livrée est INTERDIT (4.6). Attendu : ValueError.
def test_transition_interdite():
    o = Order(statut="validée")
    with pytest.raises(ValueError):
        o.changer_statut("livrée")

# Scénario : 2 lignes (2x10 + 1x5). Attendu : total = 25.
def test_calculer_total():
    from app.utils import calculer_total
    order = Order()
    order.items = [OrderItem(quantite=2, prix_unitaire=10.0),
                   OrderItem(quantite=1, prix_unitaire=5.0)]
    assert calculer_total(order) == 25.0  # Σ qte×prix = 2×10 + 1×5

# Scénario : stock suffisant (5 >= 2). Attendu : True.
def test_verifier_stock_ok():
    from app.utils import verifier_stock
    assert verifier_stock(Product(stock=5), 2) is True   # 5 >= 2 : assez de stock

# Scénario : stock insuffisant (5 < 9) ou qte <= 0. Attendu : False / ValueError.
def test_verifier_stock_insuffisant():
    from app.utils import verifier_stock
    assert verifier_stock(Product(stock=5), 9) is False
    with pytest.raises(ValueError):
        verifier_stock(Product(stock=5), 0)


# ==================================================================
# TESTS D'INTÉGRATION — POST /api/commandes
# ==================================================================

# Scénario : client connecté passe commande valide. Attendu : 201 + total + en_attente.
def test_creer_commande_201(client_http, token_client, session_test, token_admin):
    pid = _creer_produit(client_http, token_admin, session_test, stock=5)
    H = {"Authorization": f"Bearer {token_client}"}
    r = client_http.post("/api/commandes",
                         json={"address_livraison": "1 rue de Paris",
                               "items": [{"product_id": pid, "quantite": 2}]},
                         headers=H)
    assert r.status_code == 201
    body = r.get_json()
    assert body["total"] == 20.0 and body["statut"] == "en_attente"  # 2×10, statut initial

# Scénario : quantité > stock. Attendu : 400.
def test_stock_insuffisant_400(client_http, token_client, session_test, token_admin):
    pid = _creer_produit(client_http, token_admin, session_test, stock=5)
    H = {"Authorization": f"Bearer {token_client}"}
    r = client_http.post("/api/commandes",
                         json={"address_livraison": "x",
                               "items": [{"product_id": pid, "quantite": 99}]},
                         headers=H)
    assert r.status_code == 400

# Scénario : quantite = 0 (contrainte 4.3). Attendu : 400.
def test_quantite_zero_400(client_http, token_client, session_test, token_admin):
    pid = _creer_produit(client_http, token_admin, session_test)
    H = {"Authorization": f"Bearer {token_client}"}
    r = client_http.post("/api/commandes",
                         json={"address_livraison": "x",
                               "items": [{"product_id": pid, "quantite": 0}]},
                         headers=H)
    assert r.status_code == 400

# Scénario : pas de token. Attendu : 401.
def test_sans_token_401(client_http):
    r = client_http.post("/api/commandes",
                         json={"address_livraison": "x", "items": [{"product_id": 1, "quantite": 1}]})
    assert r.status_code == 401


# ==================================================================
# TESTS D'INTÉGRATION — GET /api/commandes[/<id>]
# ==================================================================

def _commande(client_http, token_client, session_test, token_admin):
    """Crée une commande pour le client de test → renvoie son id."""
    pid = _creer_produit(client_http, token_admin, session_test)
    H = {"Authorization": f"Bearer {token_client}"}
    r = client_http.post("/api/commandes",
                         json={"address_livraison": "x", "items": [{"product_id": pid, "quantite": 1}]},
                         headers=H)
    return r.get_json()["id"]

# Scénario : le client retrouve SA commande dans la liste. Attendu : 200 + 1 élément.
def test_liste_mes_commandes(client_http, token_client, session_test, token_admin):
    _commande(client_http, token_client, session_test, token_admin)
    H = {"Authorization": f"Bearer {token_client}"}
    r = client_http.get("/api/commandes", headers=H)
    assert r.status_code == 200 and len(r.get_json()) == 1   # une seule commande (la sienne)

# Scénario : un AUTRE client lit la commande d'un autre. Attendu : 403 (4.11 client_propriétaire).
def test_commande_autre_client_403(client_http, token_client, session_test, token_admin):
    oid = _commande(client_http, token_client, session_test, token_admin)
    # un 2e client s'inscrit + se loggue
    client_http.post("/api/auth/register", json={"email": "c2@x.fr", "password": "x", "first_name": "C", "last_name": "2"})
    t2 = client_http.post("/api/auth/login", json={"email": "c2@x.fr", "password": "x"}).get_json()["token"]
    r = client_http.get(f"/api/commandes/{oid}", headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403

# Scénario : commande inexistante. Attendu : 404.
def test_commande_inexistante_404(client_http, token_admin):
    r = client_http.get("/api/commandes/999", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 404


# ==================================================================
# TESTS D'INTÉGRATION — PATCH /api/commandes/<id>/statut
# ==================================================================

# Scénario : l'admin valide la commande. Attendu : 200 + statut validée + stock décrémenté.
def test_patch_admin_valide_200(client_http, token_client, session_test, token_admin):
    oid = _commande(client_http, token_client, session_test, token_admin)
    r = client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "validée"},
                          headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200 and r.get_json()["statut"] == "validée"  # admin a validé

# Scénario : le client PROPRIÉTAIRE annule sa commande. Attendu : 200 + annul\u00e9e.
def test_patch_client_proprietaire_annule_200(client_http, token_client, session_test, token_admin):
    oid = _commande(client_http, token_client, session_test, token_admin)
    r = client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "annulée"},
                          headers={"Authorization": f"Bearer {token_client}"})
    assert r.status_code == 200 and r.get_json()["statut"] == "annulée"  # proprio a annulé

# Scénario : transition interdite (en_attente -> livrée, 4.6). Attendu : 400.
def test_patch_transition_interdite_400(client_http, token_client, session_test, token_admin):
    oid = _commande(client_http, token_client, session_test, token_admin)
    r = client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "livrée"},
                          headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 400

# Scénario : un client NON propriétaire tente de modifier. Attendu : 403.
def test_patch_client_non_proprietaire_403(client_http, token_client, session_test, token_admin):
    oid = _commande(client_http, token_client, session_test, token_admin)
    client_http.post("/api/auth/register", json={"email": "c3@x.fr", "password": "x", "first_name": "C", "last_name": "3"})
    t3 = client_http.post("/api/auth/login", json={"email": "c3@x.fr", "password": "x"}).get_json()["token"]
    r = client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "annulée"},
                          headers={"Authorization": f"Bearer {t3}"})
    assert r.status_code == 403


# ==================================================================
# EFFETS DE BORD SUR LE STOCK (validation décrémente, annulation restitue)
# ==================================================================

# Scénario : validation d'une commande de 2 unités (stock 5). Attendu : stock = 3.
def test_stock_decremente_a_validation(client_http, token_client, session_test, token_admin):
    pid = _creer_produit(client_http, token_admin, session_test, stock=5)
    H = {"Authorization": f"Bearer {token_client}"}
    oid = client_http.post("/api/commandes",
                           json={"address_livraison": "x", "items": [{"product_id": pid, "quantite": 2}]},
                           headers=H).get_json()["id"]
    client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "validée"},
                      headers={"Authorization": f"Bearer {token_admin}"})
    assert session_test.get(Product, pid).stock == 3   # 5 - 2 : décrémenté à la validation

# Scénario : annulation d'une commande validée de 2 unités. Attendu : stock restitué = 5.
def test_stock_restitue_a_annulation(client_http, token_client, session_test, token_admin):
    pid = _creer_produit(client_http, token_admin, session_test, stock=5)
    H = {"Authorization": f"Bearer {token_client}"}
    oid = client_http.post("/api/commandes",
                           json={"address_livraison": "x", "items": [{"product_id": pid, "quantite": 2}]},
                           headers=H).get_json()["id"]
    Ha = {"Authorization": f"Bearer {token_admin}"}
    client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "validée"}, headers=Ha)
    client_http.patch(f"/api/commandes/{oid}/statut", json={"statut": "annulée"}, headers=Ha)
    assert session_test.get(Product, pid).stock == 5   # restitué à l'annulation
