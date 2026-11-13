"""
app.py — Point d'entrée de l'API DigiMarket (niveau 🥉).

Flask + SQLAlchemy pur : on crée l'app, on enregistre les blueprints,
puis on lance le serveur.

Niveau 🥉 : blueprint auth (POST /api/auth/register).
Niveau 🥈 : + blueprint produits (F2 : /api/produits, /api/categories) + données de démo catalogue.

Lancer depuis la racine du projet :  python -m app.app

Pourquoi app.py n'a pas les routes directement ? app.py est l'ASSEMBLAGE :
il crée l'app (Flask) et enregistre les blueprints (register_blueprint).
Les endpoints vivent dans routes/*.py (un blueprint par domaine fonctionnel,
comme l'exige le CDC) — ainsi app.py reste petit et chaque domaine a son fichier
(ici routes/auth.py, plus tard routes/produits.py, routes/commandes.py).
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
# Flask : sert à créer l'application, UNE SEULE FOIS, ici : app = Flask(__name__)
from flask import Flask

# session partagée (module db.py — tout le monde passe par db.py pour éviter
# l'import circulaire : app.py importe routes/auth.py, donc auth.py ne peut pas
# importer app.py)
from app.db import session
# modèles (définis dans modelsSQLAlchemy.py) : User (🥉), Category + Product (🥈)
from app.modelsSQLAlchemy import User, Category, Product
# hachage du mot de passe de démo (werkzeug, inclus avec Flask)
from werkzeug.security import generate_password_hash

# ------------------------------------------------------------------
# Création de l'application Flask
# ------------------------------------------------------------------
app = Flask(__name__)

# ------------------------------------------------------------------
# Blueprints (routes) — un par fonction métier (4.8)
# ------------------------------------------------------------------
# auth_bp : blueprint de routes/auth.py — F1 « Gérer les comptes »
#   🥉 POST /api/auth/register (inscription) · 🥈 POST /api/auth/login (token JWT)
from app.routes.auth import auth_bp
# produits_bp : blueprint de routes/produits.py — F2 « Gérer le catalogue » (AJOUT 🥈)
#   GET /api/produits[/<id>] (public) · POST/PUT/DELETE (admin) · POST /api/categories
#   Pourquoi un 2e blueprint ? Chaque domaine fonctionnel a son fichier (CDC) :
#   app.py ne fait qu'assembler.
from app.routes.produits import produits_bp
# register_blueprint : enregistre les routes du blueprint dans l'app
# → accessibles sous /api/auth/... et /api/produits, /api/categories
app.register_blueprint(auth_bp)
app.register_blueprint(produits_bp)

# ------------------------------------------------------------------
# Données de DÉMO (si la base est vide) : 🥉 compte admin · 🥈 + catalogue
# ------------------------------------------------------------------
def init_sample_data():
    """Ajoute les données de DÉMO si la table users est vide.

    🥉 : un compte admin (admin@digimarket.fr) pour se connecter tout de suite.
    🥈 : + 1 catégorie + 2 produits (catalogue visible sans rien créer).

    Utilité : avoir un compte prêt pour essayer l'API À LA MAIN
    (curl, navigateur, Thunder Client) sans passer par l'inscription.
    Ce sont des données factices, PAS des tests automatisés
    (les vrais tests sont dans tests/ et lancés avec pytest).
    """
    if session.query(User).count() == 0:
        # --- Compte admin de démo (pour se connecter tout de suite via /login) ---
        # Mot de passe de démo : "admin123" (haché pour de vrai, comme un vrai compte)
        admin = User(
            email="admin@digimarket.fr",
            password_hash=generate_password_hash("admin123"),
            first_name="Admin",
            last_name="Digi",
            role="admin",
        )
        session.add(admin)
        # --- Niveau 🥈 : catégorie + 2 produits de démo (catalogue visible tout de suite) ---
        cat = Category(name="Informatique")
        session.add(cat)
        session.flush()                     # donne un id à la catégorie avant les produits (FK)
        session.add(Product(name="PC portable", description="14 pouces, 16 Go RAM",
                            price=899.99, stock=10, category_id=cat.id))
        session.add(Product(name="Clavier mécanique", description="Switchs silencieux",
                            price=79.90, stock=25, category_id=cat.id))
        session.commit()
        print("Données de démo initialisées (admin + catalogue).")

# ------------------------------------------------------------------
# Point d'entrée : lance le serveur Flask
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Ce bloc ne s'exécute QUE au lancement direct (python -m app.app) :
    # quand le fichier est importé ailleurs (ex. tests : from app.app import app),
    # __name__ vaut "app.app" et non "__main__" → le bloc est ignoré.
    # → les données de démo sont créées dans la vraie base UNIQUEMENT au
    #   démarrage du serveur, jamais pendant les tests (base en mémoire).
    init_sample_data()
    app.run(debug=True)
