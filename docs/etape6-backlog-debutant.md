# ÉTAPE 6 — NIVEAU 🥉 : BACKLOG (DigiMarket, fil rouge « S'inscrire »)

⏱️ variable (c'est le codage). Règle : chaque tâche est cochable et testable seule ; le code reste fonctionnel à chaque incrément.

| ✅ | # | Tâche | Depuis étape 4 🥉 | Fichier | Testable (preuve) |
|---|---|---|---|---|---|
| [x] | 1 | Squelette : requirements.txt + app.py + db.py + modelsSQLAlchemy.py (`Base` + `User`) | 4.1 base · 4.4 classe · 4.8 module/app | `requirements.txt`, `app/app.py`, `app/db.py`, `app/modelsSQLAlchemy.py` | `python -m app.app` démarre sans erreur ✅ |
| [x] | 2 | Route `POST /api/auth/register` (blueprint `auth_bp`, JSON 400/409/201) | cas « S'inscrire » (étape 1) → route 4.7 + erreurs 4.10 | `app/routes/auth.py` | POST register → 201, puis 409, puis 400 ✅ |
| [x] | 3 | Test `test_register_email_deja_utilise` | conçu à l'étape 5 🥉 (1 test unitaire, cas 409) | `tests/test_auth.py` | `pytest` → 1 passed ✅ |

**DoD niveau 🥉** :
- [x] code ✅ (3/3 tâches cochées)
- [x] test ✅ (`pytest` : 1 passed)
- [x] README ✅ (install/lancement à jour)
- [x] commit Git ✅ (messages clairs)

---

🧵 **Fil rouge** : « S'inscrire » → `POST /api/auth/register` fonctionnel + testé ✅

*Niveau 🥉 terminé. Niveau 🥈 (produits + sécurité JWT) : voir `etape6-backlog-intermediaire.md`.*
