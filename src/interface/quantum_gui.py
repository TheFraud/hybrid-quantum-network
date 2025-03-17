import tkinter as tk
from tkinter import ttk, messagebox
import math, time, psutil, random, asyncio, threading
from collections import defaultdict
from datetime import datetime

from qiskit import QuantumCircuit, visualization as qiskit_viz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx

# -------------------- Simulated Quantum Processor --------------------
class QuantumProcessor:
    def __init__(self, n_qubits=8, mode="hybrid"):
        self.n_qubits = n_qubits
        self.mode = mode

    def create_quantum_circuit(self, circuit_type="superposition", params=None):
        qc = QuantumCircuit(self.n_qubits)
        if circuit_type == "superposition":
            for i in range(self.n_qubits):
                qc.h(i)
        elif circuit_type == "entanglement":
            qc.h(0)
            for i in range(1, self.n_qubits):
                qc.cx(0, i)
        else:
            qc.h(0)
        qc.measure_all()
        return qc

    def execute_quantum_operation(self, op_type="measurement", params=None):
        return {"result": f"Operation '{op_type}' executed with parameters {params}"}

    def measure_quantum_state(self):
        return {"0" * self.n_qubits: 1.0}

    def get_resource_usage(self):
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "qubits": self.n_qubits,
            "mode": self.mode
        }

# -------------------- XRPL Forensic Monitor --------------------
class XRPLForensicMonitor:
    def __init__(self, hybrid_client=None):
        self.client = hybrid_client  # Simulé ici
        self.transaction_history = defaultdict(list)
        self.suspicious_activities = []
        self.high_volume_accounts = []
        self.network_graph = nx.Graph()

    async def analyze_transaction(self, tx: dict):
        account = tx.get("Account")
        try:
            amount = float(tx.get("Amount", 0)) / 1000000  # Conversion en XRP
        except Exception:
            amount = 0
        timestamp = time.time()
        self.transaction_history[account].append((timestamp, amount))
        self.update_network_graph(account, tx.get("Destination"), amount)
        if self.detect_high_frequency_trading(account):
            self.suspicious_activities.append({
                "type": "HIGH FREQUENCY TRADING",
                "account": account,
                "timestamp": timestamp
            })
        if amount > 100000:
            self.suspicious_activities.append({
                "type": "HIGH VALUE TRANSACTION",
                "account": account,
                "amount": amount,
                "timestamp": timestamp
            })
        self.update_high_volume_accounts()

    def detect_high_frequency_trading(self, account: str) -> bool:
        recent = [t for t, amt in self.transaction_history[account] if time.time() - t < 60]
        return len(recent) > 10

    def update_high_volume_accounts(self):
        self.high_volume_accounts = []
        for account, transactions in self.transaction_history.items():
            total = sum(amt for t, amt in transactions)
            if total > 1000000:
                self.high_volume_accounts.append({"account": account, "volume": total})

    def update_network_graph(self, source, destination, amount):
        if source and destination:
            self.network_graph.add_edge(source, destination, weight=amount)

    def get_forensic_report(self) -> dict:
        return {
            "timestamp": time.time(),
            "suspicious_activities": self.suspicious_activities,
            "high_volume_accounts": self.high_volume_accounts,
            "network_graph": self.network_graph
        }

    def generate_address_report(self, address: str) -> str:
        transactions = self.transaction_history.get(address, [])
        if not transactions:
            return f"No transactions found for address {address}."
        total_volume = sum(amt for t, amt in transactions)
        count = len(transactions)
        report = f"Report for {address}:\n" \
                 f"- Transactions: {count}\n" \
                 f"- Total Volume: {total_volume:.2f} XRP\n"
        suspicious = [act for act in self.suspicious_activities if act.get("account") == address]
        if suspicious:
            report += "- Suspicious Activities:\n"
            for act in suspicious:
                typ = act.get("type", "UNKNOWN")
                ts = datetime.fromtimestamp(act.get("timestamp", time.time())).strftime("%Y-%m-%d %H:%M:%S")
                report += f"   * {typ} at {ts}\n"
        else:
            report += "- No suspicious activities detected.\n"
        return report

    def forensic_ai_response(self, question: str) -> str:
        responses = [
            "Based on my forensic analysis, the activity appears normal.",
            "There are some anomalies – please check the transaction frequency.",
            "Certain addresses show signs of suspicious behavior.",
            "Recent transactions indicate possible manipulation.",
            "The transaction volumes are average for this segment."
        ]
        return random.choice(responses) + f" (Question: {question})"

