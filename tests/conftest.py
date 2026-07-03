from pathlib import Path
import sys


# Ajoute la racine du projet au PYTHONPATH pour que `import src...` fonctionne
# quel que soit le dossier depuis lequel `pytest` est lancé.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
