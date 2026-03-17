import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

from src.config import resource_path

from src.database import init_db, registrar_impressao, buscar_historico, obter_proximo_epc
from services.printer_service import listar_impressoras, imprimir
from services.zpl_service import montar_zpl
from services.preview_service import gerar_preview


class AppRFID(ctk.CTk):

    def __init__(self):
        super().__init__()

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
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=20,
            fg_color="white",
            segmented_button_selected_color="#1A73E8"
        )

        self.tabview.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.tab_print = self.tabview.add("Emissão de Etiquetas")
        self.tab_history = self.tabview.add("Histórico Etiquetas")
        self.setup_aba_impressao()
        self.setup_aba_historico()

    # ABA IMPRESSÃO
    def setup_aba_impressao(self):
        self.tab_print.grid_columnconfigure(0, weight=4)
        self.tab_print.grid_columnconfigure(1, weight=6)
        form_card = ctk.CTkFrame(self.tab_print, fg_color="#F8F9FA", corner_radius=15)
        form_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.fields = {}
        fields_data = [
            ("EPC RFID", f"{self.epc_inicial}", "epc"),
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
            form_card,
            text="IMPRIMIR ETIQUETA",
            height=65,
            font=("Segoe UI", 18, "bold"),
            fg_color="#28A745",
            hover_color="#218838",
            corner_radius=10,
            command=self.imprimir_e_incrementar
        )
        self.btn_print.pack(fill="x", pady=(25, 10), padx=25)

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
                height=65,
                font=("Segoe UI", 18, "bold"),
                corner_radius=10,
                fg_color="transparent",
                text_color="#1A73E8",
                hover_color="#E8F0F3",
                image=atualizar_icon,
                command=self.gerar_preview
            )
            self.btn_preview.pack(fill="x", pady=(25,10), padx=25)
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
        columns = ("id", "data", "epc", "campo1", "campo2", "campo3", "campo4")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")

        headings = {
            "id": "ID",
            "data": "Data/Hora",
            "epc": "EPC",
            "campo1": "Campo 1",
            "campo2": "Campo 2",
            "campo3": "Campo 3",
            "campo4": "Campo 4"
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col != "data" else 150, anchor="center")
        self.tree.pack(expand=True, fill="both")
        self.atualizar_tabela_historico()

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
                v["ex4"]
            )
            if v["epc"].isdigit():
                self.fields["epc"].delete(0, "end")
                self.fields["epc"].insert(0, str(int(v["epc"]) + 1))

            self.atualizar_tabela_historico()
            self.gerar_preview()
            self.lbl_status.configure(text=f"✅ Sucesso: EPC {v['epc']} registrado.")

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