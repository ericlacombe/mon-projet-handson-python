"""
app/utils.py — fonctions Python « pures » (partie 4.9, niveau 🥇).

Une fonction pure = transformation de données SANS état et SANS effet de bord :
- elle ne lit/écrit PAS la base (pas de session) ;
- même entrées → même résultat, toujours ;
- testable seule (test unitaire, sans route ni base) → tests/test_commandes.py.

Utilisées par routes/commandes.py (F3) : total d'une commande, vérification du stock.
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
# rien : ces fonctions ne touchent qu'aux objets passés en argument (pas de base)


# ------------------------------------------------------------------
# Fonctions pures (4.9)
# ------------------------------------------------------------------

def calculer_total(order) -> float:
    """Total d'une commande = somme des (quantite * prix_unitaire) de ses lignes.

    Pure : lit seulement order.items (déjà chargés), ne modifie rien.
    Appelée à la création de la commande (POST /api/commandes).
    """
    # sum(...) sur un générateur : total = Σ ligne.quantite * ligne.prix_unitaire
    return sum(item.quantite * item.prix_unitaire for item in order.items)


def verifier_stock(product, quantite: int) -> bool:
    """True si le produit a assez de stock pour la quantité demandée.

    Pure : ne modifie PAS le stock (c'est la route qui décrémente après validation).
    Lève ValueError si quantite <= 0 (contrainte 4.3 → la route renvoie 400).
    """
    # contrainte 4.3 : une quantité doit être strictement positive
    if quantite <= 0:
        raise ValueError(f"quantite invalide : {quantite} (doit être > 0)")
    # assez de stock ?
    return product.stock >= quantite
