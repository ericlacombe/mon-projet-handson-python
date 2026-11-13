"""
db.py — Moteur SQLite + session partagée (SQLAlchemy pur).
Script standalone d'utilisation de SQLAlchemy (ORM) avec SQLite.
Ce script executable permet d'executer des opérations via une session SQLAlchemy

Pourquoi un module séparé ? Pour que app.py ET les routes (routes/auth.py)
utilisent la MÊME session sans import circulaire :
app.py importe routes/auth.py (blueprint), donc routes/auth.py ne peut pas
importer app.py. Tout le monde importe db.py à la place.
"""

# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------
# create_engine : crée la connexion vers la base de données
from sqlalchemy import create_engine
# sessionmaker   : fabrique de sessions (conversations avec la BDD)
from sqlalchemy.orm import sessionmaker

# Les modèles de tables de la base de données sont définis dans modelsSQLAlchemy.py
# Importer ce fichier ne déclenche aucune opération en base (pas de code d'exécution)
from app.modelsSQLAlchemy import Base   # la base des modèles (métadonnée des tables)

# ------------------------------------------------------------------
# 1. Création du moteur de connexion à la base de données
# ------------------------------------------------------------------
# 'sqlite:///digimarket.db' : URL de connexion.
#   - "sqlite"  : pilote SQLite (fichier local, pas de serveur)
#   - "///"     : trois slashes = chemin relatif (dossier du projet)
#   - le fichier "digimarket.db" est créé automatiquement s'il n'existe pas
# echo=False : désactive l'affichage des requêtes SQL (mettre True pour déboguer)
engine = create_engine("sqlite:///digimarket.db", echo=False)

# ------------------------------------------------------------------
# 2. Création des tables dans la base de données
# ------------------------------------------------------------------
# Base.metadata contient la description de toutes les tables déclarées
# (dans modelsSQLAlchemy.py : users 🥉, categories + products 🥈 — create_all
# couvre automatiquement les tables des niveaux suivants, pas besoin de le modifier).
# create_all(engine) envoie les ordres
# "CREATE TABLE" si les tables n'existent pas encore. Sans danger :
# les tables existantes ne sont pas recréées ni supprimées.
# C'est ici que les tables vides sont créées.
Base.metadata.create_all(engine)

# ------------------------------------------------------------------
# 3. Création d'une session
# ------------------------------------------------------------------
# Une session est l'intermédiaire entre le code Python et la base de données.
# C'est via la session qu'on ajoute, modifie, supprime ou recherche des objets.
#
# sessionmaker(bind=engine) : configure une "usine à sessions" liée au moteur.
# Session()                 : crée une nouvelle session prête à l'emploi.
#
# Cycle de vie d'une session :
#   - session.add(objet)    : marque un objet pour insertion
#   - session.commit()      : valide les changements en base
#   - session.rollback()    : annule les changements non validés
#   - session.close()       : ferme la session (libère les ressources)
Session = sessionmaker(bind=engine)
session = Session()
