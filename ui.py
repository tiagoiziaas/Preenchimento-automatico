# preenchimento_app/ui.py
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from datasource import load_table
from mapper import start_mapping
from runner import run_automation


class AutomationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Preenchimento Automático")
        self.geometry("1020x640")
        self.minsize(980, 600)

        self.file_path = tk.StringVar()
        self.sheet_name = tk.StringVar()
        self.url = tk.StringVar()
        self.delay_ms = tk.IntVar(value=250)
        self.loop_all = tk.BooleanVar(value=True)
        self.row_index = tk.IntVar(value=1)

        self.headers = []
        self.rows = []
        self.mapping = []
        self.status_text = tk.StringVar(value="Pronto.")

        self._setup_theme()
        self._build_layout()

    def _setup_theme(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", padding=(12, 8))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_layout(self):
        header = ttk.Frame(self, padding=(14, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Preenchimento Automático", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="  |  Shift+Clique = Fill  •  Ctrl+Clique = Click", foreground="#555").pack(side="left")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.tab_config = ttk.Frame(self.nb, padding=12)
        self.tab_map = ttk.Frame(self.nb, padding=12)
        self.tab_run = ttk.Frame(self.nb, padding=12)

        self.nb.add(self.tab_config, text="Configuração")
        self.nb.add(self.tab_map, text="Mapeamento")
        self.nb.add(self.tab_run, text="Execução")

        self._build_config_tab()
        self._build_map_tab()
        self._build_run_tab()

        status = ttk.Frame(self, padding=(12, 8))
        status.pack(fill="x")
        ttk.Label(status, textvariable=self.status_text, foreground="#333").pack(side="left")

    def _build_config_tab(self):
        lf = ttk.LabelFrame(self.tab_config, text="Base e URL", padding=12)
        lf.pack(fill="x")
        lf.columnconfigure(1, weight=1)

        ttk.Label(lf, text="Planilha (CSV/XLSX):").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(lf, textvariable=self.file_path).grid(row=0, column=1, sticky="we", pady=6, padx=(10, 10))
        ttk.Button(lf, text="Selecionar", command=self.pick_file).grid(row=0, column=2, pady=6)

        ttk.Label(lf, text="Aba (XLSX opcional):").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(lf, textvariable=self.sheet_name, width=24).grid(row=1, column=1, sticky="w", pady=6, padx=(10, 0))

        ttk.Label(lf, text="URL:").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(lf, textvariable=self.url).grid(row=2, column=1, sticky="we", pady=6, padx=(10, 10))
        ttk.Button(lf, text="Carregar Base", command=self.load_base).grid(row=2, column=2, pady=6)

        lf2 = ttk.LabelFrame(self.tab_config, text="Parâmetros", padding=12)
        lf2.pack(fill="x", pady=(12, 0))
        lf2.columnconfigure(1, weight=1)

        ttk.Label(lf2, text="Delay por ação (ms):").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Spinbox(lf2, from_=0, to=5000, textvariable=self.delay_ms, width=10).grid(row=0, column=1, sticky="w", pady=6, padx=(10, 0))

        ttk.Checkbutton(lf2, text="Loop: percorrer todas as linhas", variable=self.loop_all, command=self._toggle_row).grid(row=1, column=1, sticky="w", pady=6, padx=(10, 0))

        ttk.Label(lf2, text="Se NÃO for loop, linha (1 = primeira linha de dados):").grid(row=2, column=0, sticky="w", pady=6)
        self.row_spin = ttk.Spinbox(lf2, from_=1, to=999999, textvariable=self.row_index, width=10)
        self.row_spin.grid(row=2, column=1, sticky="w", pady=6, padx=(10, 0))
        self._toggle_row()

    def _build_map_tab(self):
        top = ttk.Frame(self.tab_map)
        top.pack(fill="x")

        ttk.Button(top, text="Abrir Mapeamento (Browser)", command=self.start_mapping).pack(side="left")
        ttk.Button(top, text="Limpar", command=self.clear_mapping).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Salvar Mapping", command=self.save_mapping).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Carregar Mapping", command=self.load_mapping).pack(side="left", padx=(8, 0))

        hint = ttk.Label(
            self.tab_map,
            text="Dica: Shift+Clique para campos (fill) e Ctrl+Clique para botões/links (click).",
            foreground="#555"
        )
        hint.pack(anchor="w", pady=(10, 6))

        table_frame = ttk.Frame(self.tab_map)
        table_frame.pack(fill="both", expand=True)

        cols = ("action", "label", "column", "selector")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col, title in [("action", "Ação"), ("label", "Campo"), ("column", "Coluna"), ("selector", "Seletor")]:
            self.tree.heading(col, text=title)

        self.tree.column("action", width=70, anchor="center")
        self.tree.column("label", width=220)
        self.tree.column("column", width=180)
        self.tree.column("selector", width=500)

        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    def _build_run_tab(self):
        top = ttk.Frame(self.tab_run)
        top.pack(fill="x")

        ttk.Button(top, text="Executar Preenchimento", command=self.start_run).pack(side="left")

        log_frame = ttk.LabelFrame(self.tab_run, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.log = tk.Text(log_frame, height=12)
        self.log.pack(fill="both", expand=True)

    def _toggle_row(self):
        self.row_spin.configure(state="disabled" if self.loop_all.get() else "normal")

    def set_status(self, msg: str):
        self.status_text.set(msg)

    def log_print(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def pick_file(self):
        fp = filedialog.askopenfilename(filetypes=[("CSV/XLSX", "*.csv *.xlsx *.xlsm"), ("Todos", "*.*")])
        if fp:
            self.file_path.set(fp)
            self.set_status("Planilha selecionada.")

    def load_base(self):
        try:
            fp = self.file_path.get().strip()
            if not fp:
                messagebox.showerror("Erro", "Selecione uma planilha primeiro.")
                return
            headers, rows = load_table(fp, self.sheet_name.get().strip() or None)
            self.headers = headers
            self.rows = rows
            self.set_status(f"Base carregada: {len(rows)} linhas.")
            self.log_print(f"[BASE] {len(rows)} linhas | colunas: {headers}")
        except Exception as ex:
            messagebox.showerror("Erro ao carregar base", str(ex))

    def clear_mapping(self):
        self.mapping = []
        self._refresh_tree()
        self.set_status("Mapping limpo.")

    def _refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in self.mapping:
            self.tree.insert("", "end", values=(item.get("action", ""), item.get("label", ""), item.get("column", ""), item.get("selector", "")))

    def start_mapping(self):
        if not self.headers or not self.rows:
            messagebox.showerror("Erro", "Carregue a base primeiro (aba Configuração).")
            return
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Informe a URL (aba Configuração).")
            return

        self.set_status("Abrindo navegador para mapeamento...")
        self.log_print("[MAP] Abrindo navegador... Shift=FILL | Ctrl=CLICK")
        self.nb.select(self.tab_map)

        def capture_cb(payload, selector, label_guess, action):
            if payload.get("ready"):
                self.after(0, lambda: self.set_status("Mapper ativo. Use Shift/Ctrl + Clique no navegador."))
                return

            def ask_and_add():
                if action == "click":
                    self.mapping.append({"label": str(label_guess)[:60], "selector": selector, "column": "", "action": "click"})
                    self._refresh_tree()
                    self.set_status("Ação CLICK adicionada.")
                    self.log_print(f"[MAP] CLICK: {label_guess} | {selector}")
                    return

                col = simpledialog.askstring(
                    "Mapear campo (FILL)",
                    f"Campo detectado: {label_guess}\n\nQual COLUNA da planilha devo usar?\n\nColunas disponíveis:\n{', '.join(self.headers)}",
                    parent=self
                )
                if not col:
                    self.log_print("[MAP] ignorado (coluna vazia).")
                    return
                col = col.strip()
                if col not in self.headers:
                    messagebox.showerror("Coluna inválida", f"A coluna '{col}' não existe na planilha.")
                    return

                self.mapping.append({"label": str(label_guess)[:60], "selector": selector, "column": col, "action": "fill"})
                self._refresh_tree()
                self.set_status("Campo FILL adicionado.")
                self.log_print(f"[MAP] FILL: {label_guess} -> {col} | {selector}")

            self.after(0, ask_and_add)

        t = threading.Thread(target=lambda: start_mapping(url, capture_cb), daemon=True)
        t.start()

    def start_run(self):
        if not self.mapping:
            messagebox.showerror("Erro", "Você precisa mapear pelo menos um campo/ação.")
            return
        if not self.rows:
            messagebox.showerror("Erro", "Carregue a base primeiro.")
            return
        url = self.url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Informe a URL.")
            return

        self.set_status("Executando...")
        self.nb.select(self.tab_run)
        self.log_print("[RUN] Iniciando execução...")

        def worker():
            try:
                run_automation(
                    url=url,
                    mapping=self.mapping,
                    rows=self.rows,
                    delay_ms=int(self.delay_ms.get()),
                    loop_all=bool(self.loop_all.get()),
                    row_index=int(self.row_index.get()),
                    log_cb=lambda s: self.after(0, lambda s=s: self.log_print(s)),
                )
                self.after(0, lambda: self.set_status("Execução finalizada."))
                self.after(0, lambda: self.log_print("[RUN] Finalizado."))
            except Exception as ex:
                err = str(ex)
                self.after(0, lambda err=err: messagebox.showerror("Erro na execução", err))

        threading.Thread(target=worker, daemon=True).start()

    def save_mapping(self):
        if not self.mapping:
            messagebox.showerror("Erro", "Não há mapping para salvar.")
            return
        fp = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not fp:
            return

        data = {
            "url": self.url.get().strip(),
            "delay_ms": int(self.delay_ms.get()),
            "loop_all": bool(self.loop_all.get()),
            "mapping": self.mapping
        }
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.set_status("Mapping salvo.")
        self.log_print(f"[MAP] Salvo em: {fp}")

    def load_mapping(self):
        fp = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not fp:
            return

        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.url.set(data.get("url", ""))
        self.delay_ms.set(int(data.get("delay_ms", 250)))
        self.loop_all.set(bool(data.get("loop_all", True)))
        self._toggle_row()

        self.mapping = data.get("mapping", [])
        self._refresh_tree()

        self.set_status("Mapping carregado.")
        self.log_print(f"[MAP] Carregado: {fp}")