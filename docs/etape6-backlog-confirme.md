# ÉTAPE 6 — NIVEAU 🥇 : BACKLOG (à valider AVANT le code)

Règle : Avant la 1ʳᵉ ligne de code, on valide ce backlog 🥇 et, on reprend les résultats des livrables md de l'étape 4 et de l'étape 5. Le code 🥉/🥈 reste fonctionnel (on ajoute, on ne remplace pas). Chaque tâche a son « testable » = la preuve que c'est fait. On exécute la tâche suivante uniquement lorsque la tâche en cours est validée.

| ✅ | # | Tâches de code à réaliser | Source (étape · FM) | Dépend de | Fichier | Testable (preuve) |
|---|---|---|---|---|---|---|
| [ ] | 1 | Modèles `Order` + `OrderItem` (FK, relations 4.5, `STATUTS`/`TRANSITIONS`/`changer_statut` 4.6) | étape 4 🥇 §4.1/4.5/4.6 · **F3** | — | `app/modelsSQLAlchemy.py` | import OK + `create_all` crée orders/order_items + `test_transition_autorisee/interdite` |
| [ ] | 2 | Fonctions pures 4.9 : `calculer_total` (sur `Order`/`OrderItem`), `verifier_stock` (sur `Product`) | étape 4 🥇 §4.9 · **F3** | 1 | `app/utils.py` | `test_calculer_total`, `test_verifier_stock_*` passent |
| [ ] | 3 | Blueprint `routes/commandes.py` manipulant `Order`, `OrderItem`, `Product` : POST (vérif stock, lignes, total), GET liste/détail/lignes, PATCH statut + règle 403 client_propriétaire (4.11) ; transitions 4.6 ; stock décrémenté/restitué | étapes 4 🥇 §4.7/4.3/4.11 + 5 🥇 · **F3+F4** | 1, 3 | `app/routes/commandes.py`, `app/app.py` | 201/400/401/403/404 sur chaque route (tests d'intégration) |
| [ ] | 4 | Gestionnaire d'erreurs global 4.10 : `@app.errorhandler(404/405/500)` en JSON | étape 4 🥇 §4.10 · **global** | 4 | `app/app.py` | route inconnue → 404 JSON ; mauvaise méthode → 405 JSON |
| [ ] | 5 | `conftest.py` : brancher la session de test dans `routes/commandes.py` (`cmd_module.session = S`) — sinon les tests écrivent dans la vraie base | étape 5 🥇 · **F3** (infra tests) | 1 | `tests/conftest.py` | import de `app.routes.commandes` OK, session remplacée |
| [ ] | 6 | Les ~12 tests 🥇 écrits (`test_commandes.py`) + régression : tout `pytest` rejoué | étape 5 🥇 · **F3+F4** | 1, 3, 4, 5 | `tests/test_commandes.py` | `pytest` tout vert (14 + ~12) |
| [ ] | 7 | Données de démo 🥇 : 1 commande (`Order` + `OrderItem`) exemple pour le client de démo | étape 4 🥇 §4.7 · **F3** | 4 | `app/app.py` | `python -m app.app` → commande en base |
| [ ] | 8 | README + canva 🥇 à jour (sans écraser les précédents) + matrice de traçabilité CDC complète | étapes 4 🥇 §4.8 + 5 🥇 · **doc** | 6 | `README.md`, `docs/canva-structure-confirme.mmd` | relecture OK, traçabilité complète |

> 📝 §4.2 (panier) : donnée temporaire **côté client**, pas de table → rien à coder côté API.


**Ordre conseillé** : 1 → 2 → 3 → 4 → 5 (conftest) → 6 (tests) → 7 → 8 (tests à chaque incrément, régression à la fin).

**DoD niveau 🥇** :
- [ ] code 🥇 fonctionnel (tout le CDC : étapes 1+2+3) ;
- [ ] `pytest` tout vert (unitaires + intégration + régression) ;
- [ ] README complet (livrable CDC) + canva 🥇 + matrice de traçabilité ;
- [ ] commits clairs · démo au lancement.

✅ **Niveau 🥇 terminé** quand tout est coché.
