# ÉTAPE 6 — Backlog niveau 🥉 (DigiMarket, fil rouge « S'inscrire »)

⏱️ variable (c'est le codage)

**Règle** : chaque ligne du backlog est cochable et testable seule ; après chaque incrément le code reste fonctionnel. **Chaque ligne est commentée** (pourquoi elle est là — traçabilité avec les étapes 4/5).

## Backlog 🥉 (1 seul incrément)

- [x] **1. Squelette** : `requirements.txt` (flask, sqlalchemy, pytest), `app/app.py` (Flask + engine SQLite + session + `create_all` + `init_sample_data()` + enregistrement du blueprint + `app.run`), `app/db.py` (engine + session partagée), `app/modelsSQLAlchemy.py` (`Base` + classe `User`, table `users`)
      → **pourquoi :** vient de l'étape 4 — 4.1 (base), 4.4 (classe), 4.8 (module/app) ; l'arborescence du README.
      → **testable :** `python app/app.py` démarre sans erreur ✅ (vérifié)
- [x] **2. Route** `POST /api/auth/register` dans `app/routes/auth.py` (blueprint `auth_bp`, réponses 400/409/201 en JSON)
      → **pourquoi :** cas « S'inscrire » (étape 1, acteur Visiteur) → route 4.7 + erreurs 4.10 (409 email déjà pris prévu à l'étape 4).
      → **testable :** POST register renvoie `201` ✅ (vérifié : 201 puis 409 puis 400)
- [x] **3. Test** `test_register_email_deja_utilise` dans `app/tests/test_auth.py`
      → **pourquoi :** conçu à l'étape 5 (niveau 🥉 = 1 test unitaire) ; vérifie le cas d'erreur 409 de la route (étape 4).
      → **testable :** `pytest` → 1 test OK ✅ (vérifié : 1 passed)

## Definition of Done du niveau 🥉

- [x] code ✅ (les 3 lignes du backlog cochées)
- [x] test ✅ (`pytest` passe : 1 passed)
- [x] README ✅ (install/lancement à jour)
- [x] commit Git ✅ (messages clairs)

---

🧵 **Fil rouge** : « S'inscrire » → `POST /api/auth/register` fonctionnel + testé ✅

*Niveau 🥉 terminé. Prochaine étape (avec validation) : niveau 🥈 (produits + sécurité JWT).*
