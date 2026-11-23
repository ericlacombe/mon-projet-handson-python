# ÉTAPE 6 — NIVEAU 🥇 : BACKLOG (à valider AVANT le code)

Règle : Avant la 1ʳᵉ ligne de code, on valide ce backlog 🥇 et, on reprend les résultats des livrables md de l'étape 4 et de l'étape 5. Le code 🥉/🥈 reste fonctionnel (on ajoute, on ne remplace pas). Chaque tâche a son « testable » = la preuve que c'est fait. On exécute la tâche suivante uniquement lorsque la tâche en cours est validée.

| ✅ | # | Tâches de code à réaliser | Depuis étape 4 🥇 | Fichier | Testable (preuve) |
|---|---|---|---|---|---|
| [ ] | 1 | Modèles `Order` + `OrderItem` (FK, relations 4.5, `STATUTS`/`TRANSITIONS`/`changer_statut` 4.6) | objets F3 (4.5/4.6) | `app/modelsSQLAlchemy.py` | import OK + `create_all` crée orders/order_items + `test_transition_autorisee/interdite` |
| [ ] | 2 | Fonctions pures 4.9 : `calculer_total`, `verifier_stock` | 4.9 | `app/utils.py` | `test_calculer_total`, `test_verifier_stock_*` passent |
| [ ] | 3 | Blueprint `routes/commandes.py` : POST (vérif stock, lignes, total), GET liste/détail/lignes (client_propriétaire ou admin → 403), PATCH statut (admin ou client_propriétaire pour annulée ; transition 4.6 ; stock décrémenté/restitué) | contrat 4.7 + 4.3 + 4.11 étendue | `app/routes/commandes.py`, `app/app.py` | 201/400/401/403/404 sur chaque route (tests d'intégration) |
| [ ] | 4 | Gestionnaire d'erreurs global 4.10 : `@app.errorhandler(404/405/500)` en JSON | 4.10 🥇 | `app/app.py` | route inconnue → 404 JSON ; mauvaise méthode → 405 JSON |
| [ ] | 5 | Les ~12 tests 🥇 écrits (`test_commandes.py`) + régression : tout `pytest` rejoué | matrice étape 5 🥇 | `tests/test_commandes.py` | `pytest` tout vert (14 + ~12) |
| [ ] | 6 | Données de démo 🥇 : 1 commande exemple pour le client de démo | livrable CDC | `app/app.py` | `python -m app.app` → commande en base |
| [ ] | 7 | README + canva 🥇 à jour (sans écraser les précédents) + matrice de traçabilité CDC complète | 4.8 + étape 4 🥇 | `README.md`, `docs/canva-structure-confirme.mmd` | relecture OK, traçabilité complète |

**Ordre conseillé** : 1 → 2 → 3 → 4 → 5 → 6 → 7 (tests à chaque incrément, régression à la fin).

**DoD niveau 🥇** :
- [ ] code 🥇 fonctionnel (tout le CDC : étapes 1+2+3) ;
- [ ] `pytest` tout vert (unitaires + intégration + régression) ;
- [ ] README complet (livrable CDC) + canva 🥇 + matrice de traçabilité ;
- [ ] commits clairs · démo au lancement.

✅ **Niveau 🥇 terminé** quand tout est coché.
