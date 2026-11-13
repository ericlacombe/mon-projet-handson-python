# ÉTAPE 5 appliquée à DigiMarket — NIVEAU 🥈 INTERMÉDIAIRE (conception des tests)

**Principe** : tests conçus à partir de l'étape 4 niveau 🥈 (`etape4-intermediaire.md`).
**Niveau 🥈 = test unitaire pour chaque fonction/classe + premiers tests d'intégration (route + base + sécurité).**
F3 (commandes) n'est PAS testée ici (réservée au 🥇).

## Matrice élément × type de test (niveau 🥈)

> 💡 **À quoi sert cette matrice ?** Elle croise chaque **élément créé à l'étape 4**
> (colonne « Élément testé ») avec les **types de test** possibles (unitaire / intégration),
> pour ne rien oublier. Règles de remplissage :
> - 1ʳᵉ colonne **Fonction métier**, 2ᵉ **Objet(s)** (convention étape 4) ;
> - ✅ = test prévu ; « — » = pas de test de ce type pour cet élément ;
> - unitaire = on teste la fonction/classe seule (sans route) ; intégration = on teste
>   la route complète (requête HTTP → base → réponse, y compris la sécurité 401/403).

| Fonction métier | Objet(s) | Élément testé (étape 4 🥈) | Unitaire | Intégration (route+base+sécurité) |
|---|---|---|---|---|
| **F1+F4** (auth) | `User` → token | `POST /api/auth/login` | — | ✅ `test_login_ok_renvoie_token`, `test_login_mauvais_mot_de_passe_401` |
| **F4** | token (donnée temporaire, 4.2) | `security.creer_token / verifier_token` | ✅ `test_token_invalide_401`, `test_token_expire_401` | ✅ (via login) |
| **F2** (+F4) | `Product`, `Category` | CRUD `/api/produits` | — | ✅ `test_creer_produit_sans_token_401`, `test_creer_produit_client_403`, `test_creer_produit_admin_201`, `test_creer_produit_prix_negatif_400` |
| **F2** (+F4) | `Category` | `POST /api/categories` (création catégorie) | ✅ `test_categorie_objet_attributs` | ✅ `test_creer_categorie_admin_201`, `test_categorie_nom_unique_409`, `test_categorie_sans_token_401` |
| **F2** | `Product` | `GET /api/produits` (public, recherche) | — | ✅ `test_liste_produits_avec_recherche` |

### Récap — tests prévus par fonction métier (F1 / F2 séparés de F4 sécurité)

**F1 — Gérer les comptes** (auth) :

| Test | Vérifie | Code |
|---|---|---|
| `test_login_ok_renvoie_token` | login OK → token JWT émis | 200 |
| `test_login_mauvais_mot_de_passe_401` | mauvais mot de passe | 401 |

**F2 — Gérer le catalogue** (produits + catégories) :

| Test | Vérifie | Code |
|---|---|---|
| `test_creer_produit_admin_201` | création produit (admin) | 201 |
| `test_creer_produit_sans_token_401` | route protégée sans token | 401 |
| `test_creer_produit_client_403` | token client sur route admin | 403 |
| `test_creer_produit_prix_negatif_400` | contrainte 4.3 : prix >= 0 | 400 |
| `test_liste_produits_avec_recherche` | GET public + recherche `?q=` | 200 |
| `test_creer_categorie_admin_201` | création catégorie (admin) | 201 |
| `test_categorie_nom_unique_409` | contrainte 4.3 : nom catégorie unique | 409 |
| `test_categorie_sans_token_401` | route catégories sans token | 401 |
| `test_categorie_objet_attributs` (unitaire) | objet `Category` : id, name, products | — |

**F4 — Sécuriser les accès** (séparé des F1/F2 : c'est du contrôle d'accès, pas de la logique métier) :

| Test | Vérifie | Code |
|---|---|---|
| `test_token_invalide_401` | token truqué | 401 |
| `test_token_expire_401` | token expiré | 401 |

## Les tests (extraits, avec commentaires)

