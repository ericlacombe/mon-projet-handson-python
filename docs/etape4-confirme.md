# ÉTAPE 4 appliquée à DigiMarket — NIVEAU 🥇 CONFIRMÉ (conception AVANT code)

**Niveau 🥇 = niveau 🥈 + partie 4.6 (transitions d'état) + F3 « Gérer les commandes »** (CDC étape 3).
Le code 🥉/🥈 reste fonctionnel : on AJOUTE, on ne remplace pas.

## 📋 Tableau récap — ce qu'on crée au niveau 🥇

| Fonction métier | Objet(s) | Routes (contrat 4.7) | Fichiers |
|---|---|---|---|
| **F3** Gérer les commandes | `Order`, `OrderItem` (nouveaux ; Order 1—N OrderItem, OrderItem N—1 Product, Order N—1 User) | `POST /api/commandes`, `GET /api/commandes`, `GET /api/commandes/<id>`, `GET /api/commandes/<id>/lignes`, `PATCH /api/commandes/<id>/statut` (admin) | `app/routes/commandes.py` (nouveau), `modelsSQLAlchemy.py` (+ Order, OrderItem) |

> F1/F2/F4 déjà faits au 🥈 ✅. Au 🥇 on touche à tout le CDC (étapes 1+2+3).

## 4.1 — Base de données (niveau 🥇 : la base s'étend encore, elle n'est pas recréée)

Condition : `Order` et `OrderItem` sont persistés ✅ → ACTION. La base `digimarket.db` existe déjà (🥉) et contient `users, categories, products` (🥈) : on **ajoute** 2 tables dans `modelsSQLAlchemy.py` ; `Base.metadata.create_all(engine)` (dans `db.py`) les crée au lancement **sans toucher aux tables existantes** :

```sql
-- Nouvelles tables au niveau 🥇 (à côté de users/categories/products) :
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),          -- FK : l'acheteur (N—1, §4.5)
    address_livraison TEXT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',       -- cycle de vie 4.6
    total FLOAT NOT NULL DEFAULT 0                          -- calculé par calculer_total (4.9)
);
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),        -- FK : la commande (1—N, §4.5)
    product_id INTEGER NOT NULL REFERENCES products(id),    -- FK : le produit (N—1, §4.5)
    quantite INTEGER NOT NULL,                              -- 4.3 : > 0 (400 sinon)
    prix_unitaire FLOAT NOT NULL                            -- prix figé à la commande
);
```

🥇 = **vérifier au démarrage** que les 5 tables sont bien là :

```python
assert set(Base.metadata.tables) == {"users", "categories", "products", "orders", "order_items"}
```

## 4.2 — Données temporaires (niveau 🥇)

Le **panier côté client** est une donnée temporaire : elle n'existe que le temps de la session de navigation, on ne la stocke PAS en base (comme le token JWT au 🥈). → un simple `dict`/objet léger côté client suffit, **pas de table**.

## 4.3 — Contraintes métier sur les objets (par route) — ajouts 🥇

| Fonction métier | Objet(s) | Règle | Où | Erreur |
|---|---|---|---|---|
| **F3** | `OrderItem` | `quantite > 0` | route POST | 400 |
| **F3** | `Product` | stock suffisant à la commande | route POST (vérif avant création) | 400 |
| **F3** | `Product` | stock décrémenté à la validation ; restitué à l'annulation | méthodes Order + route PATCH | — |
| **F3** | `Order.statut` | transition autorisée (4.6) | `Order.changer_statut` | 400 |

## 4.5 — Création des objets ayant une relation 1—N — ajouts 🥇

| Fonction métier | Objet(s) | Relation | Clé étrangère | relationship |
|---|---|---|---|---|
| **F3** | `Order` ↔ `OrderItem` | 1—N | `order_items.order_id → orders.id` | `Order.items`, `OrderItem.order` |
| **F3** | `OrderItem` ↔ `Product` | N—1 | `order_items.product_id → products.id` | `OrderItem.product` |
| **F3** | `Order` ↔ `User` | N—1 | `orders.user_id → users.id` | `User.orders`, `Order.user` |

## 4.6 — Création des objets ayant une transition d'état (Order) — ajouts 🥇

`Order.statut` : `en_attente` → `validée` → `expédiée` ; `annulée` possible depuis `en_attente`/`validée`.

> 💡 **Analogie** : le cycle de vie d'une commande, c'est comme le suivi d'un colis — *en préparation → expédié → livré* (on ne revient jamais en arrière).

| Fonction métier | Objet | Transition | Méthode sur la classe | Contrôle |
|---|---|---|---|---|
| **F3** | `Order` | en_attente → validée | `Order.valider()` | admin uniquement (route PATCH) + stock suffisant → décrément |
| **F3** | `Order` | validée → expédiée | `Order.expedier()` | admin uniquement |
| **F3** | `Order` | en_attente/validée → annulée | `Order.annuler()` | admin ou client_propriétaire + RESTITUTION du stock |

```python
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    # ------------------------------------------------------------------
    # Côté "N" de la relation : la clé étrangère (repris du 4.5)
    # - ForeignKey("users.id") : ce champ RÉFÉRENCE la clé primaire de users
    # - nullable=False : une commande DOIT appartenir à un utilisateur (obligatoire)
    # ------------------------------------------------------------------
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_livraison = Column(Text, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)

    # ------------------------------------------------------------------
    # RELATION 1—N : Order 1—N OrderItem (une commande a plusieurs lignes)
    # ------------------------------------------------------------------
    # relationship("OrderItem") dans Order définit la relation ORM.
    # - backref="order" : crée automatiquement orderitem.order (accès inverse :
    #   depuis une ligne, on atteint sa commande — ex. ma_ligne.order.id)
    # - lazy=True (défaut) : les lignes sont chargées UNIQUEMENT quand on y accède
    #   (chargement différé, pas tout en mémoire d'un coup)
    # - cascade="all, delete-orphan" : supprimer une commande supprime aussi ses
    #   lignes (sinon elles resteraient "orphelines", sans commande)
    items = relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    # 4.6 — Cycle de vie d'une commande (états + transitions autorisées).
    # STATUTS : tous les états possibles (constantes nommées, pas de "magic strings").
    STATUTS = ("en_attente", "validée", "expédiée", "annulée")
    # TRANSITIONS : pour chaque état, la liste des états suivants AUTORISÉS.
    #   en_attente → validée (l'admin valide, le stock est décrémenté)
    #              → annulée (restitution du stock)
    #   validée    → expédiée | annulée
    #   expédiée/annulée → AUCUNE (états finaux : on ne revient jamais en arrière)
    TRANSITIONS = {"en_attente": ["validée", "annulée"], "validée": ["expédiée", "annulée"],
                   "expédiée": [], "annulée": []}

    def changer_statut(self, nouveau):
        # 4.6 : UNE méthode par objet avec cycle de vie, qui CONTRÔLE la transition :
        # si le passage statut → nouveau n'est pas dans TRANSITIONS, on refuse
        # (ValueError → la route renvoie 400 "transition interdite").
        if nouveau not in self.TRANSITIONS[self.statut]:
            raise ValueError(f"transition {self.statut} → {nouveau} interdite")
        self.statut = nouveau
        # C'est AUSSI ici qu'on branche les effets de bord (4.3) :
        #   validée → décrémenter le stock des produits (verifier_stock + update)
        #   annulée → restituer le stock
```

## 4.7 — Routes de l'API : contrat complet niveau 🥇 (ajouts : routes commandes, CDC étape 3)

| Fonction métier | Objet(s) manipulé(s) | Action sur l'Objet | Méthode | Route | Accès | Entrée (JSON) | Sorties / codes |
|---|---|---|---|---|---|---|---|
| **F3** | `Order` + `OrderItem` | **créée** (commande + lignes + total) | POST | `/api/commandes` | Client connecté (`@login_required`) | `{adresse_livraison, items: [{product_id, quantite}]}` | `201` · `400` (stock insuffisant, qté ≤ 0) · `401` |
| **F3** | `Order` | **lue** (liste : soi-même, ou toutes si admin) | GET | `/api/commandes` | Client = ses commandes ; admin = toutes | — | `200` · `401` |
| **F3** | `Order` | **lue** (détail) | GET | `/api/commandes/<id>` | client_propriétaire ou admin | — | `200` · `403` · `404` |
| **F3** | `OrderItem` | **lues** (lignes de la commande) | GET | `/api/commandes/<id>/lignes` | client_propriétaire ou admin | — | `200` · `403` · `404` |
| **F3+F4** | `Order.statut` | **modifié** (transition contrôlée 4.6 + stock) | PATCH | `/api/commandes/<id>/statut` | **Admin** (toutes transitions) **ou client_propriétaire** (uniquement `annulée`, si en_attente/validée) | `{statut: "validée"}` | `200` · `400` (transition interdite) · `401`/`403` · `404` |

> ⚠️ Pas de `DELETE /api/commandes/<id>` : une commande ne se supprime pas (historique CDC), elle s'annule via ce PATCH.

## 4.8 — Organisation du code (arborescence complète au niveau 🥇)

Un blueprint par fonction métier ; app.py reste l'assemblage. **Ajouts 🥇** marqués 🥇 :

```
mon-projet-handson-python/
├── README.md                   # page d'entrée (install, lancement, API, sécurité)
├── requirements.txt            # flask, sqlalchemy, pytest, PyJWT
├── .env                        # SECRET_KEY (jamais commité, .gitignore)
├── .gitignore                  # venv/, .env, __pycache__/, *.db, .pytest_cache/
├── app/                        # 💻 code de l'API (package Python)
│   ├── __init__.py
│   ├── app.py                  # point d'entrée Flask (app, blueprints, init_sample_data, errorhandlers 🥇)
│   ├── db.py                   # engine SQLite + session partagée + create_all
│   ├── modelsSQLAlchemy.py     # 🥉 User · 🥈 Category, Product · 🥇 Order, OrderItem (FK 1—N, N—1)
│   ├── security.py             # 🥈 F4 : JWT, hachage, @login_required/@admin_required
│   ├── utils.py                # 🥇 fonctions pures 4.9 : calculer_total, verifier_stock
│   └── routes/
│       ├── auth.py             # 🥉 register · 🥈 login
│       ├── produits.py         # 🥈 F2 : CRUD /api/produits + /api/categories
│       └── commandes.py        # 🥇 F3 : /api/commandes (POST/GET/PATCH)
├── tests/
│   ├── conftest.py             # 🥈 fixtures (base en mémoire, tokens admin/client)
│   ├── test_auth.py            # 🥉 409
│   ├── test_security.py        # 🥈 F1 login + F4 tokens
│   ├── test_produits.py        # 🥈 F2 CRUD
│   └── test_commandes.py       # 🥇 F3 : transitions, stock, propriétaire-or-admin + régression
└── docs/                       # 📚 documentation (méthode + étapes 0-6 par niveau + canva)
    ├── attentes.md             # cahier des charges
    ├── methodologie.md / methodologie-canva.mmd
    ├── etape0…etape6-*.md       # résultats des étapes (🥉 fait, 🥈 fait, 🥇 ce fichier…)
    └── canva-structure-debutant.mmd / -intermediaire.mmd / -confirme.mmd 🥇 (jamais écrasés)
```
(digimarket.db est créé automatiquement au lancement, à la racine — jamais commité)

## 4.9 — Fonctions Python (transformations sans état) — ajouts 🥇

> 💡 Une fonction Python ici est **pure** : mêmes entrées → même sortie, sans effet de bord persistant (pas d'écriture en base). Ex. `calculer_total(lignes)`.

| Fonction | Rôle | Fichier |
|---|---|---|
| `calculer_total(commande)` | somme `quantite * prix_unitaire` des lignes | `app/routes/commandes.py` (ou `app/utils.py`) |
| `verifier_stock(items)` | vérifie la dispo de chaque produit | idem |

## 4.10 — Gestion des erreurs — ajouts 🥇 (gestionnaire global + nouveaux codes F3)

Progression de 4.10 par niveau (voir methodologie.md) :
- 🥉 : 4.10 **basique** = 1 gestionnaire (409 email déjà pris sur register) — voir `docs/etape4-conception-debutant.md` §4.7 (colonne « Sorties / codes » : 201/400/409) ;
- 🥈 : codes par route (try/except → 500) + 400/401/403/404/409 sur auth/produits — voir `docs/etape4-intermediaire.md` §4.7 (colonne « Sorties / codes » : 200/201/204/400/401/403/404/409) ;
- 🥇 : on complète avec un **gestionnaire global** `@app.errorhandler` (réponse JSON uniforme pour toute l'app, y compris 404/405/500 hors routes) + les nouveaux codes F3 ci-dessous :

**① Le bloc de code = gestionnaire GLOBAL** (dans `app/app.py`) : il intercepte les erreurs génériques de Flask **partout** (même hors des routes) et renvoie toujours du JSON uniforme :

```python
# Pourquoi SEULEMENT 404/405/500 ici ?
# - 2xx (200/201/204) = SUCCÈS : la route renvoie sa réponse normalement, pas d'erreur à intercepter.
# - 400/401/403/409 = ERREURS MÉTIER rendues volontairement par les routes
#   (return jsonify({...}), 400) : ce ne sont PAS des exceptions Flask, ce gestionnaire ne les voit pas.
# - 404/405/500 = ERREURS SYSTÈME levées par Flask lui-même (route inconnue, mauvaise méthode,
#   exception non rattrapée) → c'est ELLES qu'on intercepte ici pour toujours répondre en JSON.
@app.errorhandler(404)   # route inconnue
@app.errorhandler(405)   # mauvaise méthode HTTP sur une route existante
@app.errorhandler(500)   # exception non rattrapée
```

**② Le tableau = erreurs MÉTIER F3**, rendues **explicitement par chaque route** (`return jsonify({"error": ...}), 400`) — ce ne sont pas des exceptions Flask, le gestionnaire global ne les voit pas.

> 🎯 **Ce qu'apporte ce tableau** : il traduit chaque **contrainte métier du §4.3** (les "inputs" à valider) en **code HTTP précis** + le message d'erreur — c'est le contrat d'erreur de l'API.

| Fonction métier | Objet(s) manipulé(s) | Input / contrainte (voir §4.3) | Erreur 🥇 (métier) | Code | Où (rendu par la route) |
|---|---|---|---|---|---|
| **F3** | `OrderItem` | `quantite > 0` (entrée JSON `items[]`) | quantité ≤ 0 | 400 | route POST /api/commandes |
| **F3** | `Product` | stock suffisant (entrée `product_id`) | stock insuffisant | 400 | route POST /api/commandes |
| **F3** | `Order` | transition autorisée (§4.6) | transition interdite | 400 | route PATCH `/api/commandes/<id>/statut` (via `Order.changer_statut`, §4.6) |
| **F3+F4** | `Order` | client_propriétaire ou admin (§4.11) | non client_propriétaire, non admin | 403 | routes GET /api/commandes/<id>… |

## 4.11 — Sécuriser les accès (F4) — compléments 🥇 (chaîne de protection complétée)

```
 → 0. BASE      : role stocké ('client' par défaut, 'admin' = démo uniquement), mdp haché PBKDF2+sel
 → 1. REGISTER    : rôle forcé "client" côté serveur
 → 2. DÉMO       : UN SEUL compte admin existe (créé par init_sample_data, app.py), mdp haché — aucune route publique n'en crée d'autre
 → 3. LOGIN       : token JWT SIGNÉ (HMAC-SHA256, pas chiffré, rôle embarqué, exp 24 h)
 → 4. ROUTES      : 401 si signature invalide/expiré · 403 si rôle insuffisant
      + 🥇 NOUVEAU : 403 si client NON PROPRIÉTAIRE sur /api/commandes/<id>
        (règle « client_propriétaire ou admin » : commande.user_id == user_id du token, ou role == admin)
 → 5. .env+HTTPS  : SECRET_KEY hors git, réseau chiffré en prod
```

| Fonction métier | Objet | Protection 🥇 | Fichier |
|---|---|---|---|
| **F3+F4** | `Order` | client_propriétaire ou admin → sinon **403** | `app/routes/commandes.py`, `app/security.py` |


### Matrice de traçabilité CDC (fin de projet 🥇)

| Exigence CDC (attentes.md) | Route | Test | Statut |
|---|---|---|---|
| Inscription (étape 1) | `POST /api/auth/register` | `test_register_email_deja_utilise` (409) | ✅ 🥉 |
| Connexion + token JWT (étape 1) | `POST /api/auth/login` | `test_login_ok_renvoie_token`, `test_login_mauvais_mot_de_passe_401` | ✅ 🥈 |
| Liste/recherche/détail produits (étape 2) | `GET /api/produits[/<id>]` | `test_liste_produits_avec_recherche` | ✅ 🥈 |
| CRUD produits admin (étape 2) | `POST/PUT/DELETE /api/produits[/<id>]` | 201/401/403/400 tests | ✅ 🥈 |
| Créer une commande (étape 3) | `POST /api/commandes` | `test_creer_commande_201`, `test_stock_insuffisant_400` | 🥇 |
| Historique / suivi (étape 3) | `GET /api/commandes[/<id>]` | `test_liste_mes_commandes`, `test_commande_autre_user_403` | 🥇 |
| Lignes d'une commande (étape 3) | `GET /api/commandes/<id>/lignes` | `test_lignes_commande` | 🥇 |
| Changer le statut (admin, étape 3) | `PATCH /api/commandes/<id>/statut` | `test_patch_statut_admin_200`, `test_transition_interdite_400` | 🥇 |
| Stock décrémenté à la validation | effet de bord `Order.valider()` | `test_stock_decremente_a_validation` | 🥇 |

---

✅ **Checklist étape 4 (niveau 🥇)** : 4.1 vérif 5 tables ✅ · 4.2 temporaire ✅ · 4.3 ✅ · 4.5 ✅ · 4.6 ✅ · 4.7 ✅ · 4.9 ✅ · 4.10 ✅ · 4.11 ✅ · contrat complet ✅ · traçabilité CDC ✅.

🧵 **Fil rouge 🥇** : « passer une commande » → `POST /api/commandes` (client connecté, stock vérifié, lignes créées, total calculé) → suivi via `GET /api/commandes/<id>` → `PATCH .../statut` (admin, transition contrôlée, stock décrémenté).

❓ **Auto-évaluation** : 1) Quelles transitions de `Order` sont autorisées ? 2) Pourquoi le panier n'est pas une table (4.2) ? 3) Où est contrôlée la règle « client_propriétaire ou admin » ?

📝 **À retenir (3 lignes)** : 1) 🥇 = tout le CDC (4.1→4.11 complet). 2) Transition d'état → constantes + méthode qui contrôle (4.6). 3) Sécurité = chaîne de protection 0→5 + règle client_propriétaire-ou-admin.

