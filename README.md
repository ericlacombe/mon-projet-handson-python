# Mon projet handson — DigiMarket (API REST Flask)

📖 **Méthode suivie** : ce projet suit la méthode décrite dans **[methodologie.md](docs/methodologie.md)** (étapes 0–6 + niveaux 🥉🥈🥇). Chaque fichier ci-dessous est **le résultat d'une étape, par niveau** (conception puis code) :

- Étape 0 — AFB (besoins) → [docs/etape0-AFB.md](docs/etape0-AFB.md)
- Étape 1 — use cases → [docs/etape1-use-cases.md](docs/etape1-use-cases.md)
- Étape 2 — fonctions métier → [docs/etape2-fonctions-metier.md](docs/etape2-fonctions-metier.md)
- Étape 3 — objets (schéma ER) → [docs/etape3-objets.md](docs/etape3-objets.md)
- Étape 4 — conception → 🥉 [docs/etape4-conception-debutant.md](docs/etape4-conception-debutant.md) · 🥈 [docs/etape4-intermediaire.md](docs/etape4-intermediaire.md)
- Étape 5 — tests → 🥉 [docs/etape5-tests-debutant.md](docs/etape5-tests-debutant.md) · 🥈 [docs/etape5-tests-intermediaire.md](docs/etape5-tests-intermediaire.md)
- Étape 6 — backlog + code → 🥉 [docs/etape6-backlog-debutant.md](docs/etape6-backlog-debutant.md) · 🥈 etape6-backlog-intermediaire.md (à venir)

## Niveaux de réalisation (répartition par complexité — règle dans methodologie.md)

| Niveau | Fonctions métier | État |
|---|---|---|
| 🥉 débutant | **F1 — Gérer les comptes** (register + hachage) | ✅ fait et testé (`pytest` = 1 passed) — aussi figé dans `mon-premier-projet` |
| 🥈 intermédiaire | **F2 — catalogue** + **F4 — sécurité JWT** | ✅ fait — code + 13 tests (`pytest` = 14 passed) |
| 🥇 confirmé | **F3 — Gérer les commandes** (états, stock, historique) | ⏳ à venir |

## Conventions (étape 0)
- snake_case pour les variables et fonctions
- PascalCase pour les classes
- routes au pluriel : /api/produits, /api/commandes

## Fonctionnalités — cas d'utilisation (étape 1, avec niveau)
- **Visiteur** : s'inscrire 🥉 ✅ · se connecter 🥈 🚧 · consulter le catalogue / rechercher / détail produit 🥈 🚧
- **Client** : passer une commande, historique, suivre l'état 🥇 ⏳
- **Administrateur** : gérer les produits et stocks 🥈 🚧 · voir toutes les commandes, changer le statut 🥇 ⏳

## Fonctions métier (étape 2, avec niveau)
- **F1 — Gérer les comptes** 🥉 ✅ (register fait ; login 🥈 🚧) : inscription, connexion, token JWT
- **F2 — Gérer le catalogue** 🥈 🚧 : liste, recherche, détail, CRUD produits, gestion des stocks
- **F3 — Gérer les commandes** 🥇 ⏳ : commander, historique, suivi, changement de statut, lignes
- **F4 — Sécuriser les accès** 🥈 🚧 : hachage (🥉 ✅ dans register), vérification JWT, contrôle des rôles

## Modèle de données — objets (étape 3, avec niveau)
- **Utilisateur** 🥉 ✅ : id, email (unique), mot_de_passe_hash, nom, prenom, adresse, role
- **Categorie** 🥈 🚧 : id, nom (unique)
- **Produit** 🥈 🚧 : id, nom, description, prix, stock, categorie_id (FK)
- **Commande** 🥇 ⏳ : id, utilisateur_id (FK), adresse_livraison, statut (en_attente | validée | expédiée | annulée), date_creation
- **LigneCommande** 🥇 ⏳ : id, commande_id (FK), produit_id (FK), quantite, prix_unitaire

Liens : Utilisateur 1—N Commande · Categorie 1—N Produit · Produit 1—N LigneCommande · Commande 1—N LigneCommande
(détail complet dans `etape3-objets.md`, schéma ER + PK/FK/UK)

## Structure du projet (étape 4 → code étape 6, niveaux 🥉 fait / 🥈 en cours)
```
mon-projet-handson-python/
├── README.md                   # ce fichier (page d'entrée)
├── requirements.txt            # flask, sqlalchemy, pytest, PyJWT
├── .env                        # 🥈 SECRET_KEY (jamais commité, .gitignore)
├── app/                        # 💻 code de l'API (package Python)
│   ├── security.py             # 🥈 F4 : JWT, hachage, décorateurs 401/403
│   ├── __init__.py           # rend app/ importable comme package Python
│   ├── app.py                  # point d'entrée Flask (app, blueprints, app.run)
│   ├── db.py                   # engine SQLite + session partagée (SQLAlchemy pur)
│   ├── modelsSQLAlchemy.py     # 🥉 User · 🥈 Category, Product (relation 1—N)
│   └── routes/
│       ├── auth.py             # 🥉 register · 🥈 login (token JWT)
│       └── produits.py       # 🥈 F2 : CRUD /api/produits + /api/categories
├── tests/                      # 🧪 dossier dédié aux tests
│   ├── test_auth.py            # 🥉 test_register_email_deja_utilise (409)
│   ├── conftest.py             # 🥈 fixtures communes (base en mémoire, tokens)
│   ├── test_security.py        # 🥈 F1 login + F4 tokens (401)
│   └── test_produits.py        # 🥈 F2 CRUD produits/catégories (201/400/401/403/409)
└── docs/                       # 📚 toute la documentation
    ├── attentes.md             # cahier des charges
    ├── methodologie.md         # la méthode (étapes 0–6 + niveaux)
    ├── methodologie-canva.mmd  # schéma visuel (Mermaid)
    ├── etape0-AFB.md … etape6-backlog-debutant.md   # résultat de chaque étape (🥉)
    ├── etape4-intermediaire.md, etape5-tests-intermediaire.md   # 🥈
    └── canva-structure-debutant.mmd / canva-structure-intermediaire.mmd   # canva par niveau
```
(digimarket.db est créée automatiquement au lancement, à la racine)

