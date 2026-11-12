# ÉTAPE 4 appliquée à DigiMarket — NIVEAU 🥈 INTERMÉDIAIRE

⏱️ sur le niveau 🥈 (en plus du niveau 🥉 déjà fait)

**Rappel du principe** : on croise les résultats des étapes 1, 2 et 3. Règle à dire à voix haute : *« analyse → condition → si positif, ACTION de création »*, et *« si la condition est fausse, que se passe-t-il ? »*.

**Niveau 🥈 = niveau 🥉 + parties 4.3 (contraintes), 4.4 (relations), 4.6 (transitions simples), 4.11 (sécurité de base)**.
Le fil rouge 🥈 : **« un administrateur gère le catalogue (produits) »** + **« un utilisateur se connecte (JWT) »**.

> 📌 **Répartition des fonctions métier** (règle de complexité dans `methodologie.md`) :
> 🥈 = **F2 (catalogue) + F4 (sécurité JWT)** — objets avec relation 1—N, CRUD protégé par rôle.
> **F3 « Gérer les commandes » est réservée au niveau 🥇 confirmé** (changement d'état, cycle de vie, logique stock) — on ne la traite PAS ici.

---

## 4.3 — Contraintes & validations (condition : règle de validité sur un attribut ✅ → ACTION)

| Attribut | Règle | Où | Erreur |
|---|---|---|---|
| `users.email` | unique | contrainte base `unique=True` (déjà fait 🥉) | 409 |
| `categories.name` | unique | `unique=True` | 409 |
| `products.price` | >= 0 | validation dans la route | 400 |
| `products.stock` | >= 0 | validation dans la route | 400 |

## 4.4 — Relations entre objets (condition : deux objets liés ✅ → ACTION)

Du schéma ER (étape 3) — niveau 🥈 on ne garde que la relation utile à F2 (les relations Commande/LigneCommande = F3, réservées au 🥇) :

| Relation | Clé étrangère créée | `relationship` dans la classe |
|---|---|---|
| Categorie 1—N Produit | `products.category_id → categories.id` | `Category.products`, `Product.category` |

```python
# modelsSQLAlchemy.py (extrait 🥈) — ForeignKey et relationship
# Pourquoi ForeignKey maintenant ? Parce qu'il y a des RELATIONS entre tables (4.4)
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)   # UK : nom de catégorie unique

    # ------------------------------------------------------------------
    # RELATION 1—N : Categorie 1—N Produit (une catégorie a plusieurs produits)
    # ------------------------------------------------------------------
    # relationship("Product") dans Category définit la relation ORM entre Category et Product.
    # - backref="category" : crée automatiquement product.category (accès inverse :
    #   depuis un produit, on atteint sa catégorie — ex. mon_produit.category.name)
    # - lazy=True (défaut) : les produits sont chargés UNIQUEMENT quand on y accède
    #   (chargement différé, pas tout en mémoire d'un coup)
    # - cascade="all, delete-orphan" : supprimer une catégorie supprime aussi ses produits
    #   (sinon ils resteraient "orphelins", sans catégorie)
    products = relationship("Product", backref="category", lazy=True, cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)      # 4.3 : validé >= 0 côté route (400 sinon)
    stock = Column(Integer, nullable=False, default=0)
    # ------------------------------------------------------------------
    # Côté "N" de la relation : la clé étrangère
    # - ForeignKey("categories.id") : ce champ référence la PK de categories
    # - nullable=False : un produit DOIT appartenir à une catégorie (obligatoire)
    # ------------------------------------------------------------------
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
```

## 4.6 — Transitions d'état → niveau 🥇 confirmé

> ⚠️ La partie 4.6 (transitions d'état, ex. `Order.valider()`) concerne **F3 « Gérer les commandes »** : selon la règle de répartition par complexité (changement d'état = logique complexe), elle est traitée au **niveau 🥇 confirmé**, pas ici.

## 4.11 — Sécurité de base (condition : authentification/autorisation requise ✅ → ACTION)

Nouveau module `app/security.py` + bibliothèque **PyJWT** + fichier **`.env`** (jamais commité) :

```python
# app/security.py (extrait 🥈)
# Pourquoi un module séparé ? Toute la sécurité est regroupée ici (4.11) :
# hachage, création/vérification du token JWT, décorateurs de rôle.
import os, jwt                      # PyJWT ; os pour lire .env
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

SECRET_KEY = os.environ["SECRET_KEY"]   # lu depuis .env (jamais dans le code !)

def creer_token(user): ...              # jwt.encode({"user_id":..., "role":...}, SECRET_KEY)
def verifier_token(): ...               # décode + renvoie 401 si invalide/expiré
def login_required(f): ...             # décorateur : 401 si pas de token valide
def admin_required(f): ...             # décorateur : 403 si role != "admin"
```

Routes auth 🥈 : `POST /api/auth/register` (déjà fait) + **`POST /api/auth/login`** → renvoie `{ "token": "..." }` (vérifie le hash avec `check_password_hash`).

## 4.7 — Contrat d'API niveau 🥈 (les nouvelles routes)

| Méthode | Route | Accès | Entrée (JSON) | Sorties / codes |
|---|---|---|---|---|
| POST | `/api/auth/login` | Public | `{email, password}` | `200` + token JWT · `401` mauvais identifiants |
| GET | `/api/produits` | Public | query `?q=` (recherche) | `200` liste JSON |
| GET | `/api/produits/<id>` | Public | — | `200` · `404` |
| POST | `/api/produits` | **Admin** (token + rôle) | `{name, description, price, stock, category_id}` | `201` · `400` (prix<0…) · `401`/`403` |
| PUT | `/api/produits/<id>` | Admin | idem | `200` · `404` · `401`/`403` |
| DELETE | `/api/produits/<id>` | Admin | — | `204` · `404` · `401`/`403` |

## 4.8 — Modules niveau 🥈 (un par fonction métier)

```
app/
├── app.py               # + enregistre les nouveaux blueprints
├── db.py                # inchangé
├── security.py          # NOUVEAU (4.11) : JWT, hachage, décorateurs
├── modelsSQLAlchemy.py  # + Category, Product, Order, OrderItem (4.4, 4.6)
└── routes/
    ├── auth.py          # + POST /api/auth/login
    └── produits.py      # NOUVEAU (F2) : CRUD /api/produits
    # (routes/commandes.py sera ajouté au niveau 🥇 avec F3)
```

---

✅ **Checklist étape 4 (niveau 🥈)** : 4.3 contraintes ✅ · 4.4 FK/relations ✅ · 4.11 sécurité ✅ · contrat d'API 🥈 ✅ · arborescence 🥈 ✅ (4.6 → niveau 🥇 avec F3).

⚠️ **Piège évité** : pas de classe pour le token JWT (donnée temporaire, 4.2 — un `dict` suffit).

🧰 **Bonnes pratiques** : `.env` pour SECRET_KEY (jamais commité, `.gitignore` ✅) · `PyJWT` ajouté à `requirements.txt` · README + canva mis à jour (nouveau canva `canva-structure-intermediaire.mmd`, sans écraser celui de 🥉) · commit.

🧵 **Fil rouge 🥈** : « se connecter » → `POST /api/auth/login` → token JWT ; « gérer le catalogue » → CRUD `/api/produits` réservé admin.

❓ **Auto-évaluation** : 1) Pourquoi ForeignKey seulement maintenant ? 2) Où va la SECRET_KEY ? 3) Quelles routes sont réservées à l'admin ?

📝 **À retenir (3 lignes)** : 1) 🥈 = 🥉 + 4.3/4.4/4.6/4.11. 2) Relations → ForeignKey + relationship. 3) Sécurité → module dédié + JWT + .env + décorateurs de rôle.

---
*Conception 🥈 prête (ordre 4.3 → 4.4 → 4.6 → 4.11, comme la méthode). Prochaine étape (avec validation) : étape 5 niveau 🥈 (tests : unitaires + intégration + 401/403).*
