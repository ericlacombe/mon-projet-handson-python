# ÉTAPE 6 — NIVEAU 🥇 : BACKLOG (à valider AVANT le code)

Règle : Avant la 1ʳᵉ ligne de code, on valide ce backlog 🥇 et, on reprend les résultats des livrables md de l'étape 4 et de l'étape 5. Le code 🥉/🥈 reste fonctionnel (on ajoute, on ne remplace pas). Chaque tâche a son « testable » = la preuve que c'est fait. On exécute la tâche suivante uniquement lorsque la tâche en cours est validée.

| ✅ | # | Tâches de code à réaliser | Source (étape · FM) | Dépend de | Fichier | Testable (preuve) |
|---|---|---|---|---|---|---|
| [x] | 1 | Modèles `Order` + `OrderItem` (FK, relations 4.5, `STATUTS`/`TRANSITIONS`/`changer_statut` 4.6) | étape 4 🥇 §4.1/4.5/4.6 · **F3** | — | `app/modelsSQLAlchemy.py` | import OK + `create_all` crée orders/order_items + `test_transition_autorisee/interdite` |
| [x] | 2 | Fonctions pures 4.9 : `calculer_total` (sur `Order`/`OrderItem`), `verifier_stock` (sur `Product`) | étape 4 🥇 §4.9 · **F3** | 1 | `app/utils.py` | `test_calculer_total`, `test_verifier_stock_*` passent |
| [x] | 3 | Blueprint `routes/commandes.py` manipulant `Order`, `OrderItem`, `Product` : POST (vérif stock, lignes, total), GET liste/détail/lignes, PATCH statut + règle 403 client_propriétaire (4.11) ; transitions 4.6 ; stock décrémenté/restitué | étapes 4 🥇 §4.7/4.3/4.11 + 5 🥇 · **F3+F4** | 1, 3 | `app/routes/commandes.py`, `app/app.py` | 201/400/401/403/404 sur chaque route (tests d'intégration) |
| [x] | 4 | Gestionnaire d'erreurs global 4.10 : `@app.errorhandler(404/405/500)` en JSON | étape 4 🥇 §4.10 · **global** | 4 | `app/app.py` | route inconnue → 404 JSON ; mauvaise méthode → 405 JSON |
| [x] | 5 | `conftest.py` : brancher la session de test dans `routes/commandes.py` (`cmd_module.session = S`) — sinon les tests écrivent dans la vraie base | étape 5 🥇 · **F3** (infra tests) | 1 | `tests/conftest.py` | import de `app.routes.commandes` OK, session remplacée |
| [x] | 6 | Les ~12 tests 🥇 écrits (`test_commandes.py`) + régression : tout `pytest` rejoué | étape 5 🥇 · **F3+F4** | 1, 3, 4, 5 | `tests/test_commandes.py` | `pytest` tout vert (14 + ~12) |
| [x] | 7 | Données de démo 🥇 : 1 commande (`Order` + `OrderItem`) exemple pour le client de démo (**indépendant des tests** : base en mémoire) | étape 4 🥇 §4.7 · **F3** | 4 | `app/app.py` | `python -m app.app` → commande en base |
| [ ] | 8 | README + **canva 🥇 à jour** (structure : `docs/canva-structure-confirme.mmd` · tests : `docs/canva-tests.mmd` — sans écraser les précédents) + matrice de traçabilité CDC complète | étapes 4 🥇 §4.8 + 5 🥇 · **doc** | 6 | `README.md`, `docs/canva-structure-confirme.mmd`, `docs/canva-tests.mmd` | relecture OK, traçabilité complète |

> 📝 §4.2 (panier) : donnée temporaire **côté client**, pas de table → rien à coder côté API.


**Ordre conseillé** : 1 → 2 → 3 → 4 → 5 (conftest) → 6 (tests) → 7 → 8 (tests à chaque incrément, régression à la fin).

---

## 📊 Résultats d'exécution des tâches (template)

| Élément | Détail |
|---|---|
| Fichiers modifiés/créés | … |
| Commandes exécutées | `pytest tests/ -q`, vérif manuelle `python -c "..."` |
| Résultat | … |
| Tests exécutés | `pytest tests/ -q` → X passed = 🥉 (1 : `test_auth.py`) + 🥈 (13 : `test_security.py`, `test_produits.py`) → régression OK |
| Nouveaux tests 🥇 écrits | aucun (prévus tâche 6) — ou liste |
| Backlog | tâche N cochée + commit poussé + **résultat de la tâche mis à jour dans cette section** (sous-tâches : remplir le bloc ✅ de la tâche · **s'assurer de la cohérence des commentaires explicatifs du code** avec les autres fichiers) |

### ✅ Tâche 1 — Modèles `Order` + `OrderItem`
- **Fichiers** : `app/modelsSQLAlchemy.py`
- **Commandes** : `./venv/bin/python -c "from app.modelsSQLAlchemy import Base, Order, OrderItem; print(sorted(Base.metadata.tables))"` → 5 tables · vérif `changer_statut` → OK / ValueError · `./venv/bin/python -m pytest tests/ -q` → **14 passed**
- **Résultat** : 5 tables (`users, categories, products, orders, order_items`) · `en_attente→validée` OK · `validée→livrée` → ValueError (interdite)
- **Tests exécutés** : `pytest` → **14 passed** (🥉 1 + 🥈 13) — régression OK
- **Nouveaux tests 🥇** : aucun (prévus tâche 6 : `test_transition_autorisee/interdite`)
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 1 cochée `[x]`, commits `e0c0b59` (code) + `765393e` (backlog)

### ✅ Tâche 2 — `app/utils.py` (`calculer_total`, `verifier_stock`)
- **Fichiers** : `app/utils.py` (créé)
- **Commandes** : `./venv/bin/python -c "from app.utils import calculer_total, verifier_stock; ..."` → total=25.0, stock True/False, qte 0 → ValueError · `./venv/bin/python -m pytest tests/ -q` → **14 passed**
- **Résultat** : `calculer_total` = 25.0 (2×10 + 1×5) · `verifier_stock` qte 2 → True, qte 9 → False, qte 0 → ValueError
- **Tests exécutés** : `pytest` → **14 passed** (🥉 1 + 🥈 13) — régression OK
- **Nouveaux tests 🥇** : aucun (prévus tâche 6 : `test_calculer_total`, `test_verifier_stock_*`)
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 2 cochée `[x]`, commit `b06d4fe`

### ✅ Tâche 3 — `routes/commandes.py` (POST/GET/PATCH + règle 403 client_propriétaire)
- **Fichiers** : `app/routes/commandes.py` (créé), `app/app.py` (blueprint enregistré)
- **Commandes** : smoke test `./venv/bin/python` (script inline `app.test_client()` : login admin/client, POST catégorie+produit, POST commande, GET liste/détail, PATCH statut, → 201/400/401/403/404 OK, stock 5→3→5 · `./venv/bin/python -m pytest tests/ -q` → **14 passed**
- **Résultat** : POST 201 (total 20.0, en_attente) · 400 stock insuffisant/qte 0 · 401 sans token · GET liste 200 · autre client 403 · admin 200 · inconnu 404 · PATCH validée 200 (stock 5→3) · transition interdite 400 · client non-proprio 403 · client proprio annule 200 (stock restitué 5)
- **Tests exécutés** : `pytest` → **14 passed** (🥉 1 + 🥈 13) — régression OK
- **Nouveaux tests 🥇** : aucun (prévus tâche 6)
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 3 cochée `[x]`, commits `06cfa6e` + `a31b8fb`

### ✅ Tâche 4 — Gestionnaire d'erreurs global (4.10)
- **Fichiers** : `app/app.py` (`@app.errorhandler(404/405/500)` en JSON)
- **Commandes** : `./venv/bin/python -c "...test_client..."` → GET `/api/inexistant` = **404 JSON** · DELETE `/api/auth/login` = **405 JSON** · `./venv/bin/python -m pytest tests/ -q` → **14 passed**
- **Résultat** : 404 `{"error": "ressource introuvable"}` · 405 `{"error": "méthode non autorisée"}` · 500 handler posé
- **Tests exécutés** : `pytest` → **14 passed** (🥉 1 + 🥈 13) — régression OK
- **Nouveaux tests 🥇** : aucun (prévus tâche 6)
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 4 cochée `[x]`, commit `b9958c3`

### ✅ Tâche 5 — `conftest.py` (branche `commandes_module`)
- **Fichiers** : `tests/conftest.py` (import `cmd_module` + `cmd_module.session = S`)
- **Commandes** : `./venv/bin/python -m pytest tests/ -q` → **14 passed**
- **Résultat** : la session de test est branchée dans auth.py, produits.py **et commandes.py** → les tests 🥇 n'écriront pas dans `digimarket.db`
- **Tests exécutés** : `pytest` → **14 passed** (🥉 1 + 🥈 13) — régression OK
- **Nouveaux tests 🥇** : aucun (tâche 6)
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 5 cochée `[x]`, commit `08f08a8`

### ✅ Tâche 6 — `tests/test_commandes.py` (tests 🥇 + régression)
- **Fichiers** : `tests/test_commandes.py` (créé, 14 tests F3) · fix `tests/conftest.py` (`cmd_module.session = S`)
- **Commandes** : `./venv/bin/python -m pytest tests/ -q` → **32 passed**
- **Résultat** : unitaires 4.6/4.9 (transitions, calculer_total, verifier_stock) + intégration POST 201/400/401, GET 200/403/404, PATCH 200/400/403 + stock 5→3→5 — tout vert
- **Tests exécutés** : `pytest` → **32 passed** (🥉 1 + 🥈 13 + 🥇 18) — régression complète OK
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 6 cochée `[x]`, commits `0594f03` (tests) + `a947a13` (fix conftest)

### ✅ Tâche 7 — Données de démo (indépendant des tests)
- **Fichiers** : `app/app.py` (`init_sample_data` : + client `client@digimarket.fr` + 1 `Order`/`OrderItem` en_attente)
- **Commandes** : script inline (base en mémoire, `init_sample_data()`) → users = [admin, client] · commande id=1 en_attente total=899.99 · `./venv/bin/python -m pytest tests/ -q` → **32 passed**
- **Résultat** : au lancement (`python -m app.app`), la vraie base contient le client de démo + sa commande exemple
- **Tests exécutés** : `pytest` → **32 passed** (🥉 1 + 🥈 13 + 🥇 18) — régression OK (démo indépendante des tests)
- **Cohérence des commentaires explicatifs du code** : vérifiée ✅
- **Backlog** : tâche 7 cochée `[x]`, commit `2c2e749`

### ⬜ Tâche 8 — README + canva 🥇 + traçabilité
…

**DoD niveau 🥇** :
- [ ] code 🥇 fonctionnel (tout le CDC : étapes 1+2+3) ;
- [ ] `pytest` tout vert (unitaires + intégration + régression) ;
- [ ] README complet (livrable CDC) + canva 🥇 + matrice de traçabilité ;
- [ ] commits clairs · démo au lancement.

✅ **Niveau 🥇 terminé** quand tout est coché.
