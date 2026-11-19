# ÉTAPE 5 appliquée à DigiMarket — NIVEAU 🥉 DÉBUTANT (conception des tests)

⏱️ **~1 h — moyenne** (ici seulement le niveau 🥉)

**Principe** : on conçoit les tests à partir de **ce qui a été créé en étape 4** (`etape4-conception-debutant.md`), pas avant.
**Règle du test** : un test = **une fonction/classe testée + UN scénario + le résultat attendu**, avec un **nom explicite** qui dit le scénario et le résultat.

## Niveau 🥉 : UN seul test unitaire, sur le fil rouge « S'inscrire »

| Élément créé (étape 4) | Type de test | Nom du test | Scénario | Résultat attendu |
|---|---|---|---|---|
| route `POST /api/auth/register` | unitaire (de la route) | `test_register_email_deja_utilise` | on inscrit un email, puis on réessaie avec le **même email** | **`409`** + JSON `{"erreur": "email déjà utilisé"}` |

### Récap — tests prévus par fonction métier

**F1 — Gérer les comptes** (auth) : 1 test unitaire → `tests/test_auth.py` : `test_register_email_deja_utilise` (409).

## Les tests (extraits, avec commentaires)

```python
# ============================================================
# CATÉGORIE F1 — Gérer les comptes (authentification) → fichier : tests/test_auth.py
# ============================================================
# tests/test_auth.py
import pytest
from app import app, session          # l'app Flask + la session SQLAlchemy (votre style)
from app.modelsSQLAlchemy import Base, User

@pytest.fixture
def client():
    """Crée un client de test Flask avec une base SQLite temporaire (en mémoire)."""
    app.config["TESTING"] = True                     # mode test : pas de vrai serveur
    engine = create_engine("sqlite:///:memory:")    # base en mémoire, jetable
    Base.metadata.create_all(engine)                 # crée la table users
    yield app.test_client()                          # le client qui appelle les routes
    Base.metadata.drop_all(engine)                   # nettoyage après le test

def test_register_email_deja_utilise(client):
    """Scénario : inscrire 2 fois le même email → la 2e fois doit échouer en 409."""
    # 1er appel : l'inscription fonctionne → 201
    r1 = client.post("/api/auth/register", json={
        "email": "a@b.c", "password": "secret", "first_name": "A", "last_name": "B"
    })
    assert r1.status_code == 201                     # assert = vérifie le résultat attendu

    # 2e appel avec le MÊME email → doit échouer → 409 (conflit, car email unique)
    r2 = client.post("/api/auth/register", json={
        "email": "a@b.c", "password": "autre", "first_name": "A", "last_name": "B"
    })
    assert r2.status_code == 409                     # le résultat attendu du test
    assert r2.get_json()["erreur"] == "email déjà utilisé"
```

💡 **Pourquoi ce test ?** Parce que l'étape 4 a prévu le cas d'erreur `409` (email déjà pris, contrainte `unique`) : le test prouve que la route le renvoie bien.

## Matrice élément × type de test (niveau 🥉 = 1 cellule)

| Fonction métier | Objet(s) | Élément testé (étape 4 🥉) | Unitaire | Intégration (route+base) | Nom du fichier |
|---|---|---|---|---|---|
| **F1** Gérer les comptes | `User` | `POST /api/auth/register` | ✅ `test_register_email_deja_utilise` | (niveau 🥈) | `tests/test_auth.py` |

---

✅ **Checklist étape 5 (niveau 🥉)** :
- [x] la route créée a son test unitaire prévu ;
- [x] le test a un nom explicite (scénario + résultat attendu : 409).

⚠️ **Piège évité** : écrire les tests à la toute fin — ils ne seraient jamais faits.

🧰 **Bonnes pratiques à ce stade** :
- le test fait partie de la Definition of Done (étape 6) ;
- README : section « Comment tester » = `pytest` ;
- commit Git de cette étape (ce push).

🧵 **Fil rouge** : le test du fil rouge est `test_register_email_deja_utilise` → attend **409**.

❓ **Auto-évaluation** :
1. Un test = quoi exactement (les 3 ingrédients) ?
2. Pourquoi le nom `test_register_email_deja_utilise` est-il explicite ?
3. Pourquoi concevoir les tests APRÈS l'étape 4 et pas avant ?

📝 **À retenir (3 lignes)** :
1) Un test = 1 élément testé + 1 scénario + 1 résultat attendu, nommé explicitement.
2) Niveau 🥉 = 1 test unitaire sur le fil rouge.
3) `pytest` lance tous les tests ; on les écrit à chaque incrément (étape 6), pas à la fin.

---
*Étape 5 niveau 🥉 ✅. En attente de votre accord pour l'étape 6 niveau 🥉 (backlog + premier code : `app.py`, `modelsSQLAlchemy.py`, `routes/auth.py`, `requirements.txt`, le test).*
