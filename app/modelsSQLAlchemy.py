"""
modelsSQLAlchemy.py — Modèles SQLAlchemy (ORM) pour DigiMarket.

Niveau 🥉 : table users (fil rouge « S'inscrire »).
Niveau 🥈 : + tables categories et products (relation 1—N, partie 4.5).
Ce fichier définit (sous forme de classes) les modèles des tables de la base SQL, importés par :
- app/app.py          (l'API Flask : point d'entrée, blueprints, endpoints)
- app/db.py           (moteur + session partagée, create_all)
- app/routes/auth.py  (les routes, ex. POST /api/auth/register)
- tests/test_auth.py  (les tests)
- app/script_crud.py  (script CRUD standalone : opérations en console, à créer si besoin)
Aucun code d'exécution : importer ce fichier ne déclenche aucune opération en base de données.
Même style que l'ancien projet (SQLAlchemy pur, pas Flask-SQLAlchemy).
"""

# ------------------------------------------------------------------
# Imports SQLAlchemy
# ------------------------------------------------------------------
# Column               : définit une colonne dans une table
# Integer, String, Text : types de données des colonnes
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

# declarative_base : fonction qui génère la classe de base des modèles
# (elle garde la "métadonnée" = la description de toutes les tables)
from sqlalchemy.orm import declarative_base

# ------------------------------------------------------------------
# Déclaration de la base des modèles
# ------------------------------------------------------------------
# declarative_base() crée une classe de base. Tous les modèles héritent de Base.
# En héritant de Base, chaque classe (= une table de la base) obtient :
# - le mapping ORM (SQLAlchemy sait que la classe = une table de la base)
# - la métadonnée (enregistrée dans Base.metadata)
# - les attributs magiques (ex: User.__table__, User.__mapper__)
# - la compatibilité session (les instances peuvent être ajoutées à une session)
Base = declarative_base()

# ------------------------------------------------------------------
# Définition du modèle
# ------------------------------------------------------------------

class User(Base):
    # Nom de la table dans la base de données (pluriel, comme l'ancien projet)
    __tablename__ = "users"

    # Identifiant unique du compte (clé primaire, auto-incrémenté)
    id = Column(Integer, primary_key=True)
    # Email — unique (UK) et obligatoire : un seul compte par email (CDC)
    email = Column(String(255), unique=True, nullable=False)
    # Mot de passe haché — JAMAIS en clair (on stocke seulement le hash)
    password_hash = Column(String(255), nullable=False)
    # Prénom / nom — obligatoires, limités à 100 caractères
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # Adresse — optionnelle (type Text = pas de limite de taille)
    address = Column(Text)
    # Rôle : 'client' par défaut, 'admin' pour les administrateurs
    role = Column(String(20), nullable=False, default="client")

    # Représentation textuelle de l'objet (affichée avec print())
    def __repr__(self):
        return f"<User {self.email}>"

# ------------------------------------------------------------------
# Niveau 🥈 — Objets en relation 1—N (partie 4.5) : Category 1—N Product
# ------------------------------------------------------------------

class Category(Base):
    # Nom de la table : categories (pluriel)
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    # Nom de la catégorie — unique (contrainte 4.3) et obligatoire
    name = Column(String(100), unique=True, nullable=False)

    # RELATION 1—N (4.5) : une catégorie a plusieurs produits.
    # - relationship("Product") : côté "1" de la relation (dans Category)
    # - backref="category" : crée automatiquement product.category (accès inverse)
    # - lazy=True (défaut) : les produits sont chargés seulement quand on y accède
    # - cascade="all, delete-orphan" : supprimer une catégorie supprime ses produits
    products = relationship("Product", backref="category", lazy=True,
                            cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    # Nom de la table : products (pluriel)
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    # Prix en euros — validé >= 0 côté route (contrainte 4.3 → erreur 400)
    price = Column(Float, nullable=False)
    # Stock disponible — validé >= 0 côté route (contrainte 4.3 → 400)
    stock = Column(Integer, nullable=False, default=0)

    # Côté "N" de la relation 1—N (4.5) : la clé étrangère vers categories.
    # - ForeignKey("categories.id") : référence la clé primaire de categories
    # - nullable=False : un produit DOIT appartenir à une catégorie
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    def __repr__(self):
        return f"<Product {self.name} ({self.price}€)>"

# ------------------------------------------------------------------
# Schéma des tables (niveau 🥈 : users + categories + products) :
# ------------------------------------------------------------------
#
#   users
#   ├── id            PK int, auto-incrémenté
#   ├── email         UK string, obligatoire
#   ├── password_hash string, obligatoire
#   ├── first_name    string, obligatoire
#   ├── last_name     string, obligatoire
#   ├── address       text, optionnel
#   └── role          string, défaut 'client'
#
# ------------------------------------------------------------------

#   categories
#   ├── id    PK int
#   └── name  UK string, obligatoire
#
#   products  (category_id → categories.id, FK)
#   ├── id          PK int
#   ├── name        string, obligatoire
#   ├── description text
#   ├── price       float, obligatoire  (>= 0 validé côté route)
#   ├── stock       int, défaut 0       (>= 0 validé côté route)
#   └── category_id FK int, obligatoire
#
