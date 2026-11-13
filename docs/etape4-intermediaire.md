# ÉTAPE 4 appliquée à DigiMarket — NIVEAU 🥈 INTERMÉDIAIRE

⏱️ sur le niveau 🥈 (en plus du niveau 🥉 déjà fait)

**Rappel du principe** : on croise les résultats des étapes 1, 2 et 3. Règle à dire à voix haute : *« analyse → condition → si positif, ACTION de création »*, et *« si la condition est fausse, que se passe-t-il ? »*.

**Niveau 🥈 = niveau 🥉 + parties 4.3 (contraintes), 4.4 (relations), 4.6 (transitions simples), 4.11 (sécurité de base)**.
Le fil rouge 🥈 : **« un administrateur gère le catalogue (produits) »** + **« un utilisateur se connecte (JWT) »**.

> 📌 **Répartition des fonctions métier** (règle de complexité dans `methodologie.md`) :
> 🥈 = **F2 (catalogue) + F4 (sécurité JWT)** — objets avec relation 1—N, CRUD protégé par rôle.
> **F3 « Gérer les commandes » est réservée au niveau 🥇 confirmé** (changement d'état, cycle de vie, logique stock) — on ne la traite PAS ici.

---

## 4.3 — Contraintes métier sur les objets (par route) (condition : règle de validité sur un attribut ✅ → ACTION)

| Objet | Attribut | Règle | Où | Erreur | Route concernée | Fonction métier |
|---|---|---|---|---|---|---|
| `User` | `email` | unique | contrainte base `unique=True` (déjà fait 🥉) | 409 | `POST /api/auth/register` | **F1** Gérer les comptes |
| `Category` | `name` | unique | `unique=True` | 409 | `POST /api/categories` (🥈) | **F2** Gérer le catalogue |
| `Product` | `price` | >= 0 | validation dans la route | 400 | `POST`/`PUT /api/produits` | **F2** (+ F4 contrôle admin) |
| `Product` | `stock` | >= 0 | validation dans la route | 400 | `POST`/`PUT /api/produits` | **F2** (+ F4) |

## 4.4 — Création des objets ayant une relation 1—N (condition : deux objets liés ✅ → ACTION)

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

## 4.6 — Création des objets ayant une transition d'état (méthodes + contrôle) → niveau 🥇 confirmé

> ⚠️ La partie 4.6 (transitions d'état, ex. `Order.valider()`) concerne **F3 « Gérer les commandes »** : selon la règle de répartition par complexité (changement d'état = logique complexe), elle est traitée au **niveau 🥇 confirmé**, pas ici.

## 4.7 — Routes de l'API : contrat complet niveau 🥈 (méthode, entrées, sorties, codes, accès, fonction métier, objet)

> 💡 Rappel : une route = **URL + méthode HTTP** (le « panneau du guichet ») reliée à un
> **endpoint** (la fonction Python exécutée). Le contrat ci-dessous dit, pour chaque
> route : qui a le droit d'y accéder, quoi envoyer (entrées JSON), quoi on reçoit
> (sorties JSON + codes HTTP). Les routes protégées exigent le header
> `Authorization: Bearer <token JWT>` (obtenu via `/api/auth/login`).


| Méthode | Route | Accès | Entrée (JSON) | Sorties / codes | Fonction métier | Objet manipulé |
|---|---|---|---|---|---|---|
| POST | `/api/auth/register` | Public | `{email, password, ...}` | `201` · `400` · `409` | **F1** Gérer les comptes | `User` (créé) |
| POST | `/api/auth/login` | Public | `{email, password}` | `200` + token JWT · `401` | **F1 + F4** (auth) | `User` (lu) → token (temporaire, 4.2) |
| GET | `/api/produits` | Public | query `?q=` | `200` liste JSON | **F2** Gérer le catalogue | `Product` (lus) |
| GET | `/api/produits/<id>` | Public | — | `200` · `404` | **F2** | `Product` (lu) |
| POST | `/api/produits` | **Admin** (token + rôle) | `{name, description, price, stock, category_id}` | `201` · `400` · `401`/`403` | **F2** (+ F4 contrôle) | `Product` (créé) + `Category` (FK) |
| PUT | `/api/produits/<id>` | Admin | idem | `200` · `404` · `401`/`403` | **F2** (+ F4) | `Product` (modifié) |
| DELETE | `/api/produits/<id>` | Admin | — | `204` · `404` · `401`/`403` | **F2** (+ F4) | `Product` (supprimé) |

> 💡 Chaque route = un cas d'utilisation (étape 1) réalisé par une **fonction métier** (étape 2, F1–F4)
> qui agit sur un **objet** (étape 3) : la route ne fait que traduire la requête HTTP en appel à la fonction métier.

- `200` = OK · `201` = ressource créée · `204` = supprimé (corps vide) ;
- `400` = entrées invalides (ex. prix < 0, champs manquants) · `401` = pas de token ou token invalide ;
- `403` = token valide mais rôle insuffisant (client au lieu d'admin) · `404` = ressource introuvable ;
- `GET /api/produits` est **public** (Visiteur) : catalogue consultable sans compte, avec recherche `?q=texte`.

## 4.8 — Organisation du code niveau 🥈 : app.py + db.py + security.py + routes/*.py (un blueprint par fonction métier)

```
app/
├── app.py               # + enregistre les nouveaux blueprints
├── db.py                # inchangé
├── security.py          # NOUVEAU (4.11) : JWT, hachage, décorateurs
├── modelsSQLAlchemy.py  # + Category, Product (Order, OrderItem au 🥇 avec F3)
└── routes/
    ├── auth.py          # + POST /api/auth/login
    └── produits.py      # NOUVEAU (F2) : CRUD /api/produits
    # (routes/commandes.py sera ajouté au niveau 🥇 avec F3)
```

## 4.11 — Sécurité de base (condition : authentification/autorisation requise ✅ → ACTION)

Nouveau module `app/security.py` + bibliothèque **PyJWT** + fichier **`.env`** (jamais commité) :

```python
# ------------------------------------------------------------------
# app/security.py — TOUTE la sécurité regroupée ici (4.11)
# ------------------------------------------------------------------
# os  : lire les variables d'environnement (le fichier .env, JAMAIS commité)
# jwt : bibliothèque PyJWT — créer et vérifier les tokens JWT
import os
import jwt
# functools.wraps : conserve le nom de la fonction décorée (indispensable à Flask)
from functools import wraps
# request : lire le header "Authorization: Bearer <token>" de la requête entrante
# jsonify : renvoyer les erreurs (401/403) en JSON
from flask import request, jsonify
# werkzeug.security (inclus avec Flask) :
# - generate_password_hash : hache un mot de passe (à l'inscription)
# - check_password_hash    : vérifie un mot de passe contre son hash (au login)
from werkzeug.security import generate_password_hash, check_password_hash

# La clé secrète SERT À SIGNER les tokens JWT : elle ne doit JAMAIS être dans le
# code ni committée → on la lit dans .env (déjà dans .gitignore)
SECRET_KEY = os.environ["SECRET_KEY"]

def creer_token(user):
    # Crée le token signé : payload = {"user_id":..., "role":...}
    # jwt.encode(payload, SECRET_KEY, algorithm="HS256") → chaîne "xxxxx.yyyyy.zzzzz"
    # Le client devra renvoyer ce token dans le header Authorization à chaque appel
    ...

def verifier_token():
    # Lit le header "Authorization: Bearer <token>", décode et VÉRIFIE la signature
    # → renvoie le payload (dict) si OK ; sinon erreur 401 (token invalide ou expiré)
    ...

def login_required(f):
    # DÉCORATEUR : la route exige un token valide (utilisé avec @login_required)
    # @wraps(f) garde le nom de la route ; sans token valide → 401 en JSON
    ...

def admin_required(f):
    # DÉCORATEUR : en plus d'un token valide, exige le rôle "admin"
    # token d'un simple client → 403 (authentifié mais PAS autorisé)
    ...
```

Routes auth 🥈 : `POST /api/auth/register` (déjà fait) + **`POST /api/auth/login`** → renvoie `{ "token": "..." }` (vérifie le hash avec `check_password_hash`).

---

✅ **Checklist étape 4 (niveau 🥈)** : 4.3 contraintes ✅ · 4.4 FK/relations ✅ · 4.11 sécurité ✅ · contrat d'API 🥈 ✅ · arborescence 🥈 ✅ (4.6 → niveau 🥇 avec F3).

⚠️ **Piège évité** : pas de classe pour le token JWT (donnée temporaire, 4.2 — un `dict` suffit).

🧰 **Bonnes pratiques** : `.env` pour SECRET_KEY (jamais commité, `.gitignore` ✅) · `PyJWT` ajouté à `requirements.txt` · README + canva mis à jour (nouveau canva `canva-structure-intermediaire.mmd`, sans écraser celui de 🥉) · commit.

🧵 **Fil rouge 🥈** : « se connecter » → `POST /api/auth/login` → token JWT ; « gérer le catalogue » → CRUD `/api/produits` réservé admin.

❓ **Auto-évaluation** : 1) Pourquoi ForeignKey seulement maintenant ? 2) Où va la SECRET_KEY ? 3) Quelles routes sont réservées à l'admin ?

📝 **À retenir (3 lignes)** : 1) 🥈 = 🥉 + 4.3/4.4/4.6/4.11. 2) Relations → ForeignKey + relationship. 3) Sécurité → module dédié + JWT + .env + décorateurs de rôle.

---
*Conception 🥈 prête (ordre 4.3 → 4.4 → 4.6 → 4.11, comme la méthode). Prochaine étape (avec validation) : étape 5 niveau 🥈 (tests : unitaires + intégration + 401/403).*
