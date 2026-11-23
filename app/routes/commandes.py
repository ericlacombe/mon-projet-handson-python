"""
routes/commandes.py — Blueprint de la fonction métier F3 « Gérer les commandes » (niveau 🥇).

Routes (contrat 4.7 🥇) :
  POST  /api/commandes                  → crée une commande (CLIENT connecté, 4.11)
  GET   /api/commandes                  → liste SES commandes (client) ou TOUTES (admin)
  GET   /api/commandes/<id>             → détail d'une commande (propriétaire ou admin)
  GET   /api/commandes/<id>/lignes      → lignes de la commande (idem)
  PATCH /api/commandes/<id>/statut      → change le statut (admin : tout ; client_propriétaire : annulée)

Règles métier (4.3/4.6) : quantite > 0, stock suffisant, transitions autorisées uniquement,
stock décrémenté à la validation et restitué à l'annulation.
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
from flask import Blueprint, request, jsonify

# session partagée (db.py — évite l'import circulaire avec app.py)
from app.db import session
# sécurité (4.11) : login_required → 401 sans token valide ; user injecté dans la route
from app.security import login_required
# modèles (modelsSQLAlchemy.py) : Order, OrderItem, Product
from app.modelsSQLAlchemy import Order, OrderItem, Product
# fonctions pures 4.9 (app/utils.py)
from app.utils import calculer_total, verifier_stock

# Blueprint du domaine "commandes", préfixé /api (un fichier par fonction métier, 4.8)
commandes_bp = Blueprint("commandes", __name__, url_prefix="/api")


def _peut_voir(order, user) -> bool:
    """Règle 4.11 étendue (🥇) : on voit une commande si on est admin OU son propriétaire."""
    return user.role == "admin" or order.user_id == user.id


def _serialize(order):
    """Sérialise une commande en dict JSON."""
    return {
        "id": order.id,
        "user_id": order.user_id,
        "address_livraison": order.address_livraison,
        "date_creation": order.date_creation.isoformat() if order.date_creation else None,
        "statut": order.statut,
        "total": order.total,
        "lignes": [
            {"product_id": i.product_id, "quantite": i.quantite, "prix_unitaire": i.prix_unitaire}
            for i in order.items
        ],
    }


# ------------------------------------------------------------------
# POST /api/commandes — créer une commande (CLIENT connecté)
# ------------------------------------------------------------------
@commandes_bp.route("/commandes", methods=["POST"])
@login_required                                    # 401 sans token
def creer_commande(user):
    """Crée une commande pour l'utilisateur connecté.
    Entrée JSON : {"address_livraison": "...", "items": [{"product_id": 1, "quantite": 2}, ...]}
    Sorties : 201 créée · 400 invalide (adresse vide, item invalide, stock insuffisant) · 401."""
    body = request.get_json() or {}
    adresse = (body.get("address_livraison") or "").strip()
    items = body.get("items") or []
    # 400 : adresse obligatoire et au moins une ligne
    if not adresse or not items:
        return jsonify({"error": "address_livraison et items (non vide) requis"}), 400

    order = Order(user_id=user.id, address_livraison=adresse)   # statut = en_attente (défaut)
    for it in items:
        product_id = it.get("product_id")
        quantite = it.get("quantite")
        produit = session.get(Product, product_id) if product_id else None
        # 400 : produit inexistant ou quantite <= 0 (4.3, via verifier_stock)
        if produit is None:
            return jsonify({"error": f"produit {product_id} inexistant"}), 400
        try:
            if not verifier_stock(produit, quantite):
                return jsonify({"error": f"stock insuffisant pour {produit.name}"}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        # ligne avec prix FIGÉ au prix actuel du produit
        order.items.append(OrderItem(product_id=produit.id,
                                     quantite=quantite, prix_unitaire=produit.price))
    # total calculé par la fonction pure 4.9
    order.total = calculer_total(order)
    session.add(order)
    session.commit()                               # INSERT order + order_items
    return jsonify(_serialize(order)), 201


# ------------------------------------------------------------------
# GET /api/commandes — liste (client = les siennes, admin = toutes)
# ------------------------------------------------------------------
@commandes_bp.route("/commandes", methods=["GET"])
@login_required
def liste_commandes(user):
    """Renvoie les commandes : celles de l'utilisateur (client) ou toutes (admin)."""
    q = session.query(Order)
    if user.role != "admin":
        q = q.filter_by(user_id=user.id)           # client ne voit que les siennes
    return jsonify([_serialize(o) for o in q.all()]), 200


# ------------------------------------------------------------------
# GET /api/commandes/<id> et /<id>/lignes — détail (propriétaire ou admin)
# ------------------------------------------------------------------
@commandes_bp.route("/commandes/<int:oid>", methods=["GET"])
@commandes_bp.route("/commandes/<int:oid>/lignes", methods=["GET"])
@login_required
def detail_commande(oid, user):
    """Détail d'une commande. 404 si inconnue · 403 si ni propriétaire ni admin (4.11)."""
    order = session.get(Order, oid)
    if order is None:
        return jsonify({"error": "commande introuvable"}), 404
    if not _peut_voir(order, user):
        return jsonify({"error": "accès interdit à cette commande"}), 403
    return jsonify(_serialize(order)), 200


# ------------------------------------------------------------------
# PATCH /api/commandes/<id>/statut — changer le statut (4.6)
# ------------------------------------------------------------------
@commandes_bp.route("/commandes/<int:oid>/statut", methods=["PATCH"])
@login_required
def changer_statut(oid, user):
    """Change le statut : {"statut": "validée"}.
    - admin : toute transition autorisée ;
    - client_propriétaire : uniquement "annulée" ;
    - 400 transition interdite (4.6, ValueError) · 403 non propriétaire · 404 inconnu · 401.
    Effets de bord : validation → stock décrémenté ; annulation → stock restitué."""
    order = session.get(Order, oid)
    if order is None:
        return jsonify({"error": "commande introuvable"}), 404
    if not _peut_voir(order, user):
        return jsonify({"error": "accès interdit à cette commande"}), 403
    body = request.get_json() or {}
    nouveau = body.get("statut")
    # client non admin ne peut QUE annuler sa propre commande (pas admin ici puisqu'on a passé _peut_voir)
    if user.role != "admin" and nouveau != "annulée":
        return jsonify({"error": "un client ne peut qu'annuler sa commande"}), 403
    ancien = order.statut
    try:
        order.changer_statut(nouveau)              # 4.6 : lève ValueError si interdit
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    # effets de bord sur le stock (validation décrémente, annulation restitue)
    if nouveau == "validée":
        for item in order.items:
            item.product.stock -= item.quantite
    if nouveau == "annulée" and ancien != "annulée":
        for item in order.items:
            item.product.stock += item.quantite
    session.commit()
    return jsonify(_serialize(order)), 200
