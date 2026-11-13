# ÉTAPE 6 appliquée à DigiMarket — NIVEAU 🥈 INTERMÉDIAIRE (backlog AVANT le code)

**Règle** : on écrit et on valide CE backlog AVANT d'écrire la moindre ligne de code 🥈.
Chaque ligne = une tâche cochable, avec son **"testable"** (comment prouver que c'est fait).

## Backlog niveau 🥈 (F2 catalogue + F4 sécurité JWT + login F1)

| # | Tâche | Fichier(s) | Testable (preuve) |
|---|---|---|---|
| 1 | Modèles `Category` et `Product` (+ FK `category_id`, relation 1—N, 4.5) | `app/modelsSQLAlchemy.py` | `python -c "from app.modelsSQLAlchemy import Category, Product"` OK + `Base.metadata.create_all` crée les tables |
| 2 | Module sécurité : `creer_token`, `verifier_token`, `login_required`, `admin_required`, hachage (4.11) + `.env` (SECRET_KEY) + `PyJWT` dans `requirements.txt` | `app/security.py`, `.env`, `requirements.txt` | `pytest` → `test_token_invalide_401` passe |
| 3 | Route `POST /api/auth/login` (vérifie le hash, renvoie le token JWT) | `app/routes/auth.py` | `test_login_ok_renvoie_token` → 200 + token ; `test_login_mauvais_mot_de_passe_401` → 401 |
| 4 | Blueprint `produits_bp` : GET liste/recherche (public), GET détail, POST/PUT/DELETE (admin_required) + validations 4.3 (prix/stock >= 0) | `app/routes/produits.py` + enregistrement dans `app/app.py` | `test_creer_produit_admin_201`, `..._sans_token_401`, `..._client_403`, `..._prix_negatif_400`, `test_liste_produits_avec_recherche` |
| 5 | Route `POST /api/categories` (admin) pour créer une catégorie | `app/routes/produits.py` (ou `categories.py`) | `test_creer_categorie_admin_201`, `test_categorie_nom_unique_409`, `test_categorie_sans_token_401` |
| 6 | Tests 🥈 écrits (13 tests : F1 login, F2 produits/catégories, F4 tokens) | `tests/test_security.py`, `tests/test_produits.py` | `pytest` → tous les tests passent |
| 7 | Données de démo : 1 admin + 1 catégorie + 2 produits au lancement | `app/app.py` (`init_sample_data`) | `python -m app.app` → compte admin présent en base |
| 8 | README + canva 🥈 à jour (déjà faits en amont) | `README.md`, `docs/canva-structure-intermediaire.mmd` | relecture OK |

## Ordre d'exécution conseillé
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (modèles d'abord, sécurité ensuite, routes enfin, tests à chaque incrément).

## Definition of Done niveau 🥈
- [ ] code 🥈 fonctionnel (toutes les routes du contrat 4.7 répondent) ;
- [ ] `pytest` tout vert (🥉 + 🥈) ;
- [ ] README à jour, canva 🥈 à jour ;
- [ ] chaque commit a un message clair ;
- [ ] base recréée au lancement avec données de démo (admin + catalogue).

⚠️ **Point de vigilance CDC** : `POST /api/categories` n'est pas listé explicitement dans les routes du CDC mais la « gestion des catégories » est exigée dans le contexte → on le garde (admin uniquement).
