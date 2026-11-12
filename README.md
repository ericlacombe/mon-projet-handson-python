# Mon projet handson — DigiMarket (API REST Flask)

📖 **Méthode suivie** : ce projet suit la méthode décrite dans **[methodologie.md](docs/methodologie.md)** (étapes 0–6 + niveaux 🥉🥈🥇). Chaque fichier ci-dessous est **le résultat d'une étape** de cette méthode (conception puis code) :

- Étape 0 — AFB (besoins) → [docs/etape0-AFB.md](docs/etape0-AFB.md)
- Étape 1 — use cases → [docs/etape1-use-cases.md](docs/etape1-use-cases.md)
- Étape 2 — fonctions métier → [docs/etape2-fonctions-metier.md](docs/etape2-fonctions-metier.md)
- Étape 3 — objets (schéma ER) → [docs/etape3-objets.md](docs/etape3-objets.md)
- Étape 4 — conception 🥉 → [docs/etape4-conception-debutant.md](docs/etape4-conception-debutant.md)
- Étape 5 — tests 🥉 → [docs/etape5-tests-debutant.md](docs/etape5-tests-debutant.md)
- Étape 6 — backlog + code 🥉 → [docs/etape6-backlog-debutant.md](docs/etape6-backlog-debutant.md)

## Niveaux de réalisation (répartition par complexité — règle dans methodologie.md)

| Niveau | Fonctions métier | État |
|---|---|---|
| 🥉 débutant | **F1 — Gérer les comptes** (register + hachage) | ✅ fait et testé (`pytest` = 1 passed) — aussi figé dans `mon-premier-projet` |
| 🥈 intermédiaire | **F2 — catalogue** + **F4 — sécurité JWT** | 🚧 en cours — conception faite (`docs/etape4-intermediaire.md`, `docs/etape5-tests-intermediaire.md`) |
| 🥇 confirmé | **F3 — Gérer les commandes** (états, stock, historique) | ⏳ à venir |

## Conventions (étape 0)
- snake_case pour les variables et fonctions
- PascalCase pour les classes
- routes au pluriel : /api/produits, /api/commandes

## Fonctionnalités — cas d'utilisation (étape 1)
- **Visiteur** : s'inscrire, se connecter, consulter le catalogue, rechercher un produit, voir le détail d'un produit
- **Client** : en plus, passer une commande, consulter son historique de commandes, suivre l'état d'une commande
- **Administrateur** : gérer les produits et les stocks, voir toutes les commandes, changer le statut d'une commande

## Fonctions métier (étape 2)
- **F1 — Gérer les comptes** : inscription, connexion, émission du token JWT
- **F2 — Gérer le catalogue** : liste, recherche, détail, CRUD produits, gestion des stocks
- **F3 — Gérer les commandes** : passer une commande, historique, suivi, changement de statut, lignes
- **F4 — Sécuriser les accès** : hachage des mots de passe, vérification JWT, contrôle des rôles

## Modèle de données — objets (étape 3)
- **Utilisateur** : id, email (unique), mot_de_passe_hash, nom, prenom, adresse, role
- **Categorie** : id, nom (unique)
- **Produit** : id, nom, description, prix, stock, categorie_id (FK)
- **Commande** : id, utilisateur_id (FK), adresse_livraison, statut (en_attente | validée | expédiée | annulée), date_creation
- **LigneCommande** : id, commande_id (FK), produit_id (FK), quantite, prix_unitaire

Liens : Utilisateur 1—N Commande · Categorie 1—N Produit · Produit 1—N LigneCommande · Commande 1—N LigneCommande
(détail complet dans `etape3-objets.md`, schéma ER + PK/FK/UK)

## Structure du projet (étape 4 → code étape 6, niveau 🥉)
```
mon-premier-projet/
├── README.md                   # ce fichier (page d'entrée)
├── requirements.txt            # flask, sqlalchemy, pytest (+ PyJWT au 🥈)
├── .env                        # 🥈 à venir : SECRET_KEY (jamais commité)
├── app/                        # 💻 code de l'API (package Python)
│   └── security.py             # 🥈 à venir (F4 : JWT, hachage, décorateurs)
│   ├── __init__.py           # rend app/ importable comme package Python
│   ├── app.py                  # point d'entrée Flask (app, blueprints, app.run)
│   ├── db.py                   # engine SQLite + session partagée (SQLAlchemy pur)
│   ├── modelsSQLAlchemy.py     # 🥉 User · 🥈 + Category, Product (à venir)
│   └── routes/
│       ├── auth.py             # 🥉 register · 🥈 + login (à venir)
│       └── produits.py       # 🥈 à venir (F2 : CRUD /api/produits)
├── tests/                      # 🧪 dossier dédié aux tests
│   └── test_auth.py            # test_register_email_deja_utilise (409)
└── docs/                       # 📚 toute la documentation
    ├── attentes.md             # cahier des charges
    ├── methodologie.md         # la méthode (étapes 0–6 + niveaux)
    ├── methodologie-canva.mmd  # schéma visuel (Mermaid)
    └── etape0-AFB.md … etape6-backlog-debutant.md   # résultat de chaque étape
```
(digimarket.db est créée automatiquement au lancement, à la racine)

📊 Cette structure est illustrée dans le canva **[docs/canva-structure-debutant.mmd](docs/canva-structure-debutant.mmd)** (niveau 🥉 débutant).

## Fonctionnement d'une requête (exemple : POST /api/auth/register)
```
client HTTP
  POST /api/auth/register
        │
        ▼
app/app.py        Flask + blueprint enregistré
        │
        ▼
routes/auth.py    endpoint register()  ──►  400 si champs manquants
        │                                  409 si email déjà pris
        ▼
db.py             session SQLAlchemy
        │
        ▼
digimarket.db     table users  (modèle User défini dans modelsSQLAlchemy.py)
        │
        └── retour ──► réponse JSON 201
```

## Installation et lancement (étape 6)
```bash
python -m venv venv                # crée un environnement virtuel isolé (dossier venv/) : les bibliothèques du projet n'installent PAS dans ton Python global
source venv/bin/activate           # active cet environnement (Windows : venv\Scripts\activate) — toutes les commandes suivantes (pip, python) l'utilisent
pip install -r requirements.txt    # installe toutes les bibliothèques listées dans requirements.txt (flask, sqlalchemy, pytest) — la "liste de courses" du projet : mêmes versions pour tout le monde
python -m app.app               # lance l'API sur http://127.0.0.1:5000 (depuis la racine)
```

## Comment tester (étape 5)
```bash
pytest            # depuis la racine : lance tous les tests (ici : tests/test_auth.py → 409)
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
