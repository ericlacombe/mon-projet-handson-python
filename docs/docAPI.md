# 📘 docAPI — Documentation complète de l'API DigiMarket (Flask)

Ce document rassemble **toute la documentation de l'API**, en deux chapitres :

1. **Chapitre 1 — Contrat API pour les clients** : tout ce dont un client a besoin pour **générer et traiter des requêtes** (URL de base, authentification, contrat de chaque route avec entrées/sorties JSON, codes d'erreur, exemple curl).
2. **Chapitre 2 — Contexte interne (non nécessaire aux requêtes)** : architecture, modèle de données physique, fonctions métier, sécurité interne, niveaux pédagogiques, traçabilité — utile au **mainteneur**, pas à l'appelant de l'API.

> Le `README.md` reste la page d'entrée (installation, lancement, tests) ; ce fichier est la **référence API détaillée** exigée par le CDC (« Documentation complète de l'API », `docs/attentes.md`).

---

# Chapitre 1 — Contrat API pour les clients (générer des requêtes)

## 1.1 URL de base

- Lancer le serveur depuis la racine du projet : `python -m app.app`
- **URL de base de toutes les routes** : `http://127.0.0.1:5000` (ex. `http://127.0.0.1:5000/api/produits`)
- Port configurable : `PORT=5001 python -m app.app` → URL de base `http://127.0.0.1:5001`

## 1.2 Authentification — JWT Bearer

1. **Obtenir un token** : `POST /api/auth/login` avec `{"email": "...", "password": "..."}` → `200 {"message": "connexion réussie", "token": "eyJ..."}`
2. **Envoyer le token** sur toutes les routes protégées, dans le header :
   ```
   Authorization: Bearer <token>
   ```
   et `Content-Type: application/json` dès qu'il y a un corps de requête.