# -------------------- Interface principale (GUI + CLI + Forensic) --------------------
class QuantumGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Neural Processor Dashboard")
        self.geometry("1200x800")
        self.configure(bg="white")
        self.processor = QuantumProcessor(n_qubits=8, mode="hybrid")
        self.current_circuit = None
        self.mode_var = tk.StringVar(value="hybrid")
        self.forensic_monitor = XRPLForensicMonitor(hybrid_client=None)
        self.show_splash_animation()

    # ---------- Splash Screen (affichage d'un "0" fin et noir) ----------
    def show_splash_animation(self):
        self.splash_canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.splash_canvas.pack(fill="both", expand=True)
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        self.start_time = time.time()
        self.base_scale = 50
        self.amplitude = 1   # Variation de 49 à 51 pour un effet très discret
        self.splash_text = self.splash_canvas.create_text(
            width // 2, height // 2,
            text="0",
            font=("Helvetica", self.base_scale, "normal"),
            fill="black"
        )
        self.animate_splash()
        self.after(3000, self.destroy_splash)

    def animate_splash(self):
        if not self.splash_canvas.winfo_exists():
            return
        elapsed = time.time() - self.start_time
        scale = self.base_scale + self.amplitude * math.sin(2 * math.pi * elapsed / 2.0)
        try:
            self.splash_canvas.itemconfig(self.splash_text, font=("Helvetica", int(scale), "normal"))
        except tk.TclError:
            return
        self.after(50, self.animate_splash)

    def destroy_splash(self):
        if self.splash_canvas.winfo_exists():
            self.splash_canvas.destroy()
        self.initialize_main_interface()

    # ---------- Initialisation de l'interface principale avec onglets ----------
    def initialize_main_interface(self):
        self.configure(bg="white")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 10), padding=6)

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)

        header_label = ttk.Label(main_frame, text="Quantum Neural Processor Dashboard", font=("Helvetica", 18, "bold"))
        header_label.pack(pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=10)

        # Création des onglets classiques
        self.operations_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.circuit_tab = ttk.Frame(self.notebook)
        self.cli_tab = ttk.Frame(self.notebook)
        self.qa_tab = ttk.Frame(self.notebook)
        # Nouvel onglet Forensic
        self.forensic_tab = tk.Frame(self.notebook, bg="black")

        self.notebook.add(self.operations_tab, text="Operations")
        self.notebook.add(self.results_tab, text="Results")
        self.notebook.add(self.monitoring_tab, text="Monitoring")
        self.notebook.add(self.circuit_tab, text="Circuit Visualization")
        self.notebook.add(self.cli_tab, text="CLI")
        self.notebook.add(self.qa_tab, text="Q&A")
        self.notebook.add(self.forensic_tab, text="Forensic")

        self.setup_operations_tab()
        self.setup_results_tab()
        self.setup_monitoring_tab()
        self.setup_circuit_tab()
        self.setup_cli_tab()
        self.setup_qa_tab()
        self.setup_forensic_tab()

    def setup_operations_tab(self):
        label = ttk.Label(self.operations_tab, text="Operations functionalities will be displayed here.", font=("Helvetica", 14))
        label.pack(pady=20)

    def setup_results_tab(self):
        label = ttk.Label(self.results_tab, text="Results will be displayed here.", font=("Helvetica", 14))
        label.pack(pady=20)

    def setup_monitoring_tab(self):
        self.monitor_text = tk.Text(self.monitoring_tab, height=10, font=("Helvetica", 12))
        self.monitor_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_monitoring()

    def setup_circuit_tab(self):
        self.circuit_canvas = tk.Canvas(self.circuit_tab, bg="white")
        self.circuit_canvas.pack(fill="both", expand=True)
        self.draw_placeholder_circuit()

    def draw_placeholder_circuit(self):
        self.circuit_canvas.create_rectangle(50, 50, 300, 200, outline="black", width=2)
        self.circuit_canvas.create_text(175, 125, text="Quantum Circuit Placeholder", font=("Helvetica", 12, "italic"), fill="black")

    # ---------- CLI Tab (initialisation, création, exécution, mesure et Q&A) ----------
    def setup_cli_tab(self):
        frame = self.cli_tab
        init_frame = ttk.LabelFrame(frame, text="Initialization", padding=10)
        init_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(init_frame, text="n_qubits:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.init_n_qubits = ttk.Entry(init_frame, width=10)
        self.init_n_qubits.insert(0, "8")
        self.init_n_qubits.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(init_frame, text="mode:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.init_mode = ttk.Entry(init_frame, width=10)
        self.init_mode.insert(0, "hybrid")
        self.init_mode.grid(row=0, column=3, padx=5, pady=2)
        ttk.Button(init_frame, text="Init", command=self.cli_init).grid(row=0, column=4, padx=5, pady=2)

        status_frame = ttk.LabelFrame(frame, text="System Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(status_frame, text="Show Status", command=self.cli_status).pack(side="left", padx=5)

        circuit_frame = ttk.LabelFrame(frame, text="Create Circuit", padding=10)
        circuit_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(circuit_frame, text="Type (e.g., superposition, entanglement):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.circuit_type_entry = ttk.Entry(circuit_frame, width=20)
        self.circuit_type_entry.insert(0, "superposition")
        self.circuit_type_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(circuit_frame, text="Parameters (key=value ...):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.circuit_params_entry = ttk.Entry(circuit_frame, width=40)
        self.circuit_params_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(circuit_frame, text="Create Circuit", command=self.cli_circuit).grid(row=0, column=2, rowspan=2, padx=5, pady=2)

        run_frame = ttk.LabelFrame(frame, text="Execute Operation", padding=10)
        run_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(run_frame, text="Operation (e.g., measurement):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.run_op_entry = ttk.Entry(run_frame, width=20)
        self.run_op_entry.insert(0, "measurement")
        self.run_op_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(run_frame, text="Parameters (key=value ...):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.run_params_entry = ttk.Entry(run_frame, width=40)
        self.run_params_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(run_frame, text="Execute", command=self.cli_run).grid(row=0, column=2, rowspan=2, padx=5, pady=2)

        measure_frame = ttk.LabelFrame(frame, text="Measure Quantum State", padding=10)
        measure_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(measure_frame, text="Measure", command=self.cli_measure).pack(side="left", padx=5)

        ask_frame = ttk.LabelFrame(frame, text="Ask Hybrid AI", padding=10)
        ask_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(ask_frame, text="Question:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.ask_entry = ttk.Entry(ask_frame, width=40)
        self.ask_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(ask_frame, text="Ask", command=self.cli_ask).grid(row=0, column=2, padx=5, pady=2)

        quit_frame = ttk.Frame(frame, padding=10)
        quit_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(quit_frame, text="Exit CLI", command=self.cli_quit).pack(side="right", padx=5)

        console_frame = ttk.LabelFrame(frame, text="CLI Output", padding=10)
        console_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.cli_output = tk.Text(console_frame, height=10, font=("Helvetica", 10))
        self.cli_output.pack(fill="both", expand=True)

    def _parse_params(self, param_str: str) -> dict:
        params = {}
        for part in param_str.split():
            if '=' in part:
                key, value = part.split('=', 1)
                try:
                    params[key] = float(value)
                except ValueError:
                    params[key] = value
        return params

    def append_cli_output(self, text: str):
        self.cli_output.insert(tk.END, text + "\n")
        self.cli_output.see(tk.END)

    def cli_init(self):
        try:
            n_qubits = int(self.init_n_qubits.get())
            mode = self.init_mode.get()
            self.processor = QuantumProcessor(n_qubits=n_qubits, mode=mode)
            self.append_cli_output(f"✓ Quantum processor initialized with {n_qubits} qubits in {mode} mode.")
        except Exception as e:
            self.append_cli_output(f"✗ Initialization error: {str(e)}")

    def cli_status(self):
        status_text = "\nSystem Status:\n----------------\n"
        if self.processor:
            status_text += f"Quantum processor: Initialized\n  - Qubits: {self.processor.n_qubits}\n  - Mode: {self.processor.mode}\n"
        else:
            status_text += "Quantum processor: Not initialized\n"
        self.append_cli_output(status_text)

    def cli_circuit(self):
        if not self.processor:
            self.append_cli_output("✗ Error: Please initialize the quantum processor (use Init).")
            return
        try:
            circuit_type = self.circuit_type_entry.get().strip() or "superposition"
            params_str = self.circuit_params_entry.get().strip()
            params = self._parse_params(params_str) if params_str else {}
            circuit = self.processor.create_quantum_circuit(circuit_type, params)
            self.append_cli_output(f"\nCircuit created of type {circuit_type}:\n------------------------")
            self.append_cli_output(str(circuit))
            self.current_circuit = circuit
            self.update_circuit_visualization()
        except Exception as e:
            self.append_cli_output(f"✗ Error creating circuit: {str(e)}")

    def cli_run(self):
        if not self.processor:
            self.append_cli_output("✗ Error: Please initialize the quantum processor (use Init).")
            return
        try:
            op_type = self.run_op_entry.get().strip() or "measurement"
            params_str = self.run_params_entry.get().strip()
            params = self._parse_params(params_str) if params_str else {}
            result = self.processor.execute_quantum_operation(op_type, params)
            self.append_cli_output("\nOperation result:\n------------------------")
            self.append_cli_output(str(result))
        except Exception as e:
            self.append_cli_output(f"✗ Error executing operation: {str(e)}")

    def cli_measure(self):
        if not self.processor:
            self.append_cli_output("✗ Error: Please initialize the quantum processor (use Init).")
            return
        try:
            result = self.processor.measure_quantum_state()
            self.append_cli_output("\nMeasurement result:\n---------------------")
            for state, prob in result.items():
                self.append_cli_output(f"|{state}⟩ : {prob:.4f}")
        except Exception as e:
            self.append_cli_output(f"✗ Error measuring quantum state: {str(e)}")

    def cli_ask(self):
        question = self.ask_entry.get().strip()
        if not question:
            self.append_cli_output("Please type a question.")
            return
        answer = f"Simulated AI response to: {question}"
        self.append_cli_output("\nQuestion:")
        self.append_cli_output(question)
        self.append_cli_output("Answer:")
        self.append_cli_output(answer)

    def cli_quit(self):
        self.append_cli_output("Exiting CLI. Clearing output.")
        self.cli_output.delete("1.0", tk.END)

    # ---------- Q&A Tab ----------
    def setup_qa_tab(self):
        frame = self.qa_tab
        self.qa_output = tk.Text(frame, height=15, font=("Helvetica", 10))
        self.qa_output.pack(fill="both", expand=True, padx=10, pady=10)
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(input_frame, text="Your question:").pack(side="left", padx=5)
        self.qa_entry = ttk.Entry(input_frame, width=60)
        self.qa_entry.pack(side="left", padx=5)
        ttk.Button(input_frame, text="Send", command=self.qa_ask).pack(side="left", padx=5)

    def qa_ask(self):
        question = self.qa_entry.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please type a question.")
            return
        self.qa_output.insert(tk.END, f"You: {question}\n")
        answer = f"Simulated AI response to: {question}"
        self.qa_output.insert(tk.END, f"AI: {answer}\n\n")
        self.qa_output.see(tk.END)
        self.qa_entry.delete(0, tk.END)

    # ---------- Visualisation du Circuit ----------
    def update_circuit_visualization(self):
        if self.current_circuit:
            try:
                figure = qiskit_viz.circuit_drawer(self.current_circuit, output='mpl', style={'backgroundcolor': 'white'})
                if hasattr(self, 'viz_canvas_widget'):
                    self.viz_canvas_widget.get_tk_widget().destroy()
                self.viz_canvas_widget = FigureCanvasTkAgg(figure, self.circuit_canvas)
                self.viz_canvas_widget.draw()
                self.viz_canvas_widget.get_tk_widget().pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Visualization error", f"An error occurred while visualizing the circuit:\n{str(e)}")

    # ---------- Onglet Forensic (entièrement en noir et blanc) ----------
    def setup_forensic_tab(self):
        # Configuration du fond noir pour cet onglet
        self.forensic_tab.configure(bg="black")
        # En-tête
        header = tk.Label(self.forensic_tab, text="XRPL Forensic Analysis", font=("Helvetica", 16, "bold"),
                          bg="black", fg="white")
        header.pack(pady=10)
        # Bouton de rafraîchissement
        refresh_btn = tk.Button(self.forensic_tab, text="Refresh Forensic Data", command=self.refresh_forensic_data,
                                font=("Courier", 12), bg="black", fg="white", activebackground="gray")
        refresh_btn.pack(pady=5)
        # Cadre des listes : activités suspectes et comptes à fort volume
        list_frame = tk.Frame(self.forensic_tab, bg="black")
        list_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(list_frame, text="Suspicious Activities:", font=("Courier", 12),
                 bg="black", fg="white").pack(anchor="w")
        self.suspicious_list = tk.Listbox(list_frame, height=8, font=("Courier", 10),
                                           bg="black", fg="white", selectbackground="gray")
        self.suspicious_list.pack(fill="x", pady=5)
        tk.Label(list_frame, text="High Volume Accounts:", font=("Courier", 12),
                 bg="black", fg="white").pack(anchor="w")
        self.high_volume_list = tk.Listbox(list_frame, height=8, font=("Courier", 10),
                                            bg="black", fg="white", selectbackground="gray")
        self.high_volume_list.pack(fill="x", pady=5)
        # Paneau "Track Address" en noir et blanc
        track_frame = tk.LabelFrame(self.forensic_tab, text="Track Address", font=("Courier", 12, "bold"),
                                    bg="black", fg="white", relief="solid", bd=1)
        track_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(track_frame, text="Address:", font=("Courier", 12), bg="black", fg="white")\
            .grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.track_address_entry = tk.Entry(track_frame, font=("Courier", 12), bg="black", fg="white",
                                            insertbackground="white", width=40)
        self.track_address_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(track_frame, text="Track", font=("Courier", 12), bg="black", fg="white",
                  command=self.track_address).grid(row=0, column=2, padx=5, pady=2)
        self.address_report_text = tk.Text(track_frame, height=6, font=("Courier", 10),
                                           bg="black", fg="white")
        self.address_report_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        # Paneau "Forensic Q&A"
        qa_frame = tk.LabelFrame(self.forensic_tab, text="Forensic Q&A", font=("Courier", 12, "bold"),
                                 bg="black", fg="white", relief="solid", bd=1)
        qa_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(qa_frame, text="Your question:", font=("Courier", 12), bg="black", fg="white")\
            .grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.forensic_qa_entry = tk.Entry(qa_frame, font=("Courier", 12), bg="black", fg="white",
                                          insertbackground="white", width=40)
        self.forensic_qa_entry.grid(row=0, column=1, padx=5, pady=2)
        tk.Button(qa_frame, text="Ask", font=("Courier", 12), bg="black", fg="white",
                  command=self.forensic_qa_ask).grid(row=0, column=2, padx=5, pady=2)
        self.forensic_qa_output = tk.Text(qa_frame, height=6, font=("Courier", 10),
                                           bg="black", fg="white")
        self.forensic_qa_output.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        # Visualisation (Network Graph) en noir & blanc
        graph_frame = tk.Frame(self.forensic_tab, bg="black")
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.fig = plt.Figure(figsize=(5, 3), dpi=100, facecolor="black")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("black")
        self.forensic_canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.forensic_canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh_forensic_data(self):
        async def simulate_transactions():
            for _ in range(5):
                tx = {
                    "Account": f"rAccount{random.randint(1,100)}",
                    "Destination": f"rAccount{random.randint(1,100)}",
                    "Amount": random.randint(1, 2000000)
                }
                await self.forensic_monitor.analyze_transaction(tx)
                await asyncio.sleep(0.1)
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=lambda: loop.run_until_complete(simulate_transactions()))
        t.start()
        t.join()
        report = self.forensic_monitor.get_forensic_report()
        self.suspicious_list.delete(0, tk.END)
        for act in report.get("suspicious_activities", []):
            txt = f"{act.get('type')} - {act.get('account')}"
            self.suspicious_list.insert(tk.END, txt)
        self.high_volume_list.delete(0, tk.END)
        for acc in report.get("high_volume_accounts", []):
            txt = f"Account: {acc.get('account')} - Volume: {acc.get('volume'):.2f} XRP"
            self.high_volume_list.insert(tk.END, txt)
        # Optimisation de la visualisation du graphe réseau en noir et blanc
        self.ax.clear()
        graph = report["network_graph"]
        if graph and len(graph.nodes()) > 0:
            pos = nx.spring_layout(graph, seed=42)
            edge_widths = []
            for (u, v, d) in graph.edges(data=True):
                weight = d.get("weight", 1)
                edge_widths.append(max(1, weight / 500))
            nx.draw_networkx_nodes(graph, pos, ax=self.ax, node_color="white", node_size=600)
            nx.draw_networkx_edges(graph, pos, ax=self.ax, edge_color="white", width=edge_widths)
            nx.draw_networkx_labels(graph, pos, ax=self.ax, font_color="white", font_size=9)
        else:
            self.ax.text(0.5, 0.5, "No connections", horizontalalignment='center',
                         verticalalignment='center', transform=self.ax.transAxes,
                         fontsize=12, color="white")
        self.ax.axis("off")
        self.forensic_canvas.draw()

    def track_address(self):
        address = self.track_address_entry.get().strip()
        if not address:
            messagebox.showerror("Error", "Please enter an address to track.")
            return
        report = self.forensic_monitor.generate_address_report(address)
        self.address_report_text.delete("1.0", tk.END)
        self.address_report_text.insert(tk.END, report)

    def forensic_qa_ask(self):
        question = self.forensic_qa_entry.get().strip()
        if not question:
            messagebox.showerror("Error", "Please enter a forensic question.")
            return
        answer = self.forensic_monitor.forensic_ai_response(question)
        self.forensic_qa_output.delete("1.0", tk.END)
        self.forensic_qa_output.insert(tk.END, answer)

    # ---------- Mise à jour du panneau de monitoring ----------
    def update_monitoring(self):
        try:
            usage = self.processor.get_resource_usage()
            info = (f"CPU Usage: {usage.get('cpu', 'N/A')}%\n"
                    f"Memory Usage: {usage.get('memory', 'N/A')}%\n"
                    f"Qubits: {usage.get('qubits', 'N/A')}\n"
                    f"Mode: {usage.get('mode', 'N/A')}")
            self.monitor_text.delete("1.0", tk.END)
            self.monitor_text.insert(tk.END, info)
        except Exception as e:
            self.monitor_text.delete("1.0", tk.END)
            self.monitor_text.insert(tk.END, f"Monitoring Error: {str(e)}")
        self.after(2000, self.update_monitoring)

    # ---------- Exécution de l'application ----------
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = QuantumGUI()
    app.run()
