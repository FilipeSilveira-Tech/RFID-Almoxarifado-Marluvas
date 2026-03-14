import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import requests
import io
import os
import win32print
import sqlite3
from datetime import datetime
import sys

# Configurações de Tema
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AppRFID(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RFID Almoxarifado Marluvas - v1.0")
        self.geometry("1280x850")

        self.init_db()

        self.conf_width_mm = ctk.StringVar(value="95")
        self.conf_height_mm = ctk.StringVar(value="25")
        self.conf_dpi = ctk.StringVar(value="8")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()
        self.gerar_preview()

    def init_db(self):
        # O banco de dados NÃO usa resource_path porque ele deve ser criado
        # na pasta onde o executável está, para os dados persistirem.
        conn = sqlite3.connect("historico_rfid.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS impressoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                epc TEXT,
                produto TEXT,
                patrimonio TEXT,
                setor TEXT,
                responsavel TEXT
            )
        """)
        conn.commit()
        conn.close()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#F2F4F7")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(pady=(30, 10), padx=10)

        logo_path = resource_path("assets/logo2.png")

        if os.path.exists(logo_path):
            try:
                img_data = Image.open(logo_path)
                largura_sidebar = 240
                proporcao = largura_sidebar / float(img_data.size[0])
                altura_ajustada = int(float(img_data.size[1]) * proporcao)

                self.logo_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(largura_sidebar, altura_ajustada))

                self.logo_label = ctk.CTkLabel(self.brand_frame, image=self.logo_img, text="")
                self.logo_label.pack()
            except Exception as e:
                ctk.CTkLabel(self.brand_frame, text="RFID MARLUVAS", font=("Montserrat", 24, "bold")).pack()
        else:
            ctk.CTkLabel(self.brand_frame, text="RFID MARLUVAS", font=("Montserrat", 24, "bold")).pack()

        ctk.CTkLabel(self.sidebar, text="🖨️ DISPOSITIVO", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30)
        self.combo_printers = ctk.CTkComboBox(self.sidebar, values=self.get_printers(), width=220, fg_color="white")
        self.combo_printers.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar, text="📏 Tamanho Etiqueta", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30,
                                                                                         pady=(15, 0))
        self.combo_presets = ctk.CTkComboBox(self.sidebar, values=["95x25 mm", "100x50 mm"],
                                             command=self.aplicar_preset, width=220, fg_color="white")
        self.combo_presets.set("95x25 mm")
        self.combo_presets.pack(pady=5, padx=20)

        self.load_signature()

    def load_signature(self):
        sig_path = resource_path("assets/assinatura_transparente.png")

        if os.path.exists(sig_path):
            try:
                sig_img = Image.open(sig_path)
                sig_img.thumbnail((150, 60))
                self.img_sig = ImageTk.PhotoImage(sig_img)

                sig_label = ctk.CTkLabel(self.sidebar, image=self.img_sig, text="")
                sig_label.pack(side="bottom", pady=30)
                ctk.CTkLabel(self.sidebar, text="Developed by:", font=("Segoe UI", 9), text_color="gray").pack(
                    side="bottom")
            except Exception as e:
                print(f"Erro ao carregar assinatura: {e}")

    def create_main_area(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=20, fg_color="white",
                                      segmented_button_selected_color="#1A73E8")
        self.tabview.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.tab_print = self.tabview.add("📦 Emissão de Etiquetas")
        self.tab_history = self.tabview.add("📋 Histórico Etiquetas")

        self.setup_aba_impressao()
        self.setup_aba_historico()

    def setup_aba_impressao(self):
        self.tab_print.grid_columnconfigure(0, weight=4)
        self.tab_print.grid_columnconfigure(1, weight=6)

        form_card = ctk.CTkFrame(self.tab_print, fg_color="#F8F9FA", corner_radius=15)
        form_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.fields = {}
        fields_data = [
            ("EPC RFID", "10001", "epc"),
            ("Campo 1", "Bota Marluvas", "ex1"),
            ("Campo 2", "PAT-MAR-001", "ex2"),
            ("Campo 3", "ALMOX-01", "ex3"),
            ("Campo 4", "SISTEMA", "ex4")
        ]

        for label, default, key in fields_data:
            ctk.CTkLabel(form_card, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(12, 0))
            entry = ctk.CTkEntry(form_card, height=38, corner_radius=8, border_color="#D1D5DB")
            entry.insert(0, default)
            entry.pack(fill="x", padx=25, pady=2)
            self.fields[key] = entry

        self.btn_print = ctk.CTkButton(
            form_card, text="IMPRIMIR ETIQUETA", height=65, font=("Segoe UI", 18, "bold"),
            fg_color="#28A745", hover_color="#218838", corner_radius=10, command=self.imprimir_e_incrementar
        )
        self.btn_print.pack(fill="x", pady=(25, 10), padx=25)

        ctk.CTkButton(form_card, text="🔄 Atualizar Preview", fg_color="transparent", text_color="#1A73E8",
                      hover_color="#E8F0FE", command=self.gerar_preview).pack(pady=5)

        preview_card = ctk.CTkFrame(self.tab_print, fg_color="#E9ECEF", corner_radius=15)
        preview_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(preview_card, text="PRÉ-VISUALIZAÇÃO DA ETIQUETA", font=("Segoe UI", 11, "bold"),
                     text_color="#666").pack(pady=10)
        self.lbl_preview = ctk.CTkLabel(preview_card, text="")
        self.lbl_preview.pack(expand=True, padx=20, pady=20)

    def setup_aba_historico(self):
        self.tree_frame = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        self.tree_frame.pack(expand=True, fill="both", padx=10, pady=10)

        columns = ("id", "data", "epc", "prod", "pat", "setor")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")

        headings = {"id": "ID", "data": "Data/Hora", "epc": "EPC", "prod": "Produto", "pat": "Patrimônio",
                    "setor": "Setor"}
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col != "data" else 150, anchor="center")

        self.tree.pack(expand=True, fill="both")
        self.atualizar_tabela_historico()

    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=35, fg_color="#F2F4F7", corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.lbl_status = ctk.CTkLabel(self.status_bar, text="🟢 Pronto para impressão", font=("Segoe UI", 11))
        self.lbl_status.pack(side="left", padx=25)

    def montar_zpl(self):
        dpi = int(self.conf_dpi.get())
        # PW = Largura em dots, LL = Altura em dots
        pw = int(float(self.conf_width_mm.get()) * dpi)
        ll = int(float(self.conf_height_mm.get()) * dpi)

        v = {k: ent.get().upper() for k, ent in self.fields.items()}

        # --- LÓGICA DO SUPER EPC (24 CARACTERES HEX) ---
        prefixo = "4D41"  # MARL em Hex
        # Pega apenas números do campo patrimônio para compor o código do produto
        cod_item = "".join(filter(str.isdigit, v['ex2'])).zfill(6)
        serial = "".join(filter(str.isdigit, v['epc'])).zfill(14)

        epc_final = (prefixo + cod_item + serial)[:24]
        # -----------------------------------------------

        # Ajuste de Layout Baseado na Altura (LL)
        if ll <= 250:  # Etiquetas pequenas (25mm)
            zpl = f"""^XA^PW{pw}^LL{ll}^CI28
^CF0,30^FO50,35^FD{v['ex1']}^FS
^CF0,22^FO50,75^FD{v['ex2']}^FS
^CF0,20^FO50,115^FDSETOR: {v['ex3']}^FS
^CF0,20^FO50,145^FDRESP: {v['ex4']}^FS
^FO50,175^A0N,18,18^FDID: {epc_final}^FS
^FO{pw - 130},40^BQN,2,4^FDQA,{epc_final}^FS
^RS8,,,1^RFW,H^FD{epc_final}^FS^XZ"""
        else:  # Etiquetas Grandes (50mm ou mais)
        # Aqui aumentamos as distâncias e o tamanho do QR Code
            zpl = f"""^XA^PW{pw}^LL{ll}^CI28
^CF0,40^FO50,60^FD{v['ex1']}^FS
^CF0,30^FO50,120^FD{v['ex2']}^FS
^CF0,25^FO50,180^FDSETOR: {v['ex3']}^FS
^CF0,25^FO50,230^FDRESP: {v['ex4']}^FS
^CF0,20^FO50,300^FDID EPC:^FS
^CF0,22^FO50,330^FD{epc_final}^FS
^FO{pw - 220},100^BQN,2,7^FDQA,{epc_final}^FS
^RS8,,,1^RFW,H^FD{epc_final}^FS^XZ"""

        return zpl

    def gerar_preview(self):
        zpl = self.montar_zpl()
        w_in, h_in = float(self.conf_width_mm.get()) / 25.4, float(self.conf_height_mm.get()) / 25.4
        try:
            res = requests.get(f"http://api.labelary.com/v1/printers/8dpmm/labels/{w_in:.2f}x{h_in:.2f}/0/{zpl}",
                               timeout=5)
            img = Image.open(io.BytesIO(res.content))
            img.thumbnail((500, 250))
            photo = ImageTk.PhotoImage(img)
            self.lbl_preview.configure(image=photo)
            self.lbl_preview.image = photo
        except:
            pass

    def atualizar_tabela_historico(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = sqlite3.connect("historico_rfid.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, data_hora, epc, produto, patrimonio, setor FROM impressoes ORDER BY id DESC")
        for r in cursor.fetchall(): self.tree.insert("", "end", values=r)
        conn.close()

    def imprimir_e_incrementar(self):
        v = {k: ent.get() for k, ent in self.fields.items()}
        try:
            p = self.combo_printers.get()
            h = win32print.OpenPrinter(p)
            win32print.StartDocPrinter(h, 1, ("RFID-Marluvas", None, "RAW"))
            win32print.WritePrinter(h, self.montar_zpl().encode("utf-8"))
            win32print.EndDocPrinter(h)
            win32print.ClosePrinter(h)

            conn = sqlite3.connect("historico_rfid.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO impressoes (data_hora, epc, produto, patrimonio, setor, responsavel) VALUES (?,?,?,?,?,?)",
                (datetime.now().strftime("%d/%m/%Y %H:%M"), v['epc'], v['ex1'], v['ex2'], v['ex3'], v['ex4']))
            conn.commit();
            conn.close()

            if v['epc'].isdigit():
                self.fields["epc"].delete(0, "end")
                self.fields["epc"].insert(0, str(int(v['epc']) + 1))

            self.atualizar_tabela_historico()
            self.gerar_preview()
            self.lbl_status.configure(text=f"✅ Sucesso: EPC {v['epc']} registrado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def get_printers(self):
        return [p[2] for p in win32print.EnumPrinters(2)] or ["Sem Impressora"]

    def aplicar_preset(self, e):
        if e == "95x25 mm":
            self.conf_width_mm.set("95");
            self.conf_height_mm.set("25")
        else:
            self.conf_width_mm.set("100");
            self.conf_height_mm.set("50")
        self.gerar_preview()


if __name__ == "__main__":
    app = AppRFID()
    app.mainloop()