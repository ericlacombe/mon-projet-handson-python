"""
routes/produits.py — Blueprint de la fonction métier F2 « Gérer le catalogue ».

Niveau 🥈 : le catalogue produits (partie 4.7, contrat d'API).

Routes disponibles :
  GET    /api/produits          →  liste des produits (public, recherche ?q=)
  GET    /api/produits/<id>     →  détail d'un produit (public)
  POST   /api/produits          →  crée un produit        (ADMIN uniquement, 4.11)
  PUT    /api/produits/<id>     →  modifie un produit     (ADMIN)
  DELETE /api/produits/<id>     →  supprime un produit    (ADMIN)
  POST   /api/categories        →  crée une catégorie     (ADMIN)

Pourquoi un blueprint séparé ? Un fichier par fonction métier (4.8) :
app.py reste l'assemblage, il enregistre juste produits_bp.
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
from flask import Blueprint, request, jsonify

# session partagée (db.py — évite l'import circulaire avec app.py)
from app.db import session
# décorateurs de sécurité (4.11) : admin_required → 401 sans token, 403 si pas admin
from app.security import admin_required
# modèles (définis dans modelsSQLAlchemy.py)
from app.modelsSQLAlchemy import Category, Product

# Le blueprint regroupe les routes du domaine "produits", préfixées /api
produits_bp = Blueprint("produits", __name__, url_prefix="/api")


# ------------------------------------------------------------------
# GET /api/produits — liste + recherche (PUBLIC, Visiteur)
# ------------------------------------------------------------------
@produits_bp.route("/produits", methods=["GET"])
def liste_produits():
    """Renvoie la liste des produits. Recherche optionnelle : ?q=texte
    (filtre sur le nom, insensible à la casse)."""
    # query de base : tous les produits
    query = session.query(Product)
    # ?q=pc → filtre LIKE '%pc%' sur le nom (recherche par nom, CDC)
    q = request.args.get("q", "").strip()
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    produits = query.all()
    # Sérialisation manuelle en JSON (liste de dicts)
    return jsonify([
        {"id": p.id, "name": p.name, "description": p.description,
         "price": p.price, "stock": p.stock, "category_id": p.category_id}
        for p in produits
    ]), 200


# ------------------------------------------------------------------
# GET /api/produits/<id> — détail d'un produit (PUBLIC)
# ------------------------------------------------------------------
@produits_bp.route("/produits/<int:pid>", methods=["GET"])
def detail_produit(pid):
    """Renvoie le détail d'un produit, ou 404 s'il n'existe pas."""
    produit = session.get(Product, pid)          # get() = requête par clé primaire
    if produit is None:
        return jsonify({"error": "produit introuvable"}), 404
    return jsonify({
        "id": produit.id, "name": produit.name, "description": produit.description,
        "price": produit.price, "stock": produit.stock,
        "categorie": produit.category.name if produit.category else None,
    }), 200


# ------------------------------------------------------------------
# POST /api/produits — créer un produit (ADMIN, 4.11)
# ------------------------------------------------------------------
@produits_bp.route("/produits", methods=["POST"])
@admin_required                                   # 401 sans token, 403 si pas admin
def creer_produit(user):
    """Crée un produit. Entrée JSON : {name, description, price, stock, category_id}.

    Sorties : 201 créé · 400 invalide (champs manquants, prix/stock < 0, catégorie
    inexistante) · 401/403 selon le token.
    """
    body = request.get_json() or {}

    # 400 : champs obligatoires manquants
    if not body.get("name") or body.get("price") is None or body.get("category_id") is None:
        return jsonify({"error": "name, price et category_id requis"}), 400

    # 4.3 : contraintes métier — prix >= 0 et stock >= 0
    if body["price"] < 0 or body.get("stock", 0) < 0:
        return jsonify({"error": "price et stock doivent être >= 0"}), 400

    # 400 : la catégorie référencée (FK) doit exister
    if session.get(Category, body["category_id"]) is None:
        return jsonify({"error": "catégorie inexistante"}), 400

    produit = Product(
        name=body["name"],
        description=body.get("description", ""),
        price=body["price"],
        stock=body.get("stock", 0),
        category_id=body["category_id"],
    )
    session.add(produit)                          # marque pour insertion (rien d'écrit encore)
    session.commit()                              # INSERT définitif en base
    return jsonify({"message": "produit créé", "id": produit.id}), 201


# ------------------------------------------------------------------
# PUT /api/produits/<id> — modifier un produit (ADMIN)
# ------------------------------------------------------------------
@produits_bp.route("/produits/<int:pid>", methods=["PUT"])
@admin_required
def modifier_produit(pid, user):
    """Modifie un produit existant (champs fournis remplacés). 404 si inconnu."""
    produit = session.get(Product, pid)
    if produit is None:
        return jsonify({"error": "produit introuvable"}), 404
    body = request.get_json() or {}
    # 4.3 : si price/stock fournis, ils doivent être >= 0
    if "price" in body and body["price"] < 0:
        return jsonify({"error": "price doit être >= 0"}), 400
    if "stock" in body and body["stock"] < 0:
        return jsonify({"error": "stock doit être >= 0"}), 400
    # mise à jour champ par champ (seuls les champs fournis changent)
    for champ in ("name", "description", "price", "stock", "category_id"):
        if champ in body:
            setattr(produit, champ, body[champ])
    session.commit()
    return jsonify({"message": "produit modifié", "id": produit.id}), 200


# ------------------------------------------------------------------
# DELETE /api/produits/<id> — supprimer un produit (ADMIN)
# ------------------------------------------------------------------
@produits_bp.route("/produits/<int:pid>", methods=["DELETE"])
@admin_required
def supprimer_produit(pid, user):
    """Supprime un produit. 204 si OK, 404 si inconnu."""
    produit = session.get(Product, pid)
    if produit is None:
        return jsonify({"error": "produit introuvable"}), 404
    session.delete(produit)
    session.commit()
    return "", 204                               # 204 = No Content (corps vide)


# ------------------------------------------------------------------
# POST /api/categories — créer une catégorie (ADMIN)
# ------------------------------------------------------------------
@produits_bp.route("/categories", methods=["POST"])
@admin_required
def creer_categorie(user):
    """Crée une catégorie {name}. 201 · 400 si name manque · 409 si nom déjà pris."""
    body = request.get_json() or {}
    if not body.get("name"):
        return jsonify({"error": "name requis"}), 400
    # 4.3 : unicité du nom de catégorie (contrainte unique en base)
    if session.query(Category).filter_by(name=body["name"]).first():
        return jsonify({"error": "catégorie déjà existante"}), 409
    cat = Category(name=body["name"])
    session.add(cat)
    session.commit()
    return jsonify({"message": "catégorie créée", "id": cat.id}), 201
