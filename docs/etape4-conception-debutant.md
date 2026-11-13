# ÉTAPE 4 appliquée à DigiMarket — NIVEAU 🥉 DÉBUTANT (fil rouge : « S'inscrire »)

⏱️ **~2 h — difficile** (au total sur les 3 niveaux ; ici seulement le niveau 🥉)

**Principe** : on croise les résultats des étapes 1, 2 et 3. Règle à dire à voix haute : *« analyse → condition → si positif, ACTION de création »*, et *« si la condition est fausse, que se passe-t-il ? »*.

Niveau 🥉 = seules les parties **4.1, 4.4, 4.7 (1 route), 4.8, 4.10 basique** sont traitées, appliquées au **fil rouge** « S'inscrire » (Visiteur → cas étape 1 → F1 « Gérer les comptes » étape 2 → objet `Utilisateur` étape 3).

---

## 4.1 — Base de données (condition : `Utilisateur` est persisté ✅ → ACTION)

Création de la base SQLite `digimarket.db` et de la table `utilisateurs` :

```sql
-- Table des comptes utilisateurs (objet Utilisateur persisté, étape 3)
CREATE TABLE utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,       -- PK : identifiant unique, auto-incrémenté
    email VARCHAR(255) NOT NULL UNIQUE,          -- UK + obligatoire : un seul compte par email
    mot_de_passe_hash VARCHAR(255) NOT NULL,     -- mot de passe JAMAIS en clair, toujours haché
    nom VARCHAR(100) NOT NULL,                   -- obligatoire
    prenom VARCHAR(100) NOT NULL,                -- obligatoire
    adresse TEXT,                                -- optionnelle
    role VARCHAR(20) NOT NULL DEFAULT 'client'  -- 'client' par défaut, 'admin' pour les administrateurs
);
```

## 4.4 — Classe `Utilisateur` (condition : objet avec état persistant ✅ → ACTION)

```python
# modelsSQLAlchemy.py (extrait) — même style que le projet précédent (SQLAlchemy pur, pas Flask-SQLAlchemy)
# Pourquoi une classe ? Parce que l'objet Utilisateur a un état PERSISTANT :
# il doit vivre en base au-delà d'une seule requête (règle 4.4) → on crée une classe.
# (Un objet temporaire, ex. le token JWT décodé, n'aurait PAS de classe — règle 4.2.)
from sqlalchemy import Column, Integer, String, Text

class Utilisateur(Base):                                  # Base = declarative_base(), définie dans modelsSQLAlchemy.py
    __tablename__ = "utilisateurs"                        # nom de la table en base

    id = Column(Integer, primary_key=True)                # PK : id unique, auto-incrémenté
    email = Column(String(255), unique=True, nullable=False)   # UK : unicité de l'email garantie en base
    mot_de_passe_hash = Column(String(255), nullable=False)    # hash du mot de passe, jamais en clair
    nom = Column(String(100), nullable=False)             # obligatoire
    prenom = Column(String(100), nullable=False)          # obligatoire
    adresse = Column(Text)                                # optionnelle
    role = Column(String(20), nullable=False, default="client")  # 'client' par défaut, 'admin' sinon

    def __repr__(self):                                   # affichage lisible avec print()
        return f"<Utilisateur {self.email}>"
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
    # ... création de l'Utilisateur en base (session.add + commit) ...
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
│   └── utilisateur.py      # classe Utilisateur (4.4)
└── routes/
    └── auth.py             # blueprint auth_bp + POST /api/auth/register (4.7, 4.8)
digimarket.db               # base SQLite, table utilisateurs (4.1)
```

---

✅ **Checklist étape 4 (niveau 🥉)** :
- [x] 4.1 base créée (condition persisté ✅) → table `utilisateurs` ;
- [x] 4.4 classe créée → `Utilisateur` ;
- [x] 4.7 une route créée → `POST /api/auth/register` + contrat ;
- [x] 4.8 un module créé → `routes/auth.py` ;
- [x] 4.10 erreurs basiques → 400/409 en JSON ;
- [x] arborescence de fichiers produite (ci-dessus).

⚠️ **Piège évité** : pas de classe pour le token JWT (donnée temporaire, 4.2 — hors niveau 🥉).

🧰 **Bonnes pratiques à ce stade** :
- README : section « Structure du projet » = l'arborescence ci-dessus ;
- commit Git de cette étape (ce push).

🧵 **Fil rouge** : « S'inscrire » → table `utilisateurs` + classe `Utilisateur` + route `POST /api/auth/register` + module `auth.py` + erreurs 400/409.

❓ **Auto-évaluation** :
1. Quelle est la règle de l'étape 4 (à dire à voix haute) ?
2. Pourquoi une classe `Utilisateur` mais pas de classe pour le token ?
3. Quelles sont les sorties de la route `POST /api/auth/register` ?

📝 **À retenir (3 lignes)** :
1) Étape 4 : analyse → condition → si positif, ACTION de création (et si faux, on demande ce qui se passe).
2) Niveau 🥉 = 4.1 base + 4.4 classe + 4.7 une route + 4.8 un module + 4.10 erreurs basiques, sur UN fil rouge.
3) Sortie de l'étape 4 = l'arborescence de fichiers à créer.

---
*Étape 4 niveau 🥉 ✅. En attente de votre accord pour l'étape 5 niveau 🥉 (1 test unitaire : `test_register_email_deja_utilise` → 409).*
