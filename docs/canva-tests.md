# 🧪 Descriptif écrit de `docs/canva-tests.mmd` (schéma des interactions entre les tests)

## Rôle de `conftest.py`
pytest le charge **avant tous les fichiers de tests**. Il définit 4 fixtures communes :

- `session_test` — crée une base SQLite **en mémoire** (`sqlite:///:memory:`), y branche la session dans `routes/auth.py` et `routes/produits.py` (elle **remplace** celle de `db.py` liée à la vraie `digimarket.db`) ;
- `client_http` — `app.test_client()`, le « curl simulé » de Flask (appelle les routes sans serveur) ;
- `token_admin` / `token_client` — créent un compte en base de test, appellent `POST /api/auth/login`, renvoient le token JWT.

## Qui demande quoi (code couleur des flèches dans le canva)

| Couleur | Fichier de test | Demande |
|---|---|---|
| 🔵 bleu | `test_auth.py` (F1 🥉, 409) | → `client_http` |
| 🟣 violet | `test_security.py` (F1 login + F4 tokens 401) | → `client_http` + `session_test` + `token_admin` |
| 🟢 vert | `test_produits.py` (F2 CRUD 201/400/401/403/409) | → `client_http` + `session_test` + `token_admin` + `token_client` (pour tester le 403) |

## Côté app testé
`client_http` appelle `app/app.py`, qui dispatche vers `routes/auth.py` et `routes/produits.py` ; celles-ci utilisent la **session de test** (jamais la vraie base) et passent par `security.py` (`creer_token`/`verifier_token`/`admin_required`) — les tokens vont en header `Authorization: Bearer <token>`.

👉 **L'essentiel** : les tests sont isolés (base en mémoire, jetable à chaque test) et ne touchent **jamais** `digimarket.db`.
