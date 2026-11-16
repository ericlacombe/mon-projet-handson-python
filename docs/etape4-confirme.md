# ÉTAPE 4 appliquée à DigiMarket — NIVEAU 🥇 CONFIRMÉ (conception AVANT code)

**Niveau 🥇 = niveau 🥈 + partie 4.6 (transitions d'état) + F3 « Gérer les commandes »** (CDC étape 3).
Le code 🥉/🥈 reste fonctionnel : on AJOUTE, on ne remplace pas.

## 📋 Tableau récap — ce qu'on crée au niveau 🥇

| Fonction métier | Objet(s) | Routes (contrat 4.7) | Fichiers |
|---|---|---|---|
| **F3** Gérer les commandes | `Order`, `OrderItem` (nouveaux ; Order 1—N OrderItem, OrderItem N—1 Product, Order N—1 User) | `POST /api/commandes`, `GET /api/commandes`, `GET /api/commandes/<id>`, `GET /api/commandes/<id>/lignes`, `PATCH /api/commandes/<id>/statut` (admin) | `app/routes/commandes.py` (nouveau), `modelsSQLAlchemy.py` (+ Order, OrderItem) |

> F1/F2/F4 déjà faits au 🥈 ✅. Au 🥇 on touche à tout le CDC (étapes 1+2+3).

## 4.1 — Base de données (vérification niveau 🥇)

Rien de nouveau à créer : les 5 tables sont déclarées dans `modelsSQLAlchemy.py`
(`users, categories, products, orders, order_items`) et `Base.metadata.create_all`
les crée au lancement. 🥇 = **vérifier** au démarrage :

```python
assert set(Base.metadata.tables) == {"users", "categories", "products", "orders", "order_items"}
```

## 4.3 — Contraintes métier (ajouts 🥇)

| Fonction métier | Objet(s) | Règle | Où | Erreur |
|---|---|---|---|---|
| **F3** | `OrderItem` | `quantite > 0` | route POST | 400 |
| **F3** | `Product` | stock suffisant à la commande | route POST (vérif avant création) | 400 |
| **F3** | `Product` | stock décrémenté à la validation ; restitué à l'annulation | méthodes Order + route PATCH | — |
| **F3** | `Order.statut` | transition autorisée (4.6) | `Order.changer_statut` | 400 |

## 4.5 — Relations (ajouts 🥇)

| Fonction métier | Objet(s) | Relation | Clé étrangère | relationship |
|---|---|---|---|---|
| **F3** | `Order` ↔ `OrderItem` | 1—N | `order_items.order_id → orders.id` | `Order.items`, `OrderItem.order` |
| **F3** | `OrderItem` ↔ `Product` | N—1 | `order_items.product_id → products.id` | `OrderItem.product` |
| **F3** | `Order` ↔ `User` | N—1 | `orders.user_id → users.id` | `User.orders`, `Order.user` |

## 4.6 — Création des objets ayant une transition d'état (Order)

`Order.statut` : `en_attente` → `validée` → `expédiée` ; `annulée` possible depuis `en_attente`/`validée`.

| Fonction métier | Objet | Transition | Méthode sur la classe | Contrôle |
|---|---|---|---|---|
| **F3** | `Order` | en_attente → validée | `Order.valider()` | admin uniquement (route PATCH) + stock suffisant → décrément |
| **F3** | `Order` | validée → expédiée | `Order.expedier()` | admin uniquement |
| **F3** | `Order` | en_attente/validée → annulée | `Order.annuler()` | admin ou propriétaire + RESTITUTION du stock |

> 💡 **Rappel 4.5 appliqué à `Order`** (voir `etape4-intermediaire.md` §4.5 pour le détail) :
> - **Côté "1"** (dans `Order`) : `items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")`
>   → une commande a plusieurs lignes (`order.items`) ; supprimer la commande supprime ses lignes.
> - **Côté "N"** (dans `OrderItem`) : la **clé étrangère** `order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)`
>   → une ligne appartient obligatoirement à UNE commande (`ligne.order` grâce au backref).
>
> ```python
> # côté "1" dans Order      : items = relationship("OrderItem", backref="order", ...)
> # côté "N" dans OrderItem  : order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
> ```

```python
class Order(Base):
    # 4.6 — Cycle de vie d'une commande (états + transitions autorisées).
    # STATUTS : tous les états possibles (constantes nommées, pas de "magic strings").
    STATUTS = ("en_attente", "validée", "expédiée", "annulée")
    # TRANSITIONS : pour chaque état, la liste des états suivants AUTORISÉS.
    #   en_attente → validée (l'admin valide, le stock est décrémenté)
    #              → annulée (restitution du stock)
    #   validée    → expédiée | annulée
    #   expédiée/annulée → AUCUNE (états finaux : on ne revient jamais en arrière)
    TRANSITIONS = {"en_attente": ["validée", "annulée"], "validée": ["expédiée", "annulée"],
                   "expédiée": [], "annulée": []}

    def changer_statut(self, nouveau):
        # 4.6 : UNE méthode par objet avec cycle de vie, qui CONTRÔLE la transition :
        # si le passage statut → nouveau n'est pas dans TRANSITIONS, on refuse
        # (ValueError → la route renvoie 400 "transition interdite").
        if nouveau not in self.TRANSITIONS[self.statut]:
            raise ValueError(f"transition {self.statut} → {nouveau} interdite")
        self.statut = nouveau
        # C'est AUSSI ici qu'on branche les effets de bord (4.3) :
        #   validée → décrémenter le stock des produits (verifier_stock + update)
        #   annulée → restituer le stock
```

## 4.7 — Contrat d'API niveau 🥇 (routes commandes, CDC étape 3)

| Fonction métier | Objet(s) | Méthode | Route | Accès | Entrée (JSON) | Sorties / codes |
|---|---|---|---|---|---|---|
| **F3** | `Order` créé | POST | `/api/commandes` | Client connecté (`@login_required`) | `{adresse_livraison, items: [{product_id, quantite}]}` | `201` · `400` (stock insuffisant, qté ≤ 0) · `401` |
| **F3** | `Order` lus | GET | `/api/commandes` | Client = ses commandes ; admin = toutes | — | `200` · `401` |
| **F3** | `Order` lu | GET | `/api/commandes/<id>` | propriétaire ou admin | — | `200` · `403` · `404` |
| **F3** | `OrderItem` lus | GET | `/api/commandes/<id>/lignes` | propriétaire ou admin | — | `200` · `403` · `404` |
| **F3+F4** | `Order.statut` modifié | PATCH | `/api/commandes/<id>/statut` | **Admin** | `{statut: "validée"}` | `200` · `400` (transition interdite) · `401`/`403` · `404` |

## 4.9 — Fonctions Python (transformations sans état)

| Fonction | Rôle | Fichier |
|---|---|---|
| `calculer_total(commande)` | somme `quantite * prix_unitaire` des lignes | `app/routes/commandes.py` (ou `app/utils.py`) |
| `verifier_stock(items)` | vérifie la dispo de chaque produit | idem |

## 4.10 — Gestion des erreurs (niveau 🥇 : gestionnaire global + nouveaux codes F3)

Au 🥈 : try/except par route (500) + codes 400/401/403/404/409. Au 🥇 on ajoute un **gestionnaire global** (réponse JSON uniforme pour toute l'app) :

```python
@app.errorhandler(404)
def not_found(e):  return jsonify({"error": "introuvable"}), 404
@app.errorhandler(405)
def method_not_allowed(e):  return jsonify({"error": "méthode non autorisée"}), 405
@app.errorhandler(500)
def server_error(e):  return jsonify({"error": "erreur serveur"}), 500
```

| Fonction métier | Objet(s) | Erreur 🥇 | Code | Où |
|---|---|---|---|---|
| **F3** | `OrderItem` | quantité ≤ 0 | 400 | route POST /api/commandes |
| **F3** | `Product` | stock insuffisant | 400 | route POST /api/commandes |
| **F3** | `Order` | transition interdite (4.6) | 400 | `Order.changer_statut` → route PATCH |
| **F3+F4** | `Order` | non propriétaire, non admin | 403 | routes GET /api/commandes/<id>… |

## 4.11 — Sécurité étendue au niveau 🥇 (chaîne de protection complétée)

```
 → 0. BASE      : role stocké ('client' par défaut, 'admin' = démo uniquement), mdp haché PBKDF2+sel
 → 1. REGISTER    : rôle forcé "client" côté serveur
 → 2. DÉMO       : seul compte admin, mdp haché
 → 3. LOGIN       : token JWT SIGNÉ (HMAC-SHA256, pas chiffré, rôle embarqué, exp 24 h)
 → 4. ROUTES      : 401 si signature invalide/expiré · 403 si rôle insuffisant
      + 🥇 NOUVEAU : 403 si client NON PROPRIÉTAIRE sur /api/commandes/<id>
        (règle « propriétaire ou admin » : commande.user_id == user_id du token, ou role == admin)
 → 5. .env+HTTPS  : SECRET_KEY hors git, réseau chiffré en prod
```

| Fonction métier | Objet | Protection 🥇 | Fichier |
|---|---|---|---|
| **F3+F4** | `Order` | propriétaire ou admin → sinon **403** | `app/routes/commandes.py`, `app/security.py` |

## Backlog 🥇 (sera détaillé dans etape6-backlog-confirme.md)

1. Modèles `Order` + `OrderItem` (+ FK, relations, `changer_statut`) ;
2. Routes `commandes.py` : POST (vérif stock, lignes, total), GET liste/détail/lignes (propriétaire ou admin), PATCH statut (admin, transition + stock) ;
3. Tests 🥇 : unitaires (transitions, total) + intégration (création 201, stock insuffisant 400, 403 non propriétaire, PATCH admin 200, transition interdite 400) + **régression** (tout rejoué) ;
4. README + canva 🥇 (`canva-structure-confirme.mmd`, sans écraser les autres) + matrice de traçabilité CDC complète.

✅ **Checklist 🥇** : 4.5 N—N ✅ · 4.6 transitions ✅ · 4.7 contrat commandes ✅ · 4.3 contraintes ✅ · 4.9 fonctions ✅ · 4.10 erreurs (400/401/403/404) ✅ · 4.11 sécurité étendue (propriétaire-or-admin) ✅ · tests unitaires+intégration+régression ✅.

*Prochaine étape (avec validation) : étape 5 niveau 🥇 (matrice de tests complète) puis étape 6 (backlog 🥇) puis CODE.*