📊 Cette structure est illustrée dans les canva : 🥉 **[docs/canva-structure-debutant.mmd](docs/canva-structure-debutant.mmd)** (figé) · 🥈 **[docs/canva-structure-intermediaire.mmd](docs/canva-structure-intermediaire.mmd)** (en cours).

## API — routes du niveau 🥈 (contrat complet dans docs/etape4-intermediaire.md §4.7)

| Fonction métier | Objet(s) | Méthode | Route | Accès | Codes |
|---|---|---|---|---|---|
| F1 | `User` | POST | `/api/auth/register` | Public | 201 · 400 · 409 (🥉 ✅ fait) |
| F1+F4 | `User` → token | POST | `/api/auth/login` | Public | 200 + JWT · 401 (🥈 🚧) |
| F2 | `Product` | GET | `/api/produits` (`?q=` recherche) | Public | 200 (🥈 🚧) |
| F2 | `Product` | GET | `/api/produits/<id>` | Public | 200 · 404 (🥈 🚧) |
| F2+F4 | `Product`, `Category` | POST/PUT/DELETE | `/api/produits[/<id>]` | **Admin** (Bearer token) | 201/200/204 · 400 · 401 · 403 (🥈 🚧) |

## Installation et lancement (étape 6)
```bash
python -m venv venv                # crée un environnement virtuel isolé (dossier venv/) : les bibliothèques du projet n'installent PAS dans ton Python global
source venv/bin/activate           # active cet environnement (Windows : venv\Scripts\activate) — toutes les commandes suivantes (pip, python) l'utilisent
pip install -r requirements.txt    # installe toutes les bibliothèques listées dans requirements.txt (flask, sqlalchemy, pytest) — la "liste de courses" du projet : mêmes versions pour tout le monde
python -m app.app               # lance l'API sur http://127.0.0.1:5000 (depuis la racine)
# 💡 au niveau 🥈 : créer d'abord un fichier .env avec SECRET_KEY=... (jamais commité)
```

## Comment tester (étape 5)
```bash
pytest            # depuis la racine : lance tous les tests (14 tests : 🥉 1 + 🥈 13)
```

## Fichiers du projet (avec niveau)
| Fichier | Niveau | Description |
|---|---|---|
| 🥉 | `docs/attentes.md` | Cahier des charges de l'exercice (DigiMarket) |
| 🥉 | `docs/methodologie.md` | Méthode de travail en 6 étapes + 3 niveaux (🥉🥈🥇) — voir le lien en haut de ce README |
| 🥉 | `docs/methodologie-canva.mmd` | Schéma visuel (Mermaid) de la méthode |
| 🥉 | `docs/etape0-AFB.md` | Étape 0 : liste des besoins 🔵 et contraintes 🟠 |
| 🥉 | `docs/etape1-use-cases.md` | Étape 1 : acteurs, cas d'utilisation, matrice des rôles |
| 🥉 | `docs/etape2-fonctions-metier.md` | Étape 2 : fonctions métier F1–F4 + flux « Passer une commande » |
| 🥉 | `docs/etape3-objets.md` | Étape 3 : schéma ER (5 objets, PK/FK/UK), cycle de vie de Commande |
| 🥉 | `docs/etape4-conception-debutant.md` | Étape 4 niveau 🥉 : base, classe, route, module, erreurs (fil rouge) |
| 🥉 | `docs/etape5-tests-debutant.md` | Étape 5 niveau 🥉 : 1 test unitaire (409 email déjà pris) |
| 🥉 | `docs/etape6-backlog-debutant.md` | Étape 6 niveau 🥉 : backlog cochée, code fonctionnel (register + test) |
| 🥈 | `docs/etape4-intermediaire.md` | Étape 4 niveau 🥈 : conception F2+F4 (contraintes, relations, sécurité JWT) |
| 🥈 | `docs/etape5-tests-intermediaire.md` | Étape 5 niveau 🥈 : tests unitaires + intégration + 401/403 |
| 🥈 | `docs/canva-structure-intermediaire.mmd` | Canva de la structure niveau 🥈 (🥉 figé dans canva-structure-debutant.mmd) |
| 🥉 | `requirements.txt` | Dépendances (flask, sqlalchemy, pytest) |
| 🥉 | `app/__init__.py` | Package Python (rend app/ importable depuis la racine) |
| 🥉 | `app/app.py` | Point d'entrée Flask |
| 🥉 | `app/db.py` | Moteur SQLite + session partagée |
| 🥉 | `app/modelsSQLAlchemy.py` | Modèle User (table users) |
| 🥉 | `app/routes/auth.py` | Route POST /api/auth/register |
| 🥉 | `tests/test_auth.py` | 🧪 Test 409 email déjà pris |
| 🥉 | `README.md` | Ce fichier |
