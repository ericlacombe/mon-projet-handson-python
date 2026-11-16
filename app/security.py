"""
app/security.py — Module de SÉCURITÉ (partie 4.11, fonction métier F4).

Niveau 🥈 : toute la sécurité est regroupée ici :
- hachage/vérification des mots de passe (werkzeug) ;
- création/vérification des tokens JWT signés (PyJWT, HS256) ;
- décorateurs de contrôle d'accès : @login_required (401), @admin_required (403).

📌 Les 2 mécanismes (complémentaires, 2 menaces différentes) :
  1. HASH du mot de passe  → protège la BASE (si elle fuit, les mdp restent illisibles).
     Principe : on ne retrouve JAMAIS le mdp — on RECALCULE son hash avec un sel
     et on compare les 2 empreintes (même entrée → même hash). Le sel + les
     ~600 000 itérations PBKDF2 ralentissent les attaques par dictionnaire.
  2. TOKEN JWT SIGNÉ       → protège les REQUÊTES (prouve l'identité sans renvoyer
     le mdp). Un JWT = header.payload.signature : le payload est en clair (base64,
     JAMAIS de secret dedans : user_id, role, exp), la SIGNATURE = HMAC-SHA256
     (hash + clé secrète) garantit authenticité + intégrité. Ce n'est PAS chiffré.
     Un token = UNE connexion d'UN utilisateur : user_id et role sont embarqués
     (signés), donc token admin ≠ token client, et on ne peut pas modifier le rôle.

Le token JWT est une DONNÉE TEMPORAIRE (4.2) : pas de table, pas de classe.
La clé secrète SECRET_KEY SERT À SIGNER les tokens : si elle fuit, on peut forger
des tokens → elle est lue dans .env (jamais commité) + HTTPS en production.
Codes : 401 = pas authentifié (token absent/invalide/expiré) ; 403 = authentifié
mais rôle insuffisant (client sur une route admin).
"""

# ------------------------------------------------------------------
# Importations
# ------------------------------------------------------------------
# os  : lire les variables d'environnement (fichier .env, JAMAIS commité)
# jwt : bibliothèque PyJWT — créer et vérifier les tokens JWT
import os
import jwt
# datetime : date d'expiration du token (exp)
from datetime import datetime, timedelta, timezone
# functools.wraps : conserve le nom de la fonction décorée (indispensable à Flask)
from functools import wraps
# request : lire le header "Authorization: Bearer <token>" de la requête entrante
# jsonify : renvoyer les erreurs (401/403) en JSON
from flask import request, jsonify
# werkzeug.security (inclus avec Flask) :
# - generate_password_hash : hache un mot de passe (à l'inscription)
# - check_password_hash    : vérifie un mot de passe contre son hash (au login)
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
# Charger le fichier .env si présent (sans écraser les variables déjà définies)
# → au lancement (python -m app.app), SECRET_KEY vient de .env
if os.path.exists(".env"):
    for line in open(".env", encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

# La clé secrète SERT À SIGNER les tokens JWT : elle ne doit JAMAIS être dans
# le code ni committée → on la lit dans .env (déjà dans .gitignore)
SECRET_KEY = os.environ["SECRET_KEY"]
# Durée de validité d'un token : 24 heures
TOKEN_DUREE = timedelta(hours=24)
# Algorithme de signature du token
ALGO = "HS256"


# ------------------------------------------------------------------
# Création / vérification du token JWT
# ------------------------------------------------------------------
def creer_token(user):
    """Crée le token SIGNÉ (pas chiffré) pour UN utilisateur, à chaque login.

    Structure du JWT "xxxxx.yyyyy.zzzzz" :
      - header.payload en base64 → LISIBLES par tous (jamais de secret dedans) ;
      - signature = HMAC-SHA256(header.payload, SECRET_KEY) → prouve que le token
        vient de nous et n'a pas été modifié (le client ne peut pas changer le rôle).
    payload = {"user_id":..., "role":..., "exp":...}  → token admin ≠ token client.
    Le client renvoie ce token dans le header "Authorization: Bearer <token>".
    """
    payload = {
        "user_id": user.id,
        "role": user.role,
        # exp : date d'expiration (le token sera refusé après)
        "exp": datetime.now(timezone.utc) + TOKEN_DUREE,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)


def verifier_token():
    """Lit le header "Authorization: Bearer <token>", décode et VÉRIFIE la signature.

    Renvoie le payload (dict) si OK ; sinon None (token absent, invalide ou expiré).
    """
    # 1. Lire le header Authorization (ex. "Bearer xxxxx.yyyyy.zzzzz")
    header = request.headers.get("Authorization", "")
    # 2. Extraire le token après "Bearer "
    if not header.startswith("Bearer "):
        return None                       # pas de header Bearer → pas authentifié
    token = header[len("Bearer "):]
    try:
        # 3. Décoder + VÉRIFIER la signature (HMAC avec SECRET_KEY) ET l'expiration (exp)
        #    signature fausse → InvalidTokenError → 401 ; token volé périmé → 401
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        return None                       # token expiré → 401
    except jwt.InvalidTokenError:
        return None                       # token invalide/truqué → 401


# ------------------------------------------------------------------
# Décorateurs de contrôle d'accès (à poser sur les routes protégées)
# ------------------------------------------------------------------
def login_required(f):
    """DÉCORATEUR : la route exige un token JWT valide.

    Utilisation : @login_required au-dessus de la fonction endpoint.
    Sans token valide → réponse JSON 401 (Non authentifié).
    """
    @wraps(f)                             # garde le nom de la route (Flask en a besoin)
    def wrapper(*args, **kwargs):
        payload = verifier_token()
        if payload is None:
            # 401 = non authentifié (pas de token ou token invalide/expiré)
            return jsonify({"error": "token requis ou invalide"}), 401
        # On transmet le payload à la route (ex. pour connaître l'utilisateur)
        return f(*args, user=payload, **kwargs)
    return wrapper


def admin_required(f):
    """DÉCORATEUR : en plus d'un token valide, exige le rôle "admin".

    Token d'un simple client → 403 (authentifié mais PAS autorisé).
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload = verifier_token()
        if payload is None:
            return jsonify({"error": "token requis ou invalide"}), 401
        # Le rôle est EMBARQUÉ dans le token signé : un client ne peut pas
        # le changer (signature invalide → 401). Ici token valide mais role != admin.
        if payload.get("role") != "admin":
            # 403 = interdit : authentifié mais rôle insuffisant (vs 401 = pas authentifié)
            return jsonify({"error": "réservé aux administrateurs"}), 403
        return f(*args, user=payload, **kwargs)
    return wrapper
