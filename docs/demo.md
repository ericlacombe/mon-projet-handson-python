# 🎬 Guide de la démo — DigiMarket (API REST Flask)

## 1. Installer et lancer
```bash
cd mon-projet-handson-python
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
echo 'SECRET_KEY=ma_cle_secrete_32_caracteres_minimum' > .env   # si pas déjà fait
./venv/bin/python -m app.app          # serveur sur http://127.0.0.1:5000
```
Au lancement, `init_sample_data()` crée automatiquement :
- **admin@digimarket.fr / admin123** (rôle admin)
- **client@digimarket.fr / client123** (rôle client)
- 1 catégorie « Informatique », 2 produits (PC portable 899,99 € stock 10 · Clavier mécanique 79,90 € stock 25)
- 1 commande exemple (en_attente) pour le client de démo

## 2. Se connecter (obtenir un token JWT, valable 24 h)
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

## 3. Scénario « passer une commande » (fil rouge)
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

## 4. Côté admin : valider la commande (stock décrémenté)
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

## 5. Montrer la sécurité (codes d'erreur)
| Cas | Requête | Résultat |
|---|---|---|
| Sans token | `POST /api/commandes` sans header | **401** |
| Client sur route admin | `POST /api/produits` avec token client | **403** |
| Autre client lit la commande d'un autre | `GET /api/commandes/2` avec un 2e token client | **403** (client_propriétaire) |
| Ressource inconnue | `GET /api/commandes/999` | **404** JSON |
| Transition interdite | PATCH `en_attente` → `livrée` | **400** (cycle de vie 4.6) |
| Stock insuffisant / quantité 0 | POST commande qté 99 ou 0 | **400** |

## 6. Montrer les tests
```bash
./venv/bin/python -m pytest tests/ -q     # → 32 passed (🥉 1 + 🥈 13 + 🥇 18)
```
