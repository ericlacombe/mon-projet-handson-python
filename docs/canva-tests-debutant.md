# 🧪 Descriptif du canva tests — NIVEAU 🥉 (`docs/canva-tests-debutant.mmd`)

Un seul fichier de test au niveau 🥉 (fil rouge « S'inscrire ») :

| Couleur | Fichier | Demande |
|---|---|---|
| 🔵 bleu | `test_auth.py` (F1 🥉 : `test_register_email_deja_utilise` → 409) | `client_http` (créé par conftest.py, lancé par pytest avant tout) |

Côté app : `client_http` → `app/app.py` → `routes/auth.py` → session de test (base en mémoire, jamais `digimarket.db`).