```python
# tests/test_security.py — tests de la sécurité (4.11)
def test_login_ok_renvoie_token(client_http, session_test):
    # Un user existe en base (fixture) → login renvoie 200 + un token JWT
    r = client_http.post("/api/auth/login", json={"email": "a@b.c", "password": "secret"})
    assert r.status_code == 200
    assert "token" in r.get_json()          # le token est bien présent dans la réponse

def test_login_mauvais_mot_de_passe_401(client_http):
    r = client_http.post("/api/auth/login", json={"email": "a@b.c", "password": "faux"})
    assert r.status_code == 401             # mauvais identifiants → 401

def test_token_expire_401(client_http):
    # Token signé avec une date d'expiration passée → 401 (expiré)
    r = client_http.post("/api/produits", json={"name": "PC"},
                         headers={"Authorization": "Bearer <token_expire>"})
    assert r.status_code == 401

def test_creer_produit_sans_token_401(client_http):
    # Sans header Authorization → le décorateur login_required renvoie 401
    r = client_http.post("/api/produits", json={"name": "PC", "price": 999, "stock": 5, "category_id": 1})
    assert r.status_code == 401

def test_creer_produit_client_non_admin_403(client_http, token_client):
    # Token valide mais rôle "client" → admin_required renvoie 403
    r = client_http.post("/api/produits", json={...},
                         headers={"Authorization": f"Bearer {token_client}"})
    assert r.status_code == 403

def test_creer_produit_admin_201(client_http, token_admin):
    # Token admin → création OK → 201
    r = client_http.post("/api/produits", json={"name": "PC", "price": 999, "stock": 5, "category_id": 1},
                         headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 201

def test_creer_produit_prix_negatif_400(client_http, token_admin):
    # 4.3 : validation prix >= 0 → 400
    r = client_http.post("/api/produits", json={"name": "X", "price": -5, "stock": 1, "category_id": 1},
                         headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 400

# (test de la transition d'état Order.valider(), partie 4.6, au niveau 🥇 avec F3 — pas ici)
# tests/test_produits.py — tests dédiés à l'objet Category (F2)
def test_categorie_objet_attributs():
    c = Category(name="Informatique")
    assert c.name == "Informatique"
    assert hasattr(c, "products")          # relation 1—N (4.5)

def test_creer_categorie_admin_201(client_http, token_admin):
    r = client_http.post("/api/categories", json={"name": "Informatique"},
                         headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 201

def test_categorie_nom_unique_409(client_http, token_admin):
    # 4.3 : unicité du nom de catégorie → 2e création = 409
    client_http.post("/api/categories", json={"name": "Info"}, headers={"Authorization": f"Bearer {token_admin}"})
    r = client_http.post("/api/categories", json={"name": "Info"}, headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 409

def test_categorie_sans_token_401(client_http):
    r = client_http.post("/api/categories", json={"name": "Info"})
    assert r.status_code == 401

```

💡 **Règle du test** : 1 élément + 1 scénario + résultat attendu, nom explicite (`test_creer_produit_sans_token_401`).

---

✅ **Checklist étape 5 (niveau 🥈)** :
- [x] test unitaire pour chaque fonction/classe 🥈 (token) ; (transition 4.6 → niveau 🥇 avec F3)
- [x] tests d'intégration route + base + sécurité (login, 401/403, CRUD produits, validation 400) ;
- [x] matrice élément × type à jour ;
- [x] README « Comment tester » à jour (`pytest` lance tout).

🧰 **Bonnes pratiques** : test = partie de la DoD · `pytest` à chaque incrément · commit.

🧵 **Fil rouge 🥈** : « se connecter » (login → token) et « créer un produit en admin » (201, sinon 401/403).

❓ **Auto-évaluation** : 1) Différence unitaire / intégration ? 2) Pourquoi 401 vs 403 ? 3) Pourquoi F3 n'est pas testée ici ?

📝 **À retenir (3 lignes)** : 1) 🥈 = unitaires par élément + intégration avec sécurité. 2) 401 = pas authentifié, 403 = pas le bon rôle. 3) On teste APRÈS l'étape 4, à chaque incrément.

---
*Conception des tests 🥈 prête. Prochaine étape (avec validation) : étape 6 niveau 🥈 — backlog puis code (security.py, login, produits).*
