# 📐 Vue UML complète du projet DigiMarket (API Flask)

Ce document regroupe **tous les diagrammes UML du projet**, organisés selon les **3 familles officielles de l'UML** (standard OMG) :

| Famille UML | Question répondue | Diagrammes ici |
|---|---|---|
| 🏗️ **Structure** | *De quoi le système est-il fait ?* (classes, composants, données) | classes, ER, composants/packages |
| ⚙️ **Comportement** | *Comment le système évolue-t-il / s'enchaîne-t-il ?* (cas d'utilisation, activités, états) | cas d'utilisation, activité, machine à états |
| 🔁 **Interaction** | *Qui échange quoi avec qui, et dans quel ordre ?* | séquence |

> 💡 **Pourquoi ce fichier est en `.md`** : GitHub rend automatiquement les blocs ` ```mermaid ` **uniquement dans les fichiers Markdown** (vue fichier, README, onglet « Files changed » d'une PR). Les canva `.mmd` du projet (`canva-*.mmd`) restent du texte brut sur GitHub → rendu via [mermaid.live](https://mermaid.live). Ce doc `.md` est donc la version « rendue nativement sur GitHub ».
>
> 📖 **Légende générale UML utilisée partout ici** : visibilité `+` = public ; `PK` = clé primaire, `FK` = clé étrangère, `UK` = unique ; multiplicités `1`, `*` (plusieurs), `1..*` ; `||--o{` = « un vers zéro-ou-plusieurs » (ER) ; dans une machine à états, `[*]` = état initial/final et `A --> B : événement` = transition déclenchée par l'événement.

---

## 🏗️ Famille 1 — STRUCTURE

### 1.1 Diagramme de classes (UML `classDiagram`) — les 5 modèles ORM

Vue logique orientée objet, fidèle à `app/modelsSQLAlchemy.py` (niveau 🥇). Même contenu que le canva `docs/canva-classes-confirme.mmd`.

```mermaid
%% LÉGENDE : classe = boîte à 3 compartiments (nom / attributs / méthodes)
%% + = public · PK/FK/UK = clés · "1" --> "*" = association UML avec multiplicités (1 côté, plusieurs de l'autre)
classDiagram
    class User {
        +Integer id PK
        +String email UK
        +String password_hash
        +String first_name
        +String last_name
        +Text address
        +String role = "client"
        +__repr__() string
    }
    class Category {
        +Integer id PK
        +String name UK
        +__repr__() string
    }
    class Product {
        +Integer id PK
        +String name
        +Text description
        +Float price
        +Integer stock = 0
        +Integer category_id FK
        +__repr__() string
    }
    class Order {
        +Integer id PK
        +Integer user_id FK
        +Text address_livraison
        +DateTime date_creation
        +String statut = "en_attente"
        +Float total = 0.0
        +changer_statut(nouveau: string) void
        +__repr__() string
    }
    class OrderItem {
        +Integer id PK
        +Integer order_id FK
        +Integer product_id FK
        +Integer quantite
        +Float prix_unitaire
        +__repr__() string
    }

    note for Order "STATUTS = en_attente, validée, expédiée, livrée, annulée<br/>TRANSITIONS : en_attente → validée ou annulée · validée → expédiée ou annulée · expédiée → livrée"

    User "1" --> "*" Order : passe >
    Category "1" --> "*" Product : contient >
    Order "1" --> "*" OrderItem : comporte >
    Product "1" --> "*" OrderItem : est référencé par >
```

**Légende** : chaque boîte = une classe (= une table en base). Le compartiment du milieu liste les attributs avec leur type UML/Python ; `PK`/`UK`/`FK` sont des stéréotypes informels posés en annotation. Les flèches sont des **associations UML** avec multiplicités : un `User` passe zéro-ou-plusieurs `Order`, etc. `Order.changer_statut()` est la méthode métier du cycle de vie (4.6).

### 1.2 Diagramme entité-association (`erDiagram`) — schéma physique de la base SQLite

Même modèle, vu « base de données » : tables réelles de `digimarket.db` (`__tablename__` dans le code).

```mermaid
%% LÉGENDE ER : ||--o{ = "un vers zéro-ou-plusieurs" · PK = primary key · FK = foreign key · UK = unique
erDiagram
    users ||--o{ orders : "passe"
    categories ||--o{ products : "contient"
    orders ||--o{ order_items : "comporte"
    products ||--o{ order_items : "est référencé par"

    users {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        text address
        string role "client | admin"
    }
    categories {
        int id PK
        string name UK
    }
    products {
        int id PK
        string name
        text description
        float price
        int stock
        int category_id FK
    }
    orders {
        int id PK
        int user_id FK
        text address_livraison
        string statut "en_attente | validée | expédiée | livrée | annulée"
        datetime date_creation
        float total
    }
    order_items {
        int id PK
        int order_id FK
        int product_id FK
        int quantite
        float prix_unitaire "prix figé à la commande"
    }
```

**Légende** : `users ||--o{ orders` se lit « un utilisateur possède zéro ou plusieurs commandes ». La version « objets métier » (noms français) existe dans `docs/etape3-objets.md` ; celle-ci colle aux vrais noms de tables SQL.

### 1.3 Diagramme de composants / packages — architecture du code

Vue « package UML » : chaque `subgraph` = un package (dossier), les flèches = dépendances (imports / appels).

```mermaid
%% LÉGENDE : subgraph = package UML (dossier) · flèche pleine = dépendance (import/appel) · en pointillés = données persistées
flowchart TB
    CLIENT["👤 Client externe<br/>curl / navigateur / Thunder Client"]

    subgraph PKG_APP["package app/ - code de l'API"]
        APP["app.py<br/>Flask : crée l'app, enregistre les blueprints,<br/>errorhandlers 404/405/500, app.run"]
        DB["db.py<br/>engine SQLite + session partagée"]
        SEC["security.py<br/>JWT HS256 24h, hachage, @login_required 401, @admin_required 403"]
        MODELS["modelsSQLAlchemy.py<br/>User · Category · Product · Order · OrderItem"]
        UTILS["utils.py<br/>calculer_total, verifier_stock - fonctions pures 4.9"]
        subgraph PKG_ROUTES["package app/routes/ - blueprints, un par fonction métier"]
            RAUTH["auth.py<br/>POST /api/auth/register · /login"]
            RPROD["produits.py<br/>CRUD /api/produits + POST /api/categories - admin"]
            RCMD["commandes.py<br/>POST/GET /api/commandes · PATCH /statut"]
        end
    end

    subgraph PKG_TESTS["package tests/ - pytest, 32 tests"]
        TESTS["conftest.py - fixtures, base en mémoire<br/>test_auth · test_security · test_produits · test_commandes"]
    end

    DBFILE[("digimarket.db<br/>SQLite, créé au lancement")]

    CLIENT -->|requête HTTP JSON| APP
    APP --> RAUTH & RPROD & RCMD
    RAUTH & RPROD & RCMD --> SEC
    RAUTH & RPROD & RCMD --> DB
    DB --> MODELS
    RCMD --> UTILS
    MODELS -.->|tables créées par create_all| DBFILE
    DB -.->|session| DBFILE
    TESTS -.->|importe| APP
```

**Légende** : le client HTTP ne parle qu'à `app.py` (point d'entrée unique) ; `app.py` dispatche vers les blueprints (`routes/*.py`, un par fonction métier F1–F4, exigé par le CDC) ; la sécurité (`security.py`) filtre les routes protégées (401/403) ; tout passe par la session partagée `db.py` pour éviter l'import circulaire ; les modèles ORM sont persistés dans `digimarket.db`. Les tests importent l'app mais utilisent une base en mémoire (jamais `digimarket.db`).

---

## ⚙️ Famille 2 — COMPORTEMENT

### 2.1 Cas d'utilisation (approximation `flowchart`)

> ⚠️ Mermaid ne possède pas de `useCaseDiagram` natif en version stable : on approxime ici le diagramme de cas d'utilisation UML par un flowchart (acteurs en sous-graphes, cas dans la frontière système). Pour un vrai diagramme UML de cas d'utilisation (bonhomme + ellipse), utiliser PlantUML. Acteurs et cas issus de `docs/etape1-use-cases.md`.

```mermaid
%% LÉGENDE : subgraph externe = acteur UML · subgraph interne = frontière du système (API DigiMarket) · nœud arrondi = cas d'utilisation
flowchart LR
    subgraph ACT_V["👤 Visiteur - non inscrit"]
        UC1(("S'inscrire"))
        UC2(("Se connecter"))
        UC3(("Consulter le catalogue"))
        UC4(("Rechercher un produit ?q="))
        UC5(("Voir le détail d'un produit"))
    end
    subgraph SYS["🖥️ Système : API DigiMarket - Flask"]
        UC6(("Passer une commande"))
        UC7(("Voir son historique"))
        UC8(("Voir détail + lignes d'une commande"))
        UC9(("Annuler sa commande"))
        UC10(("Créer / modifier / supprimer un produit"))
        UC11(("Créer une catégorie"))
        UC12(("Voir toutes les commandes"))
        UC13(("Changer le statut d'une commande"))
    end
    subgraph ACT_C["👤 Client - connecté, rôle client"]
        UC6
        UC7
        UC8
        UC9
    end
    subgraph ACT_A["👤 Administrateur - rôle admin"]
        UC10
        UC11
        UC12
        UC13
    end
    ACT_V --> UC1 & UC2 & UC3 & UC4 & UC5
```

**Légende** : en UML pur, chaque acteur serait un bonhomme relié par une ligne à des ellipses (cas) à l'intérieur d'un rectangle « système ». Ici : `Visiteur` peut consulter le catalogue sans compte ; `Client` commande et gère **ses** commandes (règle client_propriétaire, 403 sinon) ; `Admin` gère produits/stocks et **toutes** les commandes.

### 2.2 Diagramme d'activité — scénario « passer une commande » (couloirs)

```mermaid
%% LÉGENDE : subgraph horizontal = couloir (swimlane) d'un acteur · losange = décision UML · flèche étiquetée [garde] = transition avec condition · (400/401) = code HTTP renvoyé en cas d'échec
flowchart TB
    subgraph SW_C["👤 Client"]
        START([Début : le client veut commander])
        SEND["POST /api/commandes<br/>{address_livraison, items[]}<br/>+ header Authorization: Bearer token"]
        OK([Commande reçue : 201 + JSON commande])
    end
    subgraph SW_API["🖥️ API Flask - routes commandes.py + security.py"]
        TOK{Token JWT valide ?}
        BODY{address_livraison non vide<br/>et items non vide ?}
        ITEM{Produit existe et<br/>quantité > 0 et stock suffisant ?}
        CRE["Order en_attente + OrderItem, prix figé<br/>+ total = calculer_total<br/>session.commit]"
    end
    subgraph SW_DB["🗄️ Base SQLite - digimarket.db"]
        INS[(INSERT orders + order_items)]
    end

    START --> SEND
    SEND --> TOK
    TOK -- non --> E401([401 token requis ou invalide])
    TOK -- oui --> BODY
    BODY -- non --> E400a([400 address_livraison et items requis])
    BODY -- oui --> ITEM
    ITEM -- non --> E400b([400 produit inexistant / stock insuffisant / quantité ≤ 0])
    ITEM -- oui --> CRE
    CRE --> INS
    INS --> OK
```

**Légende** : trois couloirs (Client / API / Base). Toute branche « non » d'un losange se termine par une erreur HTTP en JSON `{"error": ...}` ; seule la branche « tout oui » persiste la commande (201). Le stock n'est **décrémenté** qu'à la validation (voir machine à états ci-dessous), pas à la création.

### 2.3 Machine à états (UML `stateDiagram-v2`) — cycle de vie de `Order.statut`

Fidèle à `Order.TRANSITIONS` dans `app/modelsSQLAlchemy.py` (4.6). Version aussi présente dans `docs/etape3-objets.md`.

```mermaid
%% LÉGENDE machine à états UML : [*] = état initial/final · A --> B : événement/déclencheur = PATCH /api/commandes/<id>/statut
%% Effets de bord : validée → stock décrémenté · annulée → stock restitué
stateDiagram-v2
    [*] --> en_attente : création - POST /api/commandes
    en_attente --> validée : PATCH statut admin, stock décrémenté
    en_attente --> annulée : PATCH statut client propriétaire ou admin, stock restitué
    validée --> expédiée : PATCH statut admin
    validée --> annulée : PATCH statut → stock restitué
    expédiée --> livrée : PATCH statut admin
    livrée --> [*]
    annulée --> [*]
```

**Légende** : `en_attente` est l'état initial (création). `livrée` et `annulée` sont finaux (`[*]`). Toute transition hors de ce graphe → `ValueError` → **400** « transition interdite : X → Y ». Un client non admin ne peut déclencher que `annulée` sur **sa** commande (sinon 403).

---

## 🔁 Famille 3 — INTERACTION

### 3.1 Diagramme de séquence — obtention du token (login)

```mermaid
%% LÉGENDE séquence UML : lignes verticales = lignes de vie · flèche pleine = appel synchrone · flèche retour pointillée = réponse · autonumber = ordre des messages
sequenceDiagram
    autonumber
    participant C as 👤 Client curl
    participant F as app.py Flask
    participant R as routes/auth.py
    participant S as security.py
    participant D as db.py session
    C->>F: POST /api/auth/login - JSON email, password
    F->>R: dispatch - blueprint auth
    R->>D: session.query User filter_by email
    D-->>R: user ou None
    alt mauvais identifiants
        R-->>C: 401 - error identifiants invalides
    else identifiants OK
        R->>S: check_password_hash + creer_token user
        S-->>R: token JWT signé HS256 - payload user_id, role, exp 24h
        R-->>C: 200 - message + token JWT eyJ...
    end
```

**Légende** : le token n'est émis qu'après vérification du hash du mot de passe ; le `alt/else` UML montre les deux issues (401 ou 200+token).

### 3.2 Diagramme de séquence — requête protégée (ex. POST /api/commandes)

```mermaid
%% LÉGENDE : idem 3.1 · la vérification du token a lieu AVANT l'exécution de la route (décorateur @login_required)
sequenceDiagram
    autonumber
    participant C as 👤 Client curl + header Bearer
    participant F as app.py Flask
    participant R as routes/commandes.py
    participant S as security.py
    participant D as db.py session
    participant M as modelsSQLAlchemy.py
    C->>F: POST /api/commandes + Authorization: Bearer <token>
    F->>R: dispatch - blueprint commandes
    R->>S: verifier_token - décorateur @login_required
    alt token absent/invalide/expiré
        S-->>C: 401 - error token requis ou invalide
    else token valide
        S-->>R: payload {user_id, role}
        R->>D: session.get Product product_id + verifier_stock
        D-->>R: produit / stock
        alt stock insuffisant ou quantité ≤ 0
            R-->>C: 400 - error stock insuffisant...
        else
            R->>M: new Order en_attente + OrderItem prix figé + calculer_total
            R->>D: session.add order + session.commit
            D-->>R: INSERT OK
            R-->>C: 201 - commande JSON id, statut, total, lignes
        end
    end
```

**Légende** : trois `alt` UML imbriqués = les trois niveaux de contrôle (authentification 401 → validation métier 400 → succès 201). C'est exactement le contrat documenté dans `docs/docAPI.md` (chapitre 1).

---

## 📋 Tableau récapitulatif

| Famille UML | Diagramme | Bloc Mermaid | Fichier source / référence |
|---|---|---|---|
| Structure | classes | `classDiagram` | §1.1 = `app/modelsSQLAlchemy.py` + `docs/canva-classes-confirme.mmd` |
| Structure | entité-association | `erDiagram` | §1.2 = tables de `digimarket.db` (`docs/etape3-objets.md`) |
| Structure | composants/packages | `flowchart` (subgraphs) | §1.3 = arborescence `app/` (`docs/canva-structure-confirme.mmd`) |
| Comportement | cas d'utilisation | `flowchart` (approx.) | §2.1 = `docs/etape1-use-cases.md` |
| Comportement | activité « passer une commande » | `flowchart` (couloirs) | §2.2 = `routes/commandes.py` + `docs/demo.md` |
| Comportement | machine à états `Order.statut` | `stateDiagram-v2` | §2.3 = `Order.TRANSITIONS` (`modelsSQLAlchemy.py`) |
| Interaction | séquence login → token | `sequenceDiagram` | §3.1 = `routes/auth.py` + `security.py` |
| Interaction | séquence requête protégée | `sequenceDiagram` | §3.2 = `routes/commandes.py` + contrat `docs/docAPI.md` |

> 💡 Pour la démo orale : projeter §1.1 (structure), §2.3 (machine à états) et §3.2 (séquence) — ce sont les trois diagrammes UML les plus parlants pour expliquer le fonctionnement de l'API.
