import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import json

from src.config import resource_path

from services.database import init_db, registrar_impressao, buscar_historico, obter_proximo_epc
from services.printer_service import listar_impressoras, imprimir
from services.zpl_service import montar_zpl
from services.preview_service import gerar_preview
from services.ativo_service import registrar_ativo, buscar_ativos


class AppRFID(ctk.CTk):

    def __init__(self):
        super().__init__()
        scale = self.carregar_scaling()
        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)

        self.title("RFID Almoxarifado Marluvas - v1.1.0")
        self.geometry("1280x850")

        init_db()
        self.epc_inicial = obter_proximo_epc()

        self.conf_width_mm = ctk.StringVar(value="95")
        self.conf_height_mm = ctk.StringVar(value="25")
        self.conf_dpi = ctk.StringVar(value="8")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()

        self.gerar_preview()

    # SIDEBAR
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#F2F4F7")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(pady=(30, 10), padx=10)
        logo_path = resource_path("assets/img/logo_transparente.png")

        if os.path.exists(logo_path):
            try:
                img_data = Image.open(logo_path)
                largura_sidebar = 240
                proporcao = largura_sidebar / float(img_data.size[0])
                altura_ajustada = int(float(img_data.size[1]) * proporcao)
                self.logo_img = ctk.CTkImage(
                    light_image=img_data,
                    dark_image=img_data,
                    size=(largura_sidebar, altura_ajustada)
                )
                self.logo_label = ctk.CTkLabel(self.brand_frame, image=self.logo_img, text="")
                self.logo_label.pack()
            except:
                ctk.CTkLabel(self.brand_frame, text="RFID MARLUVAS", font=("Montserrat", 24, "bold")).pack()
        else:
            ctk.CTkLabel(self.brand_frame, text="RFID MARLUVAS", font=("Montserrat", 24, "bold")).pack()

        # Área Dispotivos
        printer_icone_path = resource_path("assets/icon/imprimir.png")
        if os.path.exists(printer_icone_path):
            icon_img_print = Image.open(printer_icone_path)
            self.printer_icon = ctk.CTkImage(
                light_image=icon_img_print,
                dark_image=icon_img_print,
                size=(18,18)
            )
            ctk.CTkLabel(
                self.sidebar,
                text=" DISPOSITIVOS",
                image=self.printer_icon,
                compound="left",
                font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", padx=30)
        else:
            ctk.CTkLabel(self.sidebar, text="🖨️ DISPOSITIVO", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=30)

        self.combo_printers = ctk.CTkComboBox(
            self.sidebar,
            values=listar_impressoras(),
            width=220,
            fg_color="white"
        )
        self.combo_printers.pack(pady=5, padx=20)

        # Tamanhos Etiquetas
        etiqueta_icone_path = resource_path("assets/icon/rfid.png")
        if os.path.exists(etiqueta_icone_path):
            icon_img_rfid = Image.open(etiqueta_icone_path)
            self.rfid_icon = ctk.CTkImage(
                light_image=icon_img_rfid,
                dark_image=icon_img_rfid,
                size=(18,18)
            )
            ctk.CTkLabel(
                self.sidebar,
                text=" TAMANHO ETIQUETA",
                image=self.rfid_icon,
                compound="left",
                font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", padx=30)
        else:
            ctk.CTkLabel(self.sidebar, text="📏 Tamanho Etiqueta", font=("Segoe UI", 11, "bold")).pack(anchor="w",padx=30,pady=(15, 0))

        self.combo_presets = ctk.CTkComboBox(
            self.sidebar,
            values=["95x25 mm", "100x50 mm"],
            command=self.aplicar_preset,
            width=220,
            fg_color="white"
        )
        self.combo_presets.set("95x25 mm")
        self.combo_presets.pack(pady=5, padx=20)
        self.load_signature()

        # Controle Scaling
        ctk.CTkLabel(
            self.sidebar,
            text="Escala da Interface",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=30, pady=(15,0))

        self.combo_scaling = ctk.CTkComboBox(
            self.sidebar,
            values=["110%", "100%", "90%", "80%", "75%"],
            width=220,
            command=self.alterar_scaling
        )
        valor_atual = int(self.carregar_scaling() * 100)
        self.combo_scaling.set(f"{valor_atual}%")
        self.combo_scaling.pack(pady=5, padx=20)

    # ASSINATURA
    def load_signature(self):
        sig_path = resource_path("assets/img/assinatura.png")
        if os.path.exists(sig_path):
            try:
                sig_img = Image.open(sig_path)
                sig_img.thumbnail((150, 60))
                self.img_sig = ImageTk.PhotoImage(sig_img)

                sig_label = ctk.CTkLabel(self.sidebar, image=self.img_sig, text="")
                sig_label.pack(side="bottom", pady=30)

                ctk.CTkLabel(
                    self.sidebar,
                    text="Developed by:",
                    font=("Segoe UI", 9),
                    text_color="gray"
                ).pack(side="bottom")

            except Exception as e:
                print("Erro assinatura:", e)

    # ÁREA PRINCIPAL
    def create_main_area(self):
        width = self.winfo_width()
        height = self.winfo_height()

        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=20,
            fg_color="white",
            segmented_button_selected_color="#1A73E8"
        )


        self.tabview.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.tab_print = self.tabview.add("Emissão de Etiquetas")
        self.tab_history = self.tabview.add("Histórico Etiquetas")
        self.tab_ativos = self.tabview.add("Consulta de Ativos")
        self.setup_aba_impressao()
        self.setup_aba_historico()
        self.setup_aba_ativos()

    # ABA IMPRESSÃO
    def setup_aba_impressao(self):
        self.tab_print.grid_columnconfigure(0, weight=4)
        self.tab_print.grid_columnconfigure(1, weight=6)
        form_card = ctk.CTkFrame(self.tab_print, fg_color="#F8F9FA", corner_radius=15)
        form_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.fields = {}
        fields_data = [
            ("EPC RFID:", f"{self.epc_inicial}", "epc", "entry"),
            ("Descrição:", "Bota Marluvas", "ex1", "entry"),
            ("Patrimônio:", "6565", "ex2", "entry"),
            ("Tipo:", ["DIVERSOS", "EMPILHADEIRA", "ESCADA", "MÁQUINA", "PALETEIRA", "PLATAFORMA", "TRANSPALETEIRA"], "ex3", "combo"),
            ("Unidade", ["Dores de Campos", "Oliveira", "Capitão Eneas"], "ex4", "combo"),
            ("Status", ["ATIVO", "DANIFICADO", "MANUTENÇÃO", "DESCARTADO"], "ex5", "combo")
        ]

        for label, default, key, tipo in fields_data:
            ctk.CTkLabel(form_card, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(12, 0))

            if tipo == "entry":
                entry = ctk.CTkEntry(form_card, height=38, corner_radius=8, border_color="#D1D5DB")
                entry.insert(0, default)

            elif tipo == "combo":
                entry = ctk.CTkComboBox(
                    form_card,
                    values=default
                )
                entry.set(default[0])

            entry.pack(fill="x", padx=25, pady=2)
            self.fields[key] = entry

        self.btn_print = ctk.CTkButton(
            form_card,
            text="IMPRIMIR ETIQUETA",
            height=50,
            font=("Segoe UI", 18, "bold"),
            fg_color="#28A745",
            hover_color="#218838",
            corner_radius=10,
            command=self.imprimir_e_incrementar
        )
        self.btn_print.pack(fill="x", pady=(10, 5), padx=25)

        # Botão: ATUALIZAR PREVIEW
        atualizar_icone_path = resource_path("assets/icon/atualizar.png")
        if os.path.exists(atualizar_icone_path):
            icon_img_atualizar = Image.open(atualizar_icone_path)
            atualizar_icon = ctk.CTkImage(
                light_image=icon_img_atualizar,
                dark_image=icon_img_atualizar,
                size=(25,25)
            )

            self.btn_preview = ctk.CTkButton(
                form_card,
                text="Atualizar Preview",
                height=50,
                font=("Segoe UI", 18, "bold"),
                corner_radius=10,
                fg_color="transparent",
                text_color="#1A73E8",
                hover_color="#E8F0F3",
                image=atualizar_icon,
                command=self.gerar_preview
            )
            self.btn_preview.pack(fill="x", pady=(10, 5), padx=25)
        else:
            ctk.CTkButton(
                form_card,
                text="Atualizar Preview",
                fg_color="transparent",
                text_color="#1A73E8",
                hover_color="#E8F0FE",
                command=self.gerar_preview
            ).pack(pady=5)

        preview_card = ctk.CTkFrame(self.tab_print, fg_color="#E9ECEF", corner_radius=15)
        preview_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        ctk.CTkLabel(
            preview_card,
            text="PRÉ-VISUALIZAÇÃO DA ETIQUETA",
            font=("Segoe UI", 11, "bold"),
            text_color="#666"
        ).pack(pady=10)

        self.lbl_preview = ctk.CTkLabel(preview_card, text="")
        self.lbl_preview.pack(expand=True, padx=20, pady=20)

    # ABA HISTÓRICO
    def setup_aba_historico(self):
        self.tree_frame = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        self.tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
        columns = ("id", "data_criacao", "epc", "descricao", "patrimonio", "unidade", "tipo", "status")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")

        headings = {
            "id": "ID",
            "data_criacao": "Data/Hora",
            "epc": "EPC",
            "descricao": "Descrição",
            "patrimonio": "Patrimônio",
            "unidade": "Unidade",
            "tipo": "Tipo",
            "status": "Status"
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col != "data" else 150, anchor="center")
        self.tree.pack(expand=True, fill="both")
        self.atualizar_tabela_historico()

    def setup_aba_ativos(self):
        self.tab_ativos.grid_columnconfigure(0, weight=1)
        self.tab_ativos.grid_rowconfigure(1, weight=1)

        filtro_frame = ctk.CTkFrame(self.tab_ativos, fg_color="#F8F9FA")
        filtro_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.entry_busca = ctk.CTkEntry(filtro_frame, placeholder_text="Buscar...")
        self.entry_busca.grid(row=0, column=0, padx=10, pady=10)

        self.combo_status = ctk.CTkComboBox(
            filtro_frame,
            values=["", "ATIVO", "DANIFICADO", "MANUTENÇÃO", "DESCARTE"]
        )
        self.combo_status.grid(row=0, column=1, padx=10)

        self.combo_unidade = ctk.CTkComboBox(
            filtro_frame,
            values=["", "DORES DE CAMPOS", "OLIVEIRA", "CAPITÃO ENEAS"]
        )
        self.combo_unidade.grid(row=0, column=2, padx=10)

        ctk.CTkButton(
            filtro_frame,
            text="Buscar",
            command=self.buscar_ativo_ui
        ).grid(row=0, column=3, padx=10)

        self.tree_ativos = ttk.Treeview(
            self.tab_ativos,
            columns=("epc", "descricao", "patrimonio","tipo", "unidade", "status"),
            show="headings"
        )
        headings = {
            "epc": "EPC",
            "descricao": "Descrição",
            "patrimonio": "Patriomônio",
            "tipo": "Tipo",
            "unidade": "Unidade",
            "status": "Status"
        }

        for col, text in headings.items():
            self.tree_ativos.heading(col, text=text)
            self.tree_ativos.column(col, anchor="center", width=120)

        self.tree_ativos.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def buscar_ativo_ui(self):
        texto = self.entry_busca.get()
        status = self.combo_status.get()
        unidade = self.combo_unidade.get()

        resultados = buscar_ativos(
            filtro_texto=texto,
            status=status,
            unidade=unidade
        )
        self.atualizar_tabela_ativos(resultados)

    def atualizar_tabela_ativos(self, dados):
        for i in self.tree_ativos.get_children():
            self.tree_ativos.delete(i)

        for row in dados:
            self.tree_ativos.insert("", "end", values=row)

    # STATUS BAR
    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=35, fg_color="#F2F4F7", corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="🟢 Pronto para impressão",
            font=("Segoe UI", 11)
        )

        self.lbl_status.pack(side="left", padx=25)

    # PREVIEW
    def gerar_preview(self):
        fields = {k: ent.get() for k, ent in self.fields.items()}
        try:
            zpl = montar_zpl(
                fields,
                self.conf_width_mm.get(),
                self.conf_height_mm.get(),
                int(self.conf_dpi.get())
            )
            img = gerar_preview(
                zpl,
                self.conf_width_mm.get(),
                self.conf_height_mm.get()
            )

            photo = ImageTk.PhotoImage(img)

            self.lbl_preview.configure(image=photo)
            self.lbl_preview.image = photo

        except Exception as e:
            print("Erro preview:", e)
            self.lbl_preview.configure(
                text="Erro ao gerar preview",
                image=""
            )

    # HISTÓRICO
    def atualizar_tabela_historico(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in buscar_historico():
            self.tree.insert("", "end", values=r)

    # IMPRESSÃO

    def imprimir_e_incrementar(self):
        v = {k: ent.get() for k, ent in self.fields.items()}
        try:
            printer = self.combo_printers.get()

            zpl = montar_zpl(
                v,
                self.conf_width_mm.get(),
                self.conf_height_mm.get(),
                int(self.conf_dpi.get())
            )
            imprimir(printer, zpl)

            registrar_impressao(
                v["epc"],
                v["ex1"],
                v["ex2"],
                v["ex3"],
                v["ex4"],
                v["ex5"]
            )
            if v["epc"].isdigit():
                self.fields["epc"].delete(0, "end")
                self.fields["epc"].insert(0, str(int(v["epc"]) + 1))

            self.atualizar_tabela_historico()
            self.gerar_preview()
            self.lbl_status.configure(text=f"✅ Sucesso: EPC {v['epc']} registrado.")

            try:
                registrar_ativo(
                    epc=v["epc"],
                    descricao=v["ex1"],
                    patrimonio=v["ex2"],
                    unidade=v["ex4"].upper(),
                    tipo=v["ex3"].strip().upper(),
                    status=v["ex5"].strip().upper()
                )
                messagebox.showinfo("Sucesso", "Ativo Cadastrado")
            except Exception as e:
                messagebox.showerror("Erro", str(e))


        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # PRESET ETIQUETA
    def aplicar_preset(self, e):
        if e == "95x25 mm":
            self.conf_width_mm.set("95")
            self.conf_height_mm.set("25")
        else:
            self.conf_width_mm.set("100")
            self.conf_height_mm.set("50")

        self.gerar_preview()

    # SCALING
    def carregar_scaling(self):
        try:
            with open("config.json") as f:
                return float(json.load(f).get("scaling", 1.0))
        except:
            return 1.0

    def salvar_scaling(self, valor):
        with open("config.json", "w") as f:
            json.dump({"scaling": valor}, f)

    def alterar_scaling(self, valor):
        scale = int(valor.replace("%", "")) / 100

        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)
        self.salvar_scaling(scale)