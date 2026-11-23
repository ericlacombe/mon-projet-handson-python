"""
modelsSQLAlchemy.py — Modèles SQLAlchemy (ORM) pour DigiMarket.

Niveau 🥉 : table users (fil rouge « S'inscrire »).
Niveau 🥈 : + tables categories et products (relation 1—N, partie 4.5).
Niveau 🥇 : + tables orders et order_items (relations N—1/1—N, cycle de vie 4.6).
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
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from datetime import datetime, timezone
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
    # Rôle : 'client' par défaut, 'admin' pour les administrateurs.
    # PROTECTION (chaîne de protection, docs/etape4-intermediaire.md §4.11) :
    # 'client' par défaut à l'inscription, 'admin' UNIQUEMENT pour le compte
    # de démo — aucune route publique ne change ce rôle (register force 'client',
    # voir routes/auth.py). Le rôle est ensuite embarqué SIGNÉ dans le token JWT
    # (voir security.py) : un client ne peut pas se faire passer pour admin.
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
# Niveau 🥇 — Objets F3 (partie 4.5 + 4.6) : Order 1—N OrderItem,
# Order N—1 User, OrderItem N—1 Product
# ------------------------------------------------------------------

class Order(Base):
    # Nom de la table : orders (pluriel)
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    # Côté "N" vers users (4.5) : FK vers l'acheteur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Adresse de livraison figée à la commande
    address_livraison = Column(Text, nullable=False)
    # Date de création (défaut = maintenant, UTC)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # Cycle de vie (4.6) : en_attente → validée → expédiée → livrée ; annulable depuis en_attente/validée
    statut = Column(String(20), nullable=False, default="en_attente")
    # Total calculé par calculer_total (4.9, app/utils.py) à la validation
    total = Column(Float, nullable=False, default=0.0)

    # RELATIONS (4.5), même style que Category/Product :
    # - user  : côté "N" vers users — relationship("User") + backref="orders"
    #           (crée user.orders : toutes les commandes de l'acheteur)
    # - items : côté "1" vers order_items — backref="order" (accès inverse item.order)
    # - lazy=True (défaut) : les lignes sont chargées seulement quand on y accède
    # - cascade="all, delete-orphan" : supprimer une commande supprime ses lignes
    user = relationship("User", backref="orders")
    items = relationship("OrderItem", backref="order", lazy=True,
                         cascade="all, delete-orphan")

    # ------------------------------------------------------------------
    # CYCLE DE VIE (partie 4.6) : transitions autorisées entre statuts
    # ------------------------------------------------------------------
    STATUTS = ("en_attente", "validée", "expédiée", "livrée", "annulée")
    # TRANSITIONS autorisées : (de, vers). Hors de là → ValueError (→ 400 côté route)
    TRANSITIONS = {
        "en_attente": {"validée", "annulée"},
        "validée":    {"expédiée", "annulée"},
        "expédiée":   {"livrée"},
        "livrée":     set(),
        "annulée":    set(),
    }

    def changer_statut(self, nouveau: str):
        """Change le statut si la transition est autorisée (4.6), sinon lève ValueError."""
        if nouveau not in self.STATUTS:
            raise ValueError(f"statut inconnu : {nouveau}")
        if nouveau not in self.TRANSITIONS.get(self.statut, set()):
            raise ValueError(f"transition interdite : {self.statut} → {nouveau}")
        self.statut = nouveau

    def __repr__(self):
        return f"<Order {self.id} ({self.statut}) user={self.user_id}>"


class OrderItem(Base):
    # Nom de la table : order_items (pluriel)
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    # FK vers la commande (côté "N" de Order 1—N OrderItem, 4.5)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    # FK vers le produit (N—1)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # Quantité — contrainte 4.3 : > 0 (validée côté route → 400)
    quantite = Column(Integer, nullable=False)
    # Prix unitaire FIGÉ à la commande (le prix du produit peut changer après)
    prix_unitaire = Column(Float, nullable=False)

    # RELATION (4.5) côté "N" vers products : backref="order_items" (product.order_items)
    product = relationship("Product", backref="order_items")

    def __repr__(self):
        return f"<OrderItem order={self.order_id} product={self.product_id} x{self.quantite}>"

# ------------------------------------------------------------------
# Schéma des tables (niveau 🥇 : users + categories + products + orders + order_items) :
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

#   orders  (user_id → users.id, FK)
#   ├── id                PK int
#   ├── user_id           FK int, obligatoire
#   ├── address_livraison text, obligatoire
#   ├── date_creation     datetime, défaut = maintenant (UTC)
#   ├── statut            string, défaut 'en_attente' (cycle 4.6)
#   └── total             float, défaut 0 (calculé par calculer_total, 4.9)
#
#   order_items  (order_id → orders.id, product_id → products.id, FK)
#   ├── id            PK int
#   ├── order_id      FK int, obligatoire
#   ├── product_id    FK int, obligatoire
#   ├── quantite      int, obligatoire (> 0 validé côté route, 4.3 → 400)
#   └── prix_unitaire float, obligatoire (figé à la commande)
