# ÉTAPE 6 — NIVEAU 🥉 : BACKLOG (DigiMarket, fil rouge « S'inscrire »)

⏱️ variable (c'est le codage). Règle : Avant la 1ʳᵉ ligne de code, on valide ce backlog 🥉 et, on reprend les résultats des livrables md de l'étape 4 et de l'étape 5. Chaque tâche a son « testable » = la preuve que c'est fait. On exécute la tâche suivante uniquement lorsque la tâche en cours est validée.

**BACKLOG des tâches (à valider AVANT le code)**

| ✅ | # | Tâches de code à réaliser | Source (étape · FM) | Dépend de | Fichier | Testable (preuve) |
|---|---|---|---|---|---|---|
| [x] | 1 | Squelette : `requirements.txt` + `app.py` + `db.py` + `modelsSQLAlchemy.py` (`Base` + `User`) | étape 4 🥉 §4.1/4.4/4.8 · **F1** | — | `requirements.txt`, `app/app.py`, `app/db.py`, `app/modelsSQLAlchemy.py` | `python -m app.app` démarre sans erreur ✅ |
| [x] | 2 | Route `POST /api/auth/register` (blueprint `auth_bp`, JSON 400/409/201) | étape 1 (cas « S'inscrire ») + étape 4 🥉 §4.7/4.10 · **F1** | 1 | `app/routes/auth.py` | POST register → 201, puis 409, puis 400 ✅ |
| [x] | 3 | Test `test_register_email_deja_utilise` | étape 5 🥉 (1 test unitaire, cas 409) · **F1** | 1, 2 | `tests/test_auth.py` | `pytest` → 1 passed ✅ |

**Ordre conseillé** : 1 → 2 → 3 (tests à chaque incrément).

---

## 📊 Résultats d'exécution des tâches (template)

| Élément | Détail |
|---|---|
| Fichiers modifiés/créés | … |
| Commandes exécutées | `pytest tests/ -q`, vérif manuelle |
| Résultat | … |
| Tests exécutés | `pytest tests/ -q` → X passed = 🥉 (1 : `test_auth.py`) → OK |
| Nouveaux tests écrits | … |
| Backlog | tâche N cochée + commit poussé + résultat mis à jour ici + **cohérence des commentaires vérifiée** |

### ✅ Niveau 🥉 — résultat global
- **Commandes** : `./venv/bin/python -m pytest tests/test_auth.py -q` → **1 passed** · `python -m app.app` → démarre ✅
- **Résultat** : fil rouge « S'inscrire » fonctionnel + testé — 3/3 tâches cochées

---

**DoD niveau 🥉** (Definition of Done) :

- [x] **code ✅ (3/3 tâches cochées)** ;
  > *Vérifié par* : `python -m app.app` démarre + POST `/api/auth/register` → 201/409/400.
- [x] **test ✅ (`pytest` : 1 passed)** ;
  > *Vérifié par* : `./venv/bin/python -m pytest tests/ -q` → `1 passed` (`test_auth.py`).
- [x] **README ✅ (install/lancement à jour)** ;
- [x] **commit Git ✅ (messages clairs)** ;

---

🧵 **Fil rouge** : « S'inscrire » → `POST /api/auth/register` fonctionnel + testé ✅

🎉 **Niveau 🥉 terminé.** Niveau 🥈 (produits + sécurité JWT) : voir `etape6-backlog-intermediaire.md` · 🥇 : `etape6-backlog-confirme.md`.
