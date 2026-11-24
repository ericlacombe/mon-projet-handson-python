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

## Données de démo créées automatiquement au lancement (`init_sample_data()`)

- **Comptes** : admin@digimarket.fr / admin123 (rôle admin) · client@digimarket.fr / client123 (rôle client)
- **Catalogue** : 1 catégorie « Informatique » + 2 produits (PC portable 899,99 € stock 10 · Clavier mécanique 79,90 € stock 25)
- **1 commande exemple** (en_attente) pour le client de démo

| Rôle | Email | Mot de passe |
|---|---|---|
| Admin | admin@digimarket.fr | admin123 |
| Client | client@digimarket.fr | client123 |

⚠️ **Erreur « Address already in use / Port 5000 is in use »** (un ancien serveur tourne encore). Sans toucher au code, lance sur un autre port (ex. 5001) et adapte les URL des curl en `:5001` :
```bash
python -c "from app.app import app; app.run(debug=True, port=5001)"   # serveur sur http://127.0.0.1:5001
# ex. : curl http://127.0.0.1:5001/api/produits
```
(Alternative pour tuer l'ancien processus si `fuser`/`lsof` manquent : `ss -ltnp | grep 5000` puis `kill <PID>`.)

## 🔵 ÉTAPE 3 — TERMINAL 2 : envoyer les requêtes HTTP
Dans VS Code : Terminal → New Terminal (un 2ᵉ terminal s'ouvre à côté), puis :
```bash
cd /home/blent/mon-projet-handson-python && source venv/bin/activate
```

**3.1 — Tester une route publique (catalogue)**
```bash
curl http://127.0.0.1:5000/api/produits
```
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
**3.6 — Se connecter en CLIENT**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@digimarket.fr","password":"client123"}'
```
**3.7 — Passer une commande (client, avec son token)** — remplace `COLLE_TON_TOKEN_CLIENT_ICI` :
```bash
curl -X POST http://127.0.0.1:5000/api/commandes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer COLLE_TON_TOKEN_CLIENT_ICI" \
  -d '{"address_livraison":"12 rue des Lilas, Paris","items":[{"product_id":2,"quantite":2}]}'
```
**3.8 — Voir son historique de commandes**
```bash
curl http://127.0.0.1:5000/api/commandes \
  -H "Authorization: Bearer COLLE_TON_TOKEN_CLIENT_ICI"
```
**3.9 — Annuler sa commande (PATCH statut)**
```bash
curl -X PATCH http://127.0.0.1:5000/api/commandes/1/statut \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer COLLE_TON_TOKEN_CLIENT_ICI" \
  -d '{"statut":"annulée"}'
```
**3.10 — Tester les erreurs (sans token → 401)**
```bash
curl -X POST http://127.0.0.1:5000/api/produits \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","price":10,"stock":1,"category_id":1}'
```

## 🧪 ÉTAPE 4 — Lancer les tests automatisés (dans n'importe quel terminal)
```bash
cd /home/blent/mon-projet-handson-python && source venv/bin/activate && pytest
# Tu dois voir : 32 passed.
```

## 📊 Récapitulatif des 2 terminaux

| Terminal | Rôle | Commande |
|---|---|---|
| Terminal 1 🟢 | Serveur Flask | `python -m app.app` → écoute sur http://127.0.0.1:5000 |
| Terminal 2 🔵 | Requêtes HTTP | `curl ...` → teste l'API |

---

# 🧭 Rappel rapide (résumé des commandes essentielles)

## Installer et lancer (version courte)
```bash
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/python -m app.app          # serveur sur http://127.0.0.1:5000
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
