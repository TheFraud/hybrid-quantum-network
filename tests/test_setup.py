#!/usr/bin/env python3
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
project_root = Path(__file__).parent.parent  # Remonter d'un niveau pour atteindre la racine

required_paths = {
    "src/data/connectors.py": "Module des connecteurs",
    "config/config.yml": "Fichier de configuration principale",
    "logs": "Dossier des logs",
    "checkpoints": "Dossier des points de contrôle"
}

def verify_project_structure() -> bool:
    """Vérifie la structure du projet"""
    success = True
    for rel_path, description in required_paths.items():
        full_path = project_root / rel_path
        if full_path.exists():
            logger.info(f"✓ {rel_path} trouvé ({description})")
        else:
            logger.error(f"✗ {rel_path} manquant ({description})")
            success = False
    return success

def check_external_dependencies() -> bool:
    """Vérifie les dépendances externes"""
    required_modules = {
        'aiohttp': 'Client HTTP asynchrone',
        'internetarchive': 'Client Internet Archive',
        'numpy': 'Calcul numérique',
        'qiskit': 'Framework quantique',
        'streamlit': 'Interface utilisateur'
    }
    
    success = True
    for module, description in required_modules.items():
        try:
            __import__(module)
            logger.info(f"✓ Module {module} installé ({description})")
        except ImportError:
            logger.error(f"✗ Module {module} manquant ({description})")
            success = False
    return success

def check_api_configurations() -> bool:
    """Vérifie les configurations des APIs"""
    success = True
    
    # Vérification du token IBM Quantum
    ibm_token = os.getenv('IBM_TOKEN')
    if not ibm_token:
        token_file = Path.home() / '.ibm' / 'token'
        if token_file.exists():
            with open(token_file) as f:
                ibm_token = f.read().strip()
    
    if ibm_token:
        logger.info("✓ Token IBM Quantum trouvé")
    else:
        logger.warning("! Token IBM Quantum manquant (optionnel)")
    
    # Vérification de l'API IEEE (optionnelle)
    try:
        import ieee_api
        logger.info("✓ Module IEEE API installé")
    except ImportError:
        logger.warning("! Module IEEE API non trouvé (optionnel)")
    
    return success

def test_system_dependencies() -> bool:
    """Test principal des dépendances système"""
    try:
        structure_ok = verify_project_structure()
        dependencies_ok = check_external_dependencies()
        api_ok = check_api_configurations()
        
        if structure_ok and dependencies_ok and api_ok:
            logger.info("✓ Toutes les dépendances sont correctement configurées")
            return True
        else:
            logger.warning("! Certaines dépendances sont manquantes ou mal configurées")
            return False
            
    except Exception as e:
        logger.error(f"✗ Erreur système : {str(e)}")
        return False

def run_setup_tests():
    """Exécute tous les tests de configuration"""
    logger.info("=== Début des tests de configuration du projet ===")
    success = test_system_dependencies()
    if success:
        logger.info("=== Tous les tests de configuration ont réussi ===")
    else:
        logger.error("=== Certains tests de configuration ont échoué ===")
    return success

if __name__ == "__main__":
    success = run_setup_tests()
    sys.exit(0 if success else 1)
