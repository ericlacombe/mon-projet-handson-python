# ÉTAPE 4 appliquée à DigiMarket — NIVEAU 🥉 DÉBUTANT (conception AVANT code) — fil rouge « S'inscrire »

⏱️ **~2 h — difficile** (au total sur les 3 niveaux ; ici seulement le niveau 🥉)

**Principe** : on croise les résultats des étapes 1, 2 et 3. Règle à dire à voix haute : *« analyse → condition → si positif, ACTION de création »*, et *« si la condition est fausse, que se passe-t-il ? »*.

Niveau 🥉 = seules les parties **4.1, 4.4, 4.7 (1 route), 4.8, 4.10 basique** sont traitées, appliquées au **fil rouge** « S'inscrire » (Visiteur → cas étape 1 → F1 « Gérer les comptes » étape 2 → objet `User` étape 3).

---

## 📋 Tableau récap — ce qu'on crée au niveau 🥉

| Fonction métier | Objet(s) | Routes | Fichiers à créer |
|---|---|---|---|
| **F1** Gérer les comptes | `User` | `POST /api/auth/register` | `app/app.py`, `app/db.py`, `app/modelsSQLAlchemy.py`, `app/routes/auth.py`, `requirements.txt` |

## 4.1 — Base de données (condition : `User` est persisté ✅ → ACTION)

Création de la base SQLite `digimarket.db` et de sa table `users`.

Deux choses différentes :
- **`digimarket.db`** = le FICHIER de base SQLite, créé automatiquement par `db.py` :
  `engine = create_engine("sqlite:///digimarket.db")` (chemin relatif = dossier du projet).
- **la table `users`** = créée par `Base.metadata.create_all(engine)` (dans `db.py`) à partir
  de la classe `User` définie dans `modelsSQLAlchemy.py` (`__tablename__ = "users"`, §4.4) :

```sql
-- Table des comptes (objet User persisté, étape 3) — créée via la classe User, pas à la main
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,       -- PK : identifiant unique, auto-incrémenté
    email VARCHAR(255) NOT NULL UNIQUE,          -- UK + obligatoire : un seul compte par email (409)
    password_hash VARCHAR(255) NOT NULL,         -- mot de passe JAMAIS en clair, toujours haché
    first_name VARCHAR(100) NOT NULL,            -- obligatoire
    last_name VARCHAR(100) NOT NULL,             -- obligatoire
    address TEXT,                                -- optionnelle
    role VARCHAR(20) NOT NULL DEFAULT 'client'  -- 'client' par défaut, 'admin' pour les administrateurs
);
```

## 4.4 — Classe `User` (condition : objet avec état persistant ✅ → ACTION)

```python
# modelsSQLAlchemy.py (extrait) — même style que le projet précédent (SQLAlchemy pur, pas Flask-SQLAlchemy)
# Pourquoi une classe ? Parce que l'objet User a un état PERSISTANT :
# il doit vivre en base au-delà d'une seule requête (règle 4.4) → on crée une classe.
# (Un objet temporaire, ex. le token JWT décodé, n'aurait PAS de classe — règle 4.2.)
from sqlalchemy import Column, Integer, String, Text

class User(Base):                                  # Base = declarative_base(), définie dans modelsSQLAlchemy.py
    __tablename__ = "users"                        # nom de la table en base

    id = Column(Integer, primary_key=True)                # PK : id unique, auto-incrémenté
    email = Column(String(255), unique=True, nullable=False)   # UK : unicité de l'email garantie en base
    mot_de_passe_hash = Column(String(255), nullable=False)    # hash du mot de passe, jamais en clair
    nom = Column(String(100), nullable=False)             # obligatoire
    prenom = Column(String(100), nullable=False)          # obligatoire
    adresse = Column(Text)                                # optionnelle
    role = Column(String(20), nullable=False, default="client")  # 'client' par défaut, 'admin' sinon

    def __repr__(self):                                   # affichage lisible avec print()
        return f"<User {self.email}>"
```

## 4.7 — La route du fil rouge : `POST /api/auth/register` (condition : API REST ✅ → ACTION)

| Méthode | Route | Accès | Entrée (JSON) | Sorties / codes |
|---|---|---|---|---|
| POST | `/api/auth/register` | Public | `{email, mot_de_passe, nom, prenom, adresse}` | `201` utilisateur créé (JSON) · `400` données invalides · `409` email déjà utilisé |

## 4.8 — Module `routes/auth.py` (condition : fonction métier F1 ✅ → ACTION)

```python
# routes/auth.py
from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Pourquoi une route ? Pour relier une requête URL (ici POST /api/auth/register)
# à un endpoint (la fonction register ci-dessous) où le code est appelé.
@auth_bp.route("/register", methods=["POST"])     # la route = l'URL + la méthode HTTP (le "panneau du guichet")
def register():                                    # l'endpoint = la fonction exécutée quand on atteint cette URL
    """F1 « Gérer les comptes » : inscrit un nouvel utilisateur (fil rouge)."""
    data = request.get_json() or {}                # corps JSON de la requête ({} si vide)
    # 4.10 : si un champ obligatoire manque → erreur 400 renvoyée en JSON
    if not data.get("email") or not data.get("mot_de_passe"):
        return jsonify({"erreur": "email et mot_de_passe requis"}), 400   # réponse JSON + code HTTP 400
    # ... création de l'User en base (session.add + commit) ...
    return jsonify({"message": "utilisateur créé", "email": data["email"]}), 201  # 201 = ressource créée
```

## 4.10 — Gestion des erreurs basiques (condition : branches d'erreur du flux ✅ → ACTION)

| Code | Cas | Réponse JSON |
|---|---|---|
| `400` | JSON invalide / champs manquants | `{"erreur": "..."}` |
| `409` | email déjà utilisé | `{"erreur": "email déjà utilisé"}` |

## 👉 Sortie de l'étape 4 (niveau 🥉) : arborescence de fichiers à créer

```
app/
├── app.py                  # point d'entrée Flask (crée l'app, enregistre auth_bp)
├── models/
│   └── modelsSQLAlchemy.py # classe User, table users (4.4)
└── routes/
    └── auth.py             # blueprint auth_bp + POST /api/auth/register (4.7, 4.8)
digimarket.db               # FICHIER base SQLite créé par db.py (create_engine), table users créée par create_all (4.1)
```


---

✅ **Checklist étape 4 (niveau 🥉)** : 4.1 base ✅ · 4.4 classe `User` ✅ · 4.7 (1 route) ✅ · 4.8 (1 module) ✅ · 4.10 basique (409) ✅ · arborescence ✅.

🧵 **Fil rouge 🥉** : « S'inscrire » → `POST /api/auth/register` → 201 (puis 409 si email pris).

❓ **Auto-évaluation** : 1) Pourquoi une classe pour `User` et pas pour le token ? 2) Pourquoi un blueprint plutôt que la route dans app.py ? 3) Quels codes renvoie register ?

📝 **À retenir (3 lignes)** : 1) 🥉 = 4.1 + 4.4 + 4.7 (1 route) + 4.8 + 4.10 basique. 2) Un objet persistant = une classe ; temporaire = un dict (4.2). 3) Une route = URL + endpoint dans un blueprint.

*Conception 🥉 prête. Prochaine étape (avec validation) : étape 5 niveau 🥉 (1 test unitaire), puis étape 6 : `docs/etape6-backlog-debutant.md`.*
