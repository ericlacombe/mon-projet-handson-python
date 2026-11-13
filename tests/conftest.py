"""
tests/conftest.py — configuration commune à tous les tests (pytest la charge avant tout).

Ici : on donne une SECRET_KEY de test pour que app/security.py s'importe
même sans fichier .env (les vrais secrets restent dans .env, jamais commité).
"""
import os

os.environ.setdefault("SECRET_KEY", "cle_de_test_pour_pytest_32_caracteres_min")