---

✅ **Checklist étape 4 (niveau 🥇)** : 4.1 ✅ · 4.2 ✅ · 4.3 ✅ · 4.5 ✅ · 4.6 ✅ · 4.7 ✅ · 4.8 ✅ · 4.9 ✅ · 4.10 ✅ · 4.11 ✅ · contrat complet ✅ · traçabilité CDC ✅.

🧵 **Fil rouge 🥇** : « passer une commande » → `POST /api/commandes` → suivi `GET /api/commandes/<id>` → `PATCH .../statut` (admin ou client_propriétaire pour annulation).

❓ **Auto-évaluation** : 1) Quelles transitions de `Order` sont autorisées ? 2) Pourquoi le panier n'est pas une table (4.2) ? 3) Où est contrôlée la règle « client_propriétaire ou admin » ?

📝 **À retenir (3 lignes)** : 1) 🥇 = tout le CDC (4.1→4.11 complet). 2) Transition d'état → constantes + méthode qui contrôle (4.6). 3) Sécurité = chaîne 0→5 + client_propriétaire-ou-admin.

*Conception 🥇 prête. Prochaine étape (avec validation) : étape 5 niveau 🥇 (matrice de tests complète), puis étape 6 : `docs/etape6-backlog-confirme.md` (le backlog 🥇 y sera détaillé).*
