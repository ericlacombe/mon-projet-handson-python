"""
tests/test_auth.py — Tests F1 « Gérer les comptes » (niveau 🥉, fil rouge « S'inscrire »).

Conçus à l'étape 5 🥉 (voir docs/etape5-tests-debutant.md). Lancer depuis la racine :  pytest
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
# pytest : le lanceur de tests (fixture @pytest.fixture, exécution avec `pytest`)
import pytest
# create_engine : crée un moteur SQLite EN MÉMOIRE (sqlite:///:memory:)
from sqlalchemy import create_engine
# sessionmaker : fabrique de sessions (ici pour la base de test en mémoire)
from sqlalchemy.orm import sessionmaker

# app : l'application Flask créée dans app/app.py (le point d'entrée)
from app.app import app
# Base (pour create_all/drop_all) et User (le modèle) définis dans modelsSQLAlchemy.py
from app.modelsSQLAlchemy import Base, User
# auth_module = le module routes/auth.py importé sous ce nom.
# Il sert de "poignée" : on va remplacer SA session (celle de db.py, liée à la
# vraie base digimarket.db) par une session de test en mémoire — comme ça,
# les session.add/commit de register() écrivent dans la base de TEST,
# jamais dans la vraie base.
import app.routes.auth as auth_module


@pytest.fixture
def client_http():
    """Client HTTP de test Flask + base SQLite en mémoire (jetable à chaque test).

    ⚠️ "client_http" = le client HTTP qui appelle l'API — PAS le rôle "Client"
    de la matrice des rôles (étape 1).

    Pourquoi une FONCTION avec @pytest.fixture ?
    - @pytest.fixture = « fabrique quelque chose AVANT chaque test » ;
    - la fonction prépare l'environnement (base en mémoire, session de test,
      mode TESTING) puis YIELD le client prêt à l'emploi ;
    - grâce au paramètre `def test_...(client_http):`, pytest injecte
      automatiquement ce client dans le test.
    """
    engine = create_engine("sqlite:///:memory:")   # base en RAM, rien sur le disque
    Base.metadata.create_all(engine)                # crée la table users
    TestSession = sessionmaker(bind=engine)
    # On branche la session de TEST dans le module routes/auth :
    # la route register() utilisera CETTE session (base en mémoire),
    # pas la vraie session de app/db.py
    auth_module.session = TestSession()

    app.config["TESTING"] = True                    # mode test : pas de vrai serveur
    # app.test_client() = le "navigateur/curl simulé" fourni par Flask :
    # c'est LUI qui fait les appels client_http.post("/api/auth/register", ...)
    yield app.test_client()

    Base.metadata.drop_all(engine)                  # nettoyage après le test


# Scénario : inscrire 2 fois le MÊME email → la 2e fois échoue. Résultat attendu : 409 + JSON erreur.
def test_register_email_deja_utilise(client_http):
    """Scénario testé : inscrire 2 fois le même email → la 2e fois échoue en 409.

    Règle du test (étape 5) : 1 élément testé (la route POST /api/auth/register)
    + UN scénario + le résultat attendu (409) — le nom du test dit tout ça.
    """
    # Le corps JSON envoyé à la route = les "entrées" du contrat d'API (étape 4)
    payload = {
        "email": "a@b.c",
        "password": "secret",
        "first_name": "Alice",
        "last_name": "Martin",
    }

    # ------------------------------------------------------------------
    # PARTIE 1 — le scénario du test : email déjà utilisé → 409
    # ------------------------------------------------------------------

    # 1er appel : inscription OK → 201 Created
    r1 = client_http.post("/api/auth/register", json=payload)
    # assert = vérifie le résultat attendu ; si faux, le test échoue ici
    assert r1.status_code == 201

    # 2e appel, MÊME email → doit échouer → 409 (conflit, email unique)
    r2 = client_http.post("/api/auth/register", json=payload)
    assert r2.status_code == 409
    # le corps de la réponse d'erreur est bien en JSON avec le bon message
    assert r2.get_json()["error"] == "email déjà utilisé"

    # ------------------------------------------------------------------
    # PARTIE 2 — vérification séparée : la création de l'objet User en base
    # (ce que register() a fait : session.add + commit)
    # ------------------------------------------------------------------
    assert auth_module.session.query(User).count() == 1     # exactement 1 utilisateur créé
    user = auth_module.session.query(User).filter_by(email="a@b.c").first()
    assert user is not None                                 # l'objet User existe bien en base
    assert user.role == "client"                            # rôle par défaut à la création
    assert user.password_hash != "secret"                   # mot de passe haché, jamais en clair
