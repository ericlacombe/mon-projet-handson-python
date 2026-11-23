# ÉTAPE 6 — NIVEAU 🥈 : BACKLOG (à valider AVANT le code)

Règle : Avant la 1ʳᵉ ligne de code, on valide ce backlog 🥈 et, on reprend les résultats des livrables md de l'étape 4 et de l'étape 5. Le code 🥉 reste fonctionnel (on ajoute, on ne remplace pas). Chaque tâche a son « testable » = la preuve que c'est fait. On exécute la tâche suivante uniquement lorsque la tâche en cours est validée.

**BACKLOG des tâches (à valider AVANT le code)**

| ✅ | # | Tâches de code à réaliser | Source (étape · FM) | Dépend de | Fichier | Testable (preuve) |
|---|---|---|---|---|---|---|
| [x] | 1 | Modèles `Category` + `Product` (FK, relation 1—N) | étape 4 🥈 §4.1/4.5 · **F2** | — | `app/modelsSQLAlchemy.py` | import OK + `create_all` crée categories/products |
| [x] | 2 | Sécurité : `security.py` (token JWT, hachage, @login_required/@admin_required 401/403) + `.env` + PyJWT | étape 4 🥈 §4.11 · **F4** | 1 | `app/security.py`, `.env`, `requirements.txt` | `test_token_invalide_401` passe |
| [x] | 3 | Login : `POST /api/auth/login` → token JWT | étape 4 🥈 §4.7 · **F1+F4** | 1, 2 | `app/routes/auth.py` | `test_login_ok_renvoie_token` = 200 ; mauvais mdp = 401 |
| [x] | 4 | Catalogue : GET liste/recherche + détail (public), POST/PUT/DELETE (admin), prix/stock >= 0 | étape 4 🥈 §4.7/4.3 · **F2** | 1, 2 | `app/routes/produits.py`, `app/app.py` | 201 admin · 401 sans token · 403 client · 400 prix<0 |
| [x] | 5 | Catégories : `POST /api/categories` (admin) | étape 4 🥈 §4.7 · **F2** | 1, 2, 4 | `app/routes/produits.py` | 201 admin · 409 nom pris · 401 sans token |
| [x] | 6 | Les 13 tests 🥈 écrits (F1 login, F2 produits/catégories, F4 tokens) + régression | étape 5 🥈 · **F1+F2+F4** | 1–5 | `tests/test_security.py`, `tests/test_produits.py` | `pytest` tout vert |
| [x] | 7 | Données de démo au lancement : 1 admin + 1 catégorie + 2 produits | étape 4 🥈 §4.7 · **F2** (démo, indépendant des tests) | 4 | `app/app.py` | `python -m app.app` → admin + catalogue en base |
| [x] | 8 | README + canva 🥈 à jour (structure : `canva-structure-intermediaire.mmd` · tests : `canva-tests-intermediaire.mmd` — sans écraser le 🥉) + traçabilité | étapes 4 🥈 §4.8 + 5 🥈 · **doc** | 6 | `README.md`, `docs/canva-structure-intermediaire.mmd`, `docs/canva-tests-intermediaire.mmd` | relecture OK, traçabilité à jour |

**Ordre conseillé** : 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (tests à chaque incrément, régression à la fin).

---

## 📊 Résultats d'exécution des tâches (template)

| Élément | Détail |
|---|---|
| Fichiers modifiés/créés | … |
| Commandes exécutées | `pytest tests/ -q`, vérif manuelle |
| Résultat | … |
| Tests exécutés | `pytest tests/ -q` → X passed = 🥉 (1 : `test_auth.py`) + 🥈 (13) → régression OK |
| Nouveaux tests écrits | … |
| Backlog | tâche N cochée + commit poussé + résultat mis à jour ici + **cohérence des commentaires vérifiée** |

### ✅ Niveau 🥈 — résultat global
- **Commandes** : `./venv/bin/python -m pytest tests/ -q` → **14 passed** (🥉 1 + 🥈 13)
- **Résultat** : F2 (catalogue) + F4 (sécurité JWT) + login F1 livrés et testés — 8/8 tâches cochées
- (détail tâche par tâche : conservé dans l'historique git du fichier)

---

**DoD niveau 🥈** (Definition of Done) :

- [x] **code 🥈 fonctionnel (contrat 4.7 : 8 routes répondent)** ;
  > *Vérifié par* : smoke test des routes `/api/produits`, `/api/categories`, `/api/auth/login` (201/200 · 400 · 401 · 403 · 409).
- [x] **`pytest` vert : 14 passed (🥉 1 + 🥈 13)** ;
  > *Vérifié par* : `./venv/bin/python -m pytest tests/ -q` → `14 passed`.
- [x] **README + canva 🥈 à jour** ;
  > *Vérifié par* : relecture README + `canva-structure-intermediaire.mmd` (🥉 figé non écrasé).
- [x] **commits clairs** ;
- [x] **démo au lancement (admin + catégorie + 2 produits)** ;
  > *Vérifié par* : `python -m app.app` → `init_sample_data()` crée le compte admin de démo + le catalogue.

✅ **Niveau 🥈 terminé** — F2 (catalogue) + F4 (sécurité JWT) + login F1 livrés et testés.

⚠️ CDC : `POST /api/categories` non listé en route mais « gestion des catégories » exigée → on le garde (admin).
