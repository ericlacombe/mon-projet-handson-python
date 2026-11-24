# 🎬 Démo pas à pas dans VS Code (2 terminaux) — DigiMarket (API REST Flask)

## 🟢 ÉTAPE 1 — Préparation (dans un terminal VS Code, à la racine du projet)
Dans VS Code : Terminal → New Terminal (ou Ctrl+Shift+`), puis :
```bash
cd /home/blent/mon-projet-handson-python
python3 -m venv venv
source venv/bin/activate
# Tu dois voir (venv) apparaître au début de ta ligne de commande.

pip install -r requirements.txt
# Crée le fichier .env (clé secrète pour signer les tokens JWT) :
echo 'SECRET_KEY=ma-cle-secrete-de-demo-123456' > .env
```

## 🟢 ÉTAPE 2 — Même terminal (TERMINAL 1) : lancer le serveur Flask
Le venv est déjà activé (étape 1), il suffit de lancer :
```bash
python -m app.app
```
✅ Tu dois voir apparaître :
```
 * Running on http://127.0.0.1:5000
Données de démo initialisées (admin + client + catalogue + 1 commande).
```
Laisse ce terminal ouvert — c'est le serveur qui tourne.

⚠️ **Erreur « Address already in use / Port 5000 is in use »** (un ancien serveur tourne encore). Sans toucher au code, lance sur un autre port (ex. 5001) et adapte les URL des curl en `:5001` :
```bash
python -c "from app.app import app; app.run(debug=True, port=5001)"   # serveur sur http://127.0.0.1:5001
# ex. : curl http://127.0.0.1:5001/api/produits
```
(Alternative pour tuer l'ancien processus si `fuser`/`lsof` manquent : `ss -ltnp | grep 5000` puis `kill <PID>`.)

## Données de démo créées automatiquement au lancement (`init_sample_data()`)

- **Comptes** : admin@digimarket.fr / admin123 (rôle admin) · client@digimarket.fr / client123 (rôle client)
- **Catalogue** : 1 catégorie « Informatique » + 2 produits (PC portable 899,99 € stock 10 · Clavier mécanique 79,90 € stock 25)
- **1 commande exemple** pour le client de démo : 1 × PC portable (id=1), total **899,99 €**, adresse « 12 rue des Lilas, Paris », statut **en_attente**

| Rôle | Email | Mot de passe |
|---|---|---|
| Admin | admin@digimarket.fr | admin123 |
| Client | client@digimarket.fr | client123 |

## 🔵 ÉTAPE 3 — TERMINAL 2 : envoyer les requêtes HTTP
Dans VS Code : Terminal → New Terminal (un 2ᵉ terminal s'ouvre à côté), puis :
```bash
cd /home/blent/mon-projet-handson-python && source venv/bin/activate
```
💡 `curl` = **cURL** (« Client URL ») : outil en ligne de commande pour transférer des données via HTTP (ici, appeler notre API). Anatomie d'une commande `curl` ci-dessous : `curl -X <MÉTHODE> <URL> -H "<header>" -d '<body JSON>'` — `-X` = méthode HTTP (GET par défaut, donc omis ici), `-H` = header (ex. `Authorization: Bearer <token>` pour les routes protégées, `Content-Type: application/json`), `-d` = corps JSON envoyé. Chaque requête tape l'API du serveur du terminal 1 (http://127.0.0.1:5000) et renvoie le JSON de réponse + le code HTTP.

**3.1 — Tester une route publique (catalogue)**
```bash
curl http://127.0.0.1:5000/api/produits
```
💡 `curl` fait un **GET par défaut** (pas besoin de `-X GET` : `curl -X GET "..."` marche pareil). `-X POST/PUT/PATCH/DELETE` sert uniquement à changer la méthode par défaut.
**3.2 — Rechercher un produit**
```bash
curl "http://127.0.0.1:5000/api/produits?q=clavier"
```
**3.3 — Détail d'un produit**
```bash
curl http://127.0.0.1:5000/api/produits/1
```
**3.4 — Se connecter en ADMIN et récupérer le token JWT**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@digimarket.fr","password":"admin123"}'
```
📋 Copie le token dans la réponse (le texte après `"token": "..."`).

**3.5 — Créer un produit (admin only, avec le token)** — remplace `COLLE_TON_TOKEN_ICI` :
```bash
curl -X POST http://127.0.0.1:5000/api/produits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer COLLE_TON_TOKEN_ICI" \
  -d '{"name":"Souris sans fil","description":"Silencieuse","price":29.99,"stock":50,"category_id":1}'
```
✅ Réponse attendue (201) :
```json
{"id": 4, "message": "produit créé"}
```
💡 Si tu rejoues la même commande, un **2ᵉ produit** est créé :
```json
{"id": 5, "message": "produit créé"}
```
→ Produit id 5 créé (le nom n'est pas unique, donc le doublon est accepté — seule la catégorie a un nom unique, 409).

**3.6 — ✏️ Modifier le prix du produit id 4 (admin)** — remplace `COLLE_TON_TOKEN_ICI` :
```bash
curl -X PUT http://127.0.0.1:5000/api/produits/4 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer COLLE_TON_TOKEN_ICI" \
  -d '{"price":299.99,"stock":20}'
```
✅ Réponse attendue (200) :
```json
{"id": 4, "message": "produit modifié"}
```

**3.7 — 🗑️ Supprimer le produit id 5 (admin)**
```bash
curl -X DELETE http://127.0.0.1:5000/api/produits/5 \
  -H "Authorization: Bearer COLLE_TON_TOKEN_ICI"
```
✅ 1ʳᵉ fois : **204** (corps vide). Si tu la rejoues : `{"error": "produit introuvable"}` (**404**, il n'existe plus).
Vérif : `curl http://127.0.0.1:5000/api/produits` → l'id 5 n'apparaît plus dans la liste.

**3.8 — ❌ Tester la sécurité : requête SANS token (doit renvoyer 401)**
```bash
curl -X POST http://127.0.0.1:5000/api/produits \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","price":10,"stock":1,"category_id":1}'
```
✅ Réponse attendue (401) :
```json
{"error": "token requis ou invalide"}
```
→ 401 : sans token, l'API refuse l'accès (sécurité OK ✅).

**3.9 — 🔐 Se connecter en CLIENT et stocker son token dans une variable**
```bash
# TOKEN_CLIENT=$(...)  : exécute la commande entre $( ) et stocke le résultat dans la variable TOKEN_CLIENT
# curl -s -X POST ...  : appelle le login (réponse JSON {"token": "eyJ..."}) — -s = silencieux (pas de barre de progression)
# | python3 -c "..."    : pipe (|) → envoie la réponse JSON dans ce mini-script Python qui extrait le token :
#     import sys,json            : importe sys (entrée standard) et json (parse le JSON)
#     json.load(sys.stdin)       : lit la réponse JSON reçue sur l'entrée standard (le pipe)
#     ['token']                  : récupère la valeur de la clé "token"
#     print(...)                 : l'affiche → c'est ce que contiendra la variable TOKEN_CLIENT
TOKEN_CLIENT=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@digimarket.fr","password":"client123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Ensuite, dans les étapes suivantes, utilise la variable dans le header :
#   -H "Authorization: Bearer $TOKEN_CLIENT"
```
**3.10 — Passer une commande (client, avec son token `$TOKEN_CLIENT`)** :
```bash
curl -X POST http://127.0.0.1:5000/api/commandes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_CLIENT" \
  -d '{"address_livraison":"12 rue des Lilas, Paris","items":[{"product_id":2,"quantite":2}]}'
```
✅ Réponse attendue (201) :
```json
{
  "address_livraison": "12 rue des Lilas, Paris",
  "date_creation": "2026-11-24T11:36:56.485580",
  "id": 3,
  "lignes": [
    {
      "prix_unitaire": 79.9,
      "product_id": 2,
      "quantite": 2
    }
  ],
  "statut": "en_attente",
  "total": 159.8,
  "user_id": 2
}
```
**3.11 — Voir son historique de commandes**
```bash
curl http://127.0.0.1:5000/api/commandes \
  -H "Authorization: Bearer $TOKEN_CLIENT"
```
**3.12 — 🔄 Annuler la commande id 3 (PATCH statut)**
```bash
curl -X PATCH http://127.0.0.1:5000/api/commandes/3/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_CLIENT" \
  -d '{"statut":"annulée"}'
```
✅ Réponse attendue (200) — la commande passe à `annulée` :
```json
{
  "address_livraison": "12 rue des Lilas, Paris",
  "id": 3,
  "lignes": [{"prix_unitaire": 79.9, "product_id": 2, "quantite": 2}],
  "statut": "annulée",
  "total": 159.8,
  "user_id": 2
}
```
✅ Commande 3 annulée — le stock du clavier a dû être **restitué**. Vérifions :
```bash
curl http://127.0.0.1:5000/api/produits/2
```
✅ Le stock doit être remonté à **27** (25 + 2 restitués) :
```json
{"categorie": "Informatique", "description": "Switchs silencieux", "id": 2,
 "name": "Clavier mécanique", "price": 79.9, "stock": 27}
```
→ Stock restitué : 25 → 27 après annulation. La mécanique de stock fonctionne ✅.
**3.13 — ❌ Tester le 401 sur les commandes (sans token)**
```bash
curl -X POST http://127.0.0.1:5000/api/commandes \
  -H "Content-Type: application/json" \
  -d '{"address_livraison":"test","items":[{"product_id":1,"quantite":1}]}'
```
✅ Réponse attendue (401) :
```json
{"error": "token requis ou invalide"}
```
→ 401 OK : sans token, l'API refuse l'accès.

**3.14 — ❌ Tester le 403 (un CLIENT essaie de créer un produit → réservé admin)**
```bash
curl -X POST http://127.0.0.1:5000/api/produits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_CLIENT" \
  -d '{"name":"Test client","price":10,"stock":1,"category_id":1}'
```
✅ Réponse attendue (403) :
```json
{"error": "réservé aux administrateurs"}
```
→ 403 OK : un client sur une route admin → « réservé aux administrateurs ».

**3.15 — 🛒 Créer une 2ᵉ commande (1 × PC portable id=1)** — `$TOKEN_CLIENT` encore en mémoire :
```bash
curl -X POST http://127.0.0.1:5000/api/commandes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_CLIENT" \
  -d '{"address_livraison":"12 rue des Lilas, Paris","items":[{"product_id":1,"quantite":1}]}'
```
✅ Réponse attendue (201) : commande `en_attente`, `total` = prix actuel du PC portable, `prix_unitaire` figé :
```json
{"id": 4, "statut": "en_attente", "total": 899.99,
 "lignes": [{"product_id": 1, "quantite": 1, "prix_unitaire": 899.99}], "user_id": 2, ...}
```

**3.16 — 🔐 Récupérer le token ADMIN dans une variable** (même pattern que `TOKEN_CLIENT`) :
```bash
TOKEN_ADMIN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@digimarket.fr","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

**3.17 — ✅ Admin passe la commande 4 en « validée »** (cycle : en_attente → validée → expédiée) :
```bash
curl -X PATCH http://127.0.0.1:5000/api/commandes/4/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{"statut":"validée"}'
```
✅ Réponse attendue (200) : `"statut": "validée"` (et le stock du PC portable est décrémenté).

**3.18 — ✅ Admin passe la commande 4 en « expédiée »**
```bash
curl -X PATCH http://127.0.0.1:5000/api/commandes/4/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{"statut":"expédiée"}'
```
✅ Réponse attendue (200) : `"statut": "expédiée"` → cycle complet en_attente → validée → expédiée ✅.

**3.19 — ❌ Transition INTERDITE (expédiée → en_attente) → 400**
```bash
curl -X PATCH http://127.0.0.1:5000/api/commandes/4/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{"statut":"en_attente"}'
```
✅ Réponse attendue (400) :
```json
{"error": "transition interdite : expédiée → en_attente"}
```

**3.20 — 📦 Vérifier le stock du PC portable (id 1) après validation**
```bash
curl http://127.0.0.1:5000/api/produits/1
```
✅ Le stock a été décrémenté à la validation (ex. 10 → 9) :
```json
{"id": 1, "name": "PC portable", "price": 899.99, "stock": 9, "categorie": "Informatique", ...}
```

**3.21 — ❌ Le CLIENT essaie de valider SA commande (en_attente → validée) → 403**
```bash
curl -X PATCH http://127.0.0.1:5000/api/commandes/4/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_CLIENT" \
  -d '{"statut":"validée"}'
```
✅ Réponse attendue (403) — seul l'admin peut valider :
```json
{"error": "un client ne peut qu'annuler sa commande"}
```

**3.22 — 👤 Créer un 2ᵉ client et récupérer son token**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"client2@exemple.fr","password":"mdp1234","first_name":"Jean","last_name":"Dupont"}'

TOKEN_CLIENT2=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client2@exemple.fr","password":"mdp1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo ${TOKEN_CLIENT2:0:30}    # vérif : affiche le début du token (eyJhbGciOiJIUzI1NiIs...)
```
✅ Réponse register (201) : `{"email": "client2@exemple.fr", "message": "utilisateur créé"}`.

**3.23 — ❌ client2 essaie de LIRE puis MODIFIER la commande d'un autre client → 403**
```bash
curl http://127.0.0.1:5000/api/commandes/4 -H "Authorization: Bearer $TOKEN_CLIENT2"

curl -X PATCH http://127.0.0.1:5000/api/commandes/4/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_CLIENT2" \
  -d '{"statut":"annulée"}'
```
✅ Réponse attendue (403) les 2 fois — règle client_propriétaire :
```json
{"error": "accès interdit à cette commande"}
```

**3.24 — ✅ L'ADMIN, lui, voit la commande 4 (il voit tout)**
```bash
curl http://127.0.0.1:5000/api/commandes/4 -H "Authorization: Bearer $TOKEN_ADMIN"
```
✅ Réponse attendue (200) : la commande complète (propriétaire `user_id: 2`).

## 🧪 ÉTAPE 4 — Lancer les tests automatisés (dans n'importe quel terminal, ex. Terminal 2)
```bash
cd /home/blent/mon-projet-handson-python && source venv/bin/activate
```
⚠️ Piège classique : `pytest` seul plante avec `ModuleNotFoundError: No module named 'app'` (pytest n'ajoute pas la racine au PYTHONPATH). Il faut lancer avec :
```bash
python -m pytest
```
✅ Tu dois voir la suite complète puis la dernière ligne :
```
tests/test_auth.py .                                       [  3%]
tests/test_commandes.py ..................                 [ 59%]
tests/test_produits.py .........                           [ 87%]
tests/test_security.py ....                                [100%]
======================= 32 passed in 7.01s =======================
```
🎉 **32 passed** — tous les tests passent !

## 📊 Récapitulatif de la session de démo

| Action | Résultat |
|---|---|
| 🟢 Serveur Flask | http://127.0.0.1:5000 ✅ |
| 📦 Liste catalogue (public) | 200 ✅ |
| 🔍 Recherche `?q=clavier` | 200 ✅ |
| 📦 Détail produit | 200 ✅ |
| 🔐 Login admin → JWT | 200 ✅ |
| 🔐 Login client → JWT | 200 ✅ |
| 📝 Register nouveau compte | 201 ✅ |
| ➕ Créer produit (admin) | 201 ✅ |
| ✏️ Modifier produit (admin) | 200 ✅ |
| 🗑️ Supprimer produit (admin) | 204 ✅ |
| ❌ Créer produit sans token | 401 ✅ |
| ❌ Créer produit avec token client | 403 ✅ |
| 🛒 Passer commande (client) | 201 ✅ |
| 📋 Historique commandes | 200 ✅ |
| 🔄 en_attente → validée (admin) | 200 ✅ |
| 🔄 validée → expédiée (admin) | 200 ✅ |
| ❌ expédiée → en_attente (interdit) | 400 ✅ |
| ❌ Client valide sa commande | 403 ✅ |
| 🔄 Annulation client → stock restitué | 200 ✅ |
| ❌ Client2 voit commande d'un autre | 403 ✅ |
| ❌ Client2 modifie commande d'un autre | 403 ✅ |
| ✅ Admin voit toutes les commandes | 200 ✅ |
| 🧪 Suite de tests automatisés | 32 passed ✅ |

🚀 Ton API DigiMarket est **fully opérationnelle** !
Pour arrêter le serveur : retourne dans le **Terminal 1** et fais **Ctrl+C**.

---

# 🧭 Rappel rapide (résumé des commandes essentielles)

📊 **Récapitulatif des 2 terminaux** — **Terminal 1 🟢** = serveur Flask (`python -m app.app`, écoute sur http://127.0.0.1:5000) · **Terminal 2 🔵** = requêtes HTTP (`curl ...` qui testent l'API). Donc : les étapes 3.x (tous les `curl`) se font dans le **Terminal 2 🔵**, le serveur tourne dans le **Terminal 1 🟢**, et les tests (étape 4, `python -m pytest`) peuvent se lancer dans l'un ou l'autre.

| Terminal | Rôle | Commande |
|---|---|---|
| Terminal 1 🟢 | Serveur Flask | `python -m app.app` → écoute sur http://127.0.0.1:5000 |
| Terminal 2 🔵 | Requêtes HTTP | `curl ...` → teste l'API |

## Installer et lancer (version courte) — dans le **Terminal 1 🟢** (celui du serveur)
```bash
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/python -m app.app          # serveur sur http://127.0.0.1:5000 — Terminal 1 🟢
```

## Se connecter (obtenir un token JWT, valable 24 h)
```bash
# curl = client HTTP en ligne de commande (ici contre notre API locale sur le port 5000)
# -X POST                          : méthode HTTP POST (envoi de données)
# http://127.0.0.1:5000/...        : 127.0.0.1 = la machine locale, 5000 = port de Flask
# -H "Content-Type: application/json" : on envoie du JSON (le serveur lit request.get_json())
# -d '{...}'                       : le corps de la requête = les identifiants de démo
curl -X POST http://127.0.0.1:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"client@digimarket.fr","password":"client123"}'
# → {"token": "eyJ..."}   : réponse 200, le token JWT signé (à mettre ensuite dans le header
#                          "Authorization: Bearer <token>" de toutes les requêtes protégées)
```

## Scénario « passer une commande » (fil rouge)
```bash
TOKEN="eyJ..."   # token du login

# catalogue (public)
curl http://127.0.0.1:5000/api/produits

# passer une commande : 2 x PC portable (id=1)
curl -X POST http://127.0.0.1:5000/api/commandes \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"address_livraison":"12 rue des Lilas, Paris","items":[{"product_id":1,"quantite":2}]}'
# → 201 {"id":2, "statut":"en_attente", "total":1799.98, "lignes":[...]}

# voir SES commandes (historique)
curl http://127.0.0.1:5000/api/commandes -H "Authorization: Bearer $TOKEN"

# détail + lignes d'une commande
curl http://127.0.0.1:5000/api/commandes/2 -H "Authorization: Bearer $TOKEN"
curl http://127.0.0.1:5000/api/commandes/2/lignes -H "Authorization: Bearer $TOKEN"
```

## Côté admin : valider la commande (stock décrémenté)
```bash
TOKEN_ADMIN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@digimarket.fr","password":"admin123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -X PATCH http://127.0.0.1:5000/api/commandes/2/statut \
     -H "Authorization: Bearer $TOKEN_ADMIN" -H "Content-Type: application/json" \
     -d '{"statut":"validée"}'     # → 200, statut=validée, stock PC portable 10 → 8

# le client peut annuler sa propre commande (stock restitué)
curl -X PATCH http://127.0.0.1:5000/api/commandes/2/statut \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"statut":"annulée"}'
```

## Montrer la sécurité (codes d'erreur)
| Cas | Requête | Résultat |
|---|---|---|
| Sans token | `POST /api/commandes` sans header | **401** |
| Client sur route admin | `POST /api/produits` avec token client | **403** |
| Autre client lit la commande d'un autre | `GET /api/commandes/2` avec un 2e token client | **403** (client_propriétaire) |
| Ressource inconnue | `GET /api/commandes/999` | **404** JSON |
| Transition interdite | PATCH `en_attente` → `livrée` | **400** (cycle de vie 4.6) |
| Stock insuffisant / quantité 0 | POST commande qté 99 ou 0 | **400** |

## Montrer les tests
```bash
./venv/bin/python -m pytest tests/ -q     # → 32 passed (🥉 1 + 🥈 13 + 🥇 18)
```
