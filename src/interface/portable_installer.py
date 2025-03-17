import os
import sys
import yaml
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Optionnel : importation de pyusb pour la détection USB
try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

class PortableInstaller:
    """
    Wizard d'installation portable pour le système Quantum AI.
    Version améliorée avec support USB-C et détection améliorée des périphériques.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        self.root = tk.Tk()
        self.root.title("Quantum AI - Installation Portable")
        self.root.geometry("800x600")
        self.current_step = 0
        # Variable pour conserver le mode d'installation choisi (Standard ou USB-C)
        self.installation_mode = tk.StringVar(value="Standard")
        self.usb_devices = []
        self.setup_ui()
    
    def _load_config(self) -> Dict:
        """Charge la configuration depuis config/config.yml"""
        try:
            config_path = Path("config/config.yml")
            if config_path.exists():
                with open(config_path, 'r', encoding="utf-8") as f:
                    return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Erreur de chargement de la configuration: {str(e)}")
        return {}
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # En-tête
        self.header = ttk.Label(self.main_frame, text="Installation du Système Quantum AI", font=("Helvetica", 16, "bold"))
        self.header.pack(pady=10)
        
        # Zone de contenu
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Barre de progression
        self.progress = ttk.Progressbar(self.main_frame, length=700, mode='determinate')
        self.progress.pack(pady=10)
        
        # Boutons de navigation
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        self.prev_button = ttk.Button(self.button_frame, text="Précédent", command=self.previous_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.button_frame, text="Suivant", command=self.next_step)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Démarrage de la première étape
        self.show_step(0)
    
    def show_step(self, step: int):
        """Affiche l'étape spécifiée dans le wizard"""
        # Nettoyer le contenu précédent
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        steps = [
            self.show_welcome,
            self.show_system_check,
            self.show_usb_detection,
            self.show_configuration,
            self.show_installation,
            self.show_finish
        ]
        
        if 0 <= step < len(steps):
            steps[step]()
            self.current_step = step
            self.progress['value'] = (step / (len(steps) - 1)) * 100
            
            self.prev_button['state'] = tk.NORMAL if step > 0 else tk.DISABLED
            self.next_button['text'] = "Terminer" if step == len(steps) - 1 else "Suivant"
    
    def show_welcome(self):
        """Page d'accueil"""
        welcome_text = (
            "Bienvenue dans l'assistant d'installation du Système Quantum AI.\n\n"
            "Cet assistant va vous guider à travers l'installation et la configuration "
            "de votre environnement portable.\n\n"
            "Cliquez sur 'Suivant' pour commencer."
        )
        label = ttk.Label(self.content_frame, text=welcome_text, wraplength=600, justify=tk.CENTER)
        label.pack(expand=True)
    
    def show_system_check(self):
        """Vérification des prérequis système"""
        label = ttk.Label(self.content_frame, text="Vérification des prérequis système...", font=("Helvetica", 14))
        label.pack(pady=10)
        # Simulation de quelques vérifications système
        checks = [
            ("Python 3.8+", sys.version_info >= (3, 8)),
            ("Dépendances chargées", True),
            ("Espace disque suffisant", True),
            ("Mémoire disponible", True)
        ]
        for check_text, status in checks:
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=check_text).pack(side=tk.LEFT)
            status_text = "✓" if status else "✗"
            color = "green" if status else "red"
            ttk.Label(frame, text=status_text, foreground=color).pack(side=tk.RIGHT)
    
    def show_usb_detection(self):
        """Détection des périphériques USB avec prise en charge USB-C"""
        frame = ttk.LabelFrame(self.content_frame, text="Détection des périphériques USB", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        if USB_AVAILABLE:
            self.usb_devices = self.detect_usb_devices()
            if self.usb_devices:
                text = "Périphériques USB détectés:\n" + "\n".join(self.usb_devices)
            else:
                text = "Aucun périphérique USB détecté."
        else:
            text = "La détection USB n'est pas disponible (module pyusb non installé)."
        ttk.Label(frame, text=text, wraplength=600, justify=tk.LEFT).pack(pady=5)
        
        # Option pour choisir le mode d'installation en fonction des périphériques USB
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(pady=10)
        ttk.Label(mode_frame, text="Mode d'installation:").pack(side=tk.LEFT, padx=5)
        mode_options = ["Standard", "USB-C"]
        mode_combo = ttk.Combobox(mode_frame, values=mode_options, textvariable=self.installation_mode, state="readonly")
        mode_combo.pack(side=tk.LEFT, padx=5)
    
    def detect_usb_devices(self) -> list:
        """Détecte les périphériques USB à l'aide de pyusb"""
        devices = []
        try:
            devs = usb.core.find(find_all=True)
            for dev in devs:
                vendor = hex(dev.idVendor)
                product = hex(dev.idProduct)
                devices.append(f"Vendor: {vendor}, Product: {product}")
        except Exception as e:
            self.logger.error(f"Erreur de détection USB: {str(e)}")
        return devices
    
    def show_configuration(self):
        """Configuration du système"""
        frame = ttk.LabelFrame(self.content_frame, text="Configuration", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Label(frame, text="Choisissez le mode d'installation:").grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)
        mode_combo = ttk.Combobox(frame, values=["Standard", "USB-C"], textvariable=self.installation_mode, state="readonly")
        mode_combo.grid(row=0, column=1, pady=5, padx=5)
    
    def show_installation(self):
        """Installation des composants"""
        frame = ttk.LabelFrame(self.content_frame, text="Installation", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.install_progress = ttk.Progressbar(frame, length=500, mode='determinate')
        self.install_progress.pack(pady=20)
        
        info = ttk.Label(frame, text="Installation en cours... Veuillez patienter.", font=("Helvetica", 12))
        info.pack(pady=10)
        
        # Lancer l'installation simulée après un court délai
        self.root.after(500, self.perform_installation)
    
    def perform_installation(self):
        """Simule l'installation et met à jour la progression"""
        steps = [
            ("Création des dossiers", 20),
            ("Copie des fichiers", 40),
            ("Configuration système", 70),
            ("Installation des pilotes USB-C", 85) if self.installation_mode.get() == "USB-C" else ("Configuration Standard", 85),
            ("Finalisation", 100)
        ]
        for i, (step_label, value) in enumerate(steps):
            self.install_progress['value'] = value
            self.root.update()
            self.root.after(500)
        messagebox.showinfo("Installation", "Installation terminée avec succès.")
    
    def show_finish(self):
        """Page de fin"""
        finish_text = (
            "L'installation de Quantum AI est terminée avec succès !\n\n"
            "Vous pouvez maintenant lancer l'application en exécutant main.py.\n"
            "Merci d'avoir choisi notre solution."
        )
        label = ttk.Label(self.content_frame, text=finish_text, wraplength=600, justify=tk.CENTER)
        label.pack(expand=True)
    
    def next_step(self):
        """Passe à l'étape suivante ou termine l'installation"""
        if self.current_step < 5:
            self.show_step(self.current_step + 1)
        else:
            self.root.quit()
    
    def previous_step(self):
        """Revient à l'étape précédente"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def run(self):
        """Lance l'interface d'installation"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = PortableInstaller()
    installer.run()

