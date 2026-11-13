# ÉTAPE 6 — NIVEAU 🥈 : BACKLOG (à valider AVANT le code)

Règle : on valide ce backlog avant la 1ère ligne de code 🥈. Chaque tâche a son « testable » = la preuve que c'est fait.

| ✅ | # | Tâche | Depuis étape 4 🥈 | Fichier | Testable (preuve) |
|---|---|---|---|---|---|
| [x] | 1 | Modèles `Category` + `Product` (FK, relation 1—N) | objets F2 (4.5) | `app/modelsSQLAlchemy.py` | import OK + `create_all` crée les tables |
| [x] | 2 | Sécurité : `security.py` (token JWT, hachage, décorateurs 401/403) + `.env` + PyJWT | F4 (4.11) | `app/security.py`, `.env`, `requirements.txt` | `test_token_invalide_401` passe |
| [x] | 3 | Login : `POST /api/auth/login` → token JWT | route F1 (4.7) | `app/routes/auth.py` | `test_login_ok_renvoie_token` = 200 ; mauvais mdp = 401 |
| [x] | 4 | Catalogue : GET liste/recherche + détail (public), POST/PUT/DELETE (admin) + prix/stock >= 0 | routes F2 (4.7) + contraintes (4.3) | `app/routes/produits.py`, `app/app.py` | 201 admin · 401 sans token · 403 client · 400 prix<0 |
| [x] | 5 | Catégories : `POST /api/categories` (admin) | objet `Category` + CDC contexte | `app/routes/produits.py` | 201 admin · 409 nom pris · 401 sans token |
| [x] | 6 | Les 13 tests 🥈 écrits (F1 login, F2 produits/catégories, F4 tokens) | matrice étape 5 🥈 | `tests/test_security.py`, `tests/test_produits.py` | `pytest` tout vert |
| [ ] | 7 | Données de démo au lancement : 1 admin + 1 catégorie + 2 produits | livrable CDC « données de test » | `app/app.py` | `python -m app.app` → admin en base |
| [ ] | 8 | README + canva 🥈 à jour | arborescence 4.8 | `README.md`, `docs/canva-structure-intermediaire.mmd` | relecture OK |

**Ordre conseillé** : 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (tests à chaque incrément).

**DoD niveau 🥈** : code 🥈 fonctionnel (contrat 4.7) · `pytest` vert · README/canva à jour · commits clairs · démo au lancement.

⚠️ CDC : `POST /api/categories` non listé en route mais « gestion des catégories » exigée → on le garde (admin).
