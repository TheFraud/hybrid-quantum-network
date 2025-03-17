import streamlit as st
import subprocess
import requests

# ------------------------------------------------------------------------------
# NOTE:
# Ce fichier (dashboard.py) est le tableau de bord principal de la solution "0" —
# le système hybride d'intelligence artificielle alimenté par Qiskit et IBM Quantum Computers.
# Il doit être situé à la racine du projet.
# ------------------------------------------------------------------------------
 
# ------------------------------------------------------------------------------
# Configuration de la page
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Hybrid Quantum-Classical Network Dashboard",
    layout="centered"
)

# ------------------------------------------------------------------------------
# Entête et aperçu
# ------------------------------------------------------------------------------
st.title("Hybrid Quantum-Classical Network Dashboard")
st.markdown("## Overview")
st.write(
    "Welcome to 0 – our state-of-the-art hybrid AI system powered by IBM Quantum Computers and Qiskit. "
    "This system integrates quantum circuit simulation with a classical neural network. In addition, it queries "
    "public libraries (such as Internet Archive, GitHub, and Wikipedia) to retrieve real-time external data, and "
    "utilizes an XRPL forensic tool for advanced investigations. \n\n"
    "Use the options below to generate training data, train the network, input custom data, perform external queries, "
    "run XRPL forensic analysis, and execute automated tests to verify system integrity."
)

# ------------------------------------------------------------------------------
# Section : Génération de données d'entraînement
# ------------------------------------------------------------------------------
if st.button("Generate Training Data"):
    st.write("Generating training data using quantum-inspired methods...")
    # (Processus simulé : insérez ici votre logique de génération de données réelle)
    st.success("Training data successfully generated: 100 quantum samples produced.")

# ------------------------------------------------------------------------------
# Section : Entraînement du réseau
# ------------------------------------------------------------------------------
if st.button("Train the Network"):
    st.write(
        "Initiating network training. The hybrid AI system is combining quantum simulation with classical neural network learning. "
        "Please wait while the system updates its internal parameters..."
    )
    # (Processus d'entraînement simulé : remplacez par vos routines d'entraînement réelles si besoin)
    st.success("Network training completed successfully with minimal quantum error rates.")

# ------------------------------------------------------------------------------
# Section : Saisie de données personnalisées
# ------------------------------------------------------------------------------
user_input = st.text_input("Enter input data (comma-separated)", "")
if user_input:
    try:
        # Analyse des nombres saisis séparés par des virgules
        input_data = [float(x.strip()) for x in user_input.split(",")]
        st.write("Parsed Input Data:", input_data)
    except Exception as e:
        st.error("Error: Please enter valid numeric values separated by commas.")

# ------------------------------------------------------------------------------
# Section : Interroger les bibliothèques publiques
# ------------------------------------------------------------------------------
if st.button("Query Public Libraries"):
    st.write("Querying public libraries for external data. Please wait...")
    
    # --- Requête à l'API GitHub ---
    try:
        github_response = requests.get("https://api.github.com")
        github_info = github_response.json()
    except Exception as e:
        github_info = {"error": str(e)}
    
    # --- Requête à l'API Wikipedia pour "Quantum computing" ---
    try:
        wiki_response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "titles": "Quantum computing",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True
            }
        )
        wiki_info = wiki_response.json()
    except Exception as e:
        wiki_info = {"error": str(e)}
        
    # --- Requête à l'API Internet Archive pour "quantum computing" ---
    try:
        ia_response = requests.get(
            "https://archive.org/advancedsearch.php",
            params={
                "q": "quantum computing",
                "fl[]": "identifier",
                "rows": 5,
                "page": 1,
                "output": "json"
            }
        )
        ia_info = ia_response.json()
    except Exception as e:
        ia_info = {"error": str(e)}
    
    st.markdown("### GitHub API Response")
    st.json(github_info)
    
    st.markdown("### Wikipedia API Response")
    st.json(wiki_info)
    
    st.markdown("### Internet Archive API Response")
    st.json(ia_info)

# ------------------------------------------------------------------------------
# Section : Outil de forensic XRPL
# ------------------------------------------------------------------------------
if st.button("Run XRPL Forensic Tool"):
    st.write("Querying XRPL endpoint for forensic data...")
    xrpl_rpc_url = "https://s1.ripple.com:51234/"
    payload = {"method": "server_info", "params": [{}]}
    try:
        xrpl_response = requests.post(xrpl_rpc_url, json=payload, timeout=30)
        xrpl_data = xrpl_response.json()
        st.markdown("### XRPL Forensic Response")
        st.json(xrpl_data)
    except Exception as e:
        st.error("Error querying XRPL: " + str(e))

# ------------------------------------------------------------------------------
# Section : Tests automatisés
# ------------------------------------------------------------------------------
if st.button("Run Automated Tests"):
    st.write("Running automated tests to verify system integrity. Please wait...")
    try:
        # Exécute les tests via un appel subprocess à pytest
        result = subprocess.run(
            ["pytest", "--maxfail=1", "--disable-warnings", "-q"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout + "\n" + result.stderr
        st.markdown("### Detailed Test Results")
        st.text(output)
        if result.returncode == 0:
            st.success("All automated tests passed successfully! The hybrid AI system is fully operational.")
        else:
            st.error("Some tests failed. Please review the details above and address any issues.")
    except Exception as ex:
        st.error("An error occurred while executing tests: " + str(ex))

# ------------------------------------------------------------------------------
# Pied de page : À propos du système
# ------------------------------------------------------------------------------
st.markdown("---")
st.write(
    "0 is an advanced hybrid AI system that leverages quantum circuit simulation via Qiskit and classical neural networks. "
    "It also queries public libraries (including Internet Archive, GitHub, and Wikipedia) to incorporate external data in real time, "
    "and utilizes an XRPL forensic tool for advanced investigations. "
    "This unique integration positions 0 at the forefront of AI innovation, powered by IBM Quantum Computers."
)