3. Le token est un **JWT signé (HS256)**, payload `{user_id, role, exp}`, valable **24 h**. Token absent, invalide ou expiré → **401** `{"error": "token requis ou invalide"}`.
4. Deux **rôles** : `client` (attribué par défaut à l'inscription) et `admin`. Token valide mais rôle insuffisant → **403**.

**Comptes de démo** (créés automatiquement au 1ᵉʳ lancement, utiles pour tester) :

| Rôle | Email | Mot de passe |
|---|---|---|
| Admin | admin@digimarket.fr | admin123 |
| Client | client@digimarket.fr | client123 |

## 1.3 Conventions communes

- Tous les échanges sont en **JSON**. Les requêtes avec body exigent `Content-Type: application/json`.
- Succès : corps JSON + code `200` (lecture/modification), `201` (création), `204` (suppression, **corps vide**).
- **Toute erreur est renvoyée en JSON** : `{"error": "<message>"}` avec un code 4xx/5xx.
- Erreurs **globales** (valables pour toutes les routes) : `404 {"error": "ressource introuvable"}` (route inconnue) · `405 {"error": "méthode non autorisée"}` · `500 {"error": "erreur interne du serveur"}`.

## 1.4 Contrat complet des routes

Légende des accès : **Public** = sans token · **Client** = token `client` suffisant · **Admin** = token avec rôle `admin` · **Propriétaire** = client auteur de la ressource (ou admin).

| Méthode | Route | Accès | Entrée (JSON) | Sorties / codes |
|---|---|---|---|---|
| POST | `/api/auth/register` | Public | `{"email", "password", "first_name"?, "last_name"?, "address"?}` (email et password requis) | `201 {"message", "email"}` · `400` champs manquants · `409` email déjà utilisé |
| POST | `/api/auth/login` | Public | `{"email", "password"}` | `200 {"message", "token"}` (JWT 24 h) · `400` · `401` identifiants invalides |
| GET | `/api/produits` | Public | query optionnelle `?q=texte` (recherche sur le nom, insensible à la casse) | `200` liste de produits (voir 1.5) |
| GET | `/api/produits/<id>` | Public | — | `200` détail produit · `404` produit introuvable |
| POST | `/api/produits` | Admin | `{"name", "price", "category_id", "description"?, "stock"?}` (name, price, category_id requis ; price/stock ≥ 0 ; catégorie existante) | `201 {"message": "produit créé", "id"}` · `400` · `401`/`403` |
| PUT | `/api/produits/<id>` | Admin | champs partiels : `name`, `description`, `price`, `stock`, `category_id` (price/stock ≥ 0 si fournis) | `200 {"message": "produit modifié", "id"}` · `400` · `401`/`403` · `404` |
| DELETE | `/api/produits/<id>` | Admin | — | `204` (corps vide) · `401`/`403` · `404` |
| POST | `/api/categories` | Admin | `{"name"}` (unique) | `201 {"message": "catégorie créée", "id"}` · `400` · `409` nom déjà pris · `401`/`403` |
| POST | `/api/commandes` | Client | `{"address_livraison", "items": [{"product_id", "quantite"}, ...]}` (adresse non vide, items non vide, quantité > 0, stock suffisant) | `201` commande complète (voir 1.5) · `400` (adresse/items requis, produit inexistant, stock insuffisant, quantité ≤ 0) · `401` |
| GET | `/api/commandes` | Client = **ses** commandes ; Admin = **toutes** | — | `200` liste de commandes · `401` |
| GET | `/api/commandes/<id>` | Propriétaire ou admin | — | `200` commande complète · `401` · `403` accès interdit à cette commande · `404` commande introuvable |
| GET | `/api/commandes/<id>/lignes` | Propriétaire ou admin | — | `200` commande complète incluant ses `lignes` (même JSON que le détail) · `401` · `403` · `404` |
| PATCH | `/api/commandes/<id>/statut` | Admin = toute transition ; client propriétaire = uniquement `"annulée"` | `{"statut": "validée" \| "expédiée" \| "livrée" \| "annulée"}` | `200` commande mise à jour · `400` transition interdite · `401` · `403` un client ne peut qu'annuler sa commande · `404` |

### 1.4.1 Cycle de vie d'une commande (statut)

Valeurs : `en_attente` (défaut à la création) → `validée` → `expédiée` → `livrée`, et `annulée` depuis `en_attente` ou `validée`.

- Transitions autorisées : `en_attente` → {`validée`, `annulée`} · `validée` → {`expédiée`, `annulée`} · `expédiée` → {`livrée`} · `livrée`/`annulée` → aucune.
- Toute autre transition → `400 {"error": "transition interdite : <de> → <vers>"}`.
- Effets de bord sur le stock : **validation** → stock décrémenté ; **annulation** → stock restitué.

## 1.5 Formes JSON des objets

**Produit** (liste `GET /api/produits`) :
```json
[{"id": 1, "name": "PC portable", "description": "14 pouces, 16 Go RAM", "price": 899.99, "stock": 10, "category_id": 1}]
```
**Détail produit** (`GET /api/produits/<id>`) : mêmes champs + `"categorie"` (nom de la catégorie, ex. `"Informatique"`).

**Commande** (`POST/GET/PATCH /api/commandes...`) :
```json
{"id": 3, "user_id": 2, "address_livraison": "12 rue des Lilas, Paris",
 "date_creation": "2026-11-24T11:36:56.485580", "statut": "en_attente", "total": 159.8,
 "lignes": [{"product_id": 2, "quantite": 2, "prix_unitaire": 79.9}]}
```
(`prix_unitaire` = prix du produit figé au moment de la commande ; `total` = somme des lignes.)

## 1.6 Exemple de session client (curl)

```bash
# 1. Se connecter (client de démo) et stocker le token
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@digimarket.fr","password":"client123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 2. Consulter le catalogue (public, avec recherche)
curl "http://127.0.0.1:5000/api/produits?q=clavier"

# 3. Passer une commande (route protégée → header Bearer)
curl -X POST http://127.0.0.1:5000/api/commandes \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"address_livraison":"12 rue des Lilas, Paris","items":[{"product_id":2,"quantite":2}]}'

# 4. Voir son historique
curl http://127.0.0.1:5000/api/commandes -H "Authorization: Bearer $TOKEN"
```
Scénario complet (admin, 401/403/404, transitions) : `docs/demo.md`.

## 1.7 Récapitulatif des codes d'erreur

| Code | Signification | Exemples de `{"error": ...}` |
|---|---|---|
| `400` | requête invalide (champs manquants, prix/stock < 0, stock insuffisant, quantité ≤ 0, transition interdite) | `"transition interdite : expédiée → en_attente"`, `"stock insuffisant pour PC portable"` |
| `401` | token absent/invalide/expiré | `"token requis ou invalide"`, `"identifiants invalides"` |
| `403` | rôle insuffisant ou ressource d'un autre | `"réservé aux administrateurs"`, `"un client ne peut qu'annuler sa commande"`, `"accès interdit à cette commande"` |
| `404` | ressource/route inconnue | `"produit introuvable"`, `"commande introuvable"`, `"ressource introuvable"` (global) |
| `405` | mauvaise méthode HTTP sur une route existante | `"méthode non autorisée"` (global) |
| `409` | conflit d'unicité | `"email déjà utilisé"`, `"catégorie déjà existante"` |
| `500` | erreur interne | `"erreur interne du serveur"` (global) |

---

# Chapitre 2 — Contexte interne (non nécessaire pour lancer des requêtes)

Ce chapitre décrit **comment l'API est construite en interne** : il s'adresse au mainteneur du projet, pas au client de l'API.

## 2.1 Architecture interne (fichiers et blueprints)

```
app/
├── app.py                  # point d'entrée : app = Flask(__name__), register_blueprint ×3, errorhandlers 404/405/500, init_sample_data(), app.run
├── db.py                   # moteur SQLite (sqlite:///digimarket.db) + session partagée (évite l'import circulaire)
├── security.py             # JWT (HS256, 24 h), hachage mots de passe, décorateurs login_required / admin_required
├── modelsSQLAlchemy.py     # modèles ORM : User, Category, Product, Order, OrderItem
├── utils.py                # fonctions pures : calculer_total, verifier_stock
└── routes/                 # un blueprint par fonction métier (CDC)
    ├── auth.py             # /api/auth   : register, login
    ├── produits.py         # /api        : produits (GET/POST/PUT/DELETE) + categories (POST)
    └── commandes.py        # /api        : commandes (POST/GET/PATCH)
```

## 2.2 Modèle de données physique (tables SQL)

Tables créées par `Base.metadata.create_all` dans `digimarket.db` (fichier SQLite à la racine) :

| Table | Champs | Clés |
|---|---|---|
| `users` | id, email, password_hash, first_name, last_name, address, role | PK id · UK email |
| `categories` | id, name | PK id · UK name |
| `products` | id, name, description, price, stock, category_id | PK id · FK category_id → categories.id |
| `orders` | id, user_id, address_livraison, statut, date_creation, total | PK id · FK user_id → users.id |
| `order_items` | id, order_id, product_id, quantite, prix_unitaire | PK id · FK order_id → orders.id · FK product_id → products.id |

Relations : Utilisateur 1—N Commande · Catégorie 1—N Produit · Produit 1—N LigneCommande · Commande 1—N LigneCommande. Détail : `docs/etape3-objets.md` (schéma ER).

## 2.3 Fonctions métier ↔ routes

| Fonction métier | Objet(s) | Routes implémentées |
|---|---|---|
| **F1 — Gérer les comptes** | `User` | `POST /api/auth/register`, `POST /api/auth/login` |
| **F2 — Gérer le catalogue** | `Product`, `Category` | `GET/POST /api/produits`, `GET/PUT/DELETE /api/produits/<id>`, `POST /api/categories` |
| **F3 — Gérer les commandes** | `Order`, `OrderItem` | `POST/GET /api/commandes`, `GET /api/commandes/<id>(/lignes)`, `PATCH /api/commandes/<id>/statut` |
| **F4 — Sécuriser les accès** | `User` (rôle), token | décorateurs sur toutes les routes non publiques + JWT (voir 2.4) |

## 2.4 Chaîne de protection interne (consigne 4.11)

```
→ 0. BASE      : rôle stocké en base ("client" par défaut à l'inscription, "admin" uniquement pour le compte de démo), mot de passe haché (PBKDF2 + sel), jamais en clair
→ 1. REGISTER  : rôle forcé "client" côté serveur (un {"role":"admin"} envoyé est ignoré)
→ 2. DÉMO      : seul compte admin = compte de démo, mot de passe haché
→ 3. LOGIN     : token JWT SIGNÉ (HMAC-SHA256, pas chiffré, rôle embarqué, exp 24 h)
→ 4. ROUTES    : 401 si signature invalide/expirée, 403 si rôle insuffisant (admin_required / client_propriétaire)
→ 5. .env+HTTPS: SECRET_KEY hors git (.gitignore), réseau chiffré en production
```

## 2.5 Niveaux pédagogiques et traçabilité

Le projet est réalisé en 3 niveaux (🥉 débutant = F1 register · 🥈 intermédiaire = F2 + F4 · 🥇 confirmé = F3) : voir `docs/methodologie.md` (étapes 0–6) et les `docs/etape*-<niveau>.md`. La traçabilité exigence CDC → réalisation → test est dans le `README.md` (« Traçabilité CDC »).

## 2.6 Initialisation des données de démo (interne)

Au lancement direct (`python -m app.app`), le bloc `if __name__ == "__main__":` appelle `init_sample_data()` (`app/app.py`) : si la table `users` est vide, elle crée les 2 comptes de démo (mots de passe hachés), 1 catégorie « Informatique », 2 produits (PC portable 899,99 € stock 10 · Clavier mécanique 79,90 € stock 25) et 1 commande exemple `en_attente`. La base vit dans `digimarket.db` (créée automatiquement, dans `.gitignore`). Les tests (`tests/`) utilisent leur propre base en mémoire et ne voient jamais ces données.
