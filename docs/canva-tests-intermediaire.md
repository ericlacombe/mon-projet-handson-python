# 🧪 Descriptif du canva tests — NIVEAU 🥈 (`docs/canva-tests-intermediaire.mmd`)

`conftest.py` (chargé par pytest avant tout) fournit : `session_test` (base en mémoire, session branchée dans auth.py/produits.py), `client_http` (test_client = curl simulé), `token_admin`, `token_client`.

| Couleur | Fichier (niveau 🥈) | Demande |
|---|---|---|
| 🟣 violet | `test_security.py` (F1 login + F4 tokens 401) | client_http + session_test + token_admin |
| 🟢 vert | `test_produits.py` (F2 CRUD 201/400/401/403/409) | client_http + session_test + token_admin + token_client (403) |

(Le test 🥉 `test_auth.py` est retiré de ce canva — voir `docs/canva-tests-debutant.mmd`.)
Côté app : `client_http` → `app/app.py` → routes → `security.py` (Bearer). Tests isolés : jamais `digimarket.db`.
