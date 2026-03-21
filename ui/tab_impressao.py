import customtkinter as ctk
from tkinter import messagebox
from PIL import ImageTk, Image
import os

from services.printer_service import imprimir
from services.database import registrar_impressao
from services.zpl_service import montar_zpl, gerar_epc
from services.preview_service import gerar_preview as gerar_preview_img
from services.ativo_service import registrar_ativo
from src.config import resource_path
from services.database import init_db


class TabImpressao:
    def __init__(self, parent, app):
        self.app = app
        self.frame = parent
        self.zpl_gerado = None
        init_db()

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=4)
        self.frame.grid_columnconfigure(1, weight=6)

        self.fields = {}

        self.build_form()
        self.build_preview()

        self.gerar_preview()

    # ------------------------
    # FORMULÁRIO
    # ------------------------
    def build_form(self):
        self.frame.grid_columnconfigure(0, weight=4)
        self.frame.grid_columnconfigure(1, weight=6)
        form = ctk.CTkFrame(self.frame, fg_color="#F8F9FA", corner_radius=15)
        form.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        form.grid_columnconfigure(0, weight=1)

        fields_data = [
            ("EPC RFID:", f"{self.app.epc_inicial}", "epc", "entry"),
            ("Descrição:", "PALETEIRA PLT-DC-001", "descricao", "entry"),
            ("Patrimônio:", "0001", "patrimonio", "entry"),
            ("Tipo:", ["DIVERSOS", "EMPILHADEIRA", "ESCADA", "MÁQUINA", "PALETEIRA", "PLATAFORMA", "TRANSPALETEIRA"], "tipo", "combo"),
            ("Unidade:", ["Dores de Campos", "Oliveira", "Capitão Eneas"], "unidade", "combo"),
            ("Status:", ["ATIVO", "DANIFICADO", "MANUTENÇÃO", "DESCARTADO"], "status", "combo")
        ]

        for label, default, key, tipo in fields_data:
            ctk.CTkLabel(form, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=25, pady=(12, 0))

            if tipo == "entry":
                widget = ctk.CTkEntry(form, height=38, corner_radius=8, border_color="#D1D5DB")
                widget.insert(0, default)
                widget.bind("<Return>", lambda e: self.gerar_preview())
            elif tipo == "combo":
                widget = ctk.CTkComboBox(form, values=default)
                widget.set(default[0])
                widget.configure(command=lambda _: self.gerar_preview())

            widget.pack(fill="x", padx=25, pady=2)
            self.fields[key] = widget

        ctk.CTkButton(
            form,
            text="IMPRIMIR ETIQUETA",
            height=50,
            font=("Segoe UI", 18, "bold"),
            fg_color="#28A745",
            hover_color="#218838",
            corner_radius=10,
            command=self.imprimir
        ).pack(pady=(10, 5), padx=25, fill="x")

        atualizar_icone_path = resource_path("assets/icon/atualizar.png")
        if os.path.exists(atualizar_icone_path):
            icon_img_atualizar = Image.open(atualizar_icone_path)
            atualizar_icon = ctk.CTkImage(
                light_image=icon_img_atualizar,
                dark_image=icon_img_atualizar,
                size=(25,25)
            )

            ctk.CTkButton(
                form,
                text="Atualizar Preview",
                height=50,
                font=("Segoe UI", 18, "bold"),
                corner_radius=10,
                fg_color="transparent",
                text_color="#1A73E8",
                hover_color="#E8F0F3",
                image=atualizar_icon,
                command=self.gerar_preview
            ).pack(fill="x", pady=(10, 5), padx=25)
        else:
            ctk.CTkButton(
                form,
                text="Atualizar Preview",
                fg_color="transparent",
                text_color="#1A73E8",
                hover_color="#E8F0FE",
                command=self.gerar_preview
            ).pack(pady=5)

    # ------------------------
    # PREVIEW
    # ------------------------
    def build_preview(self):
        preview_frame = ctk.CTkFrame(self.frame, fg_color="#E9ECEF", corner_radius=15)
        preview_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(
            preview_frame,
            text="PRÉ-VISUALIZAÇÃO DA ETIQUETA",
            font=("Segoe UI", 11, "bold"),
            text_color="#666"
        ).pack(pady=10)

        self.lbl_preview = ctk.CTkLabel(preview_frame, text="")
        self.lbl_preview.pack(expand=True, padx=20, pady=20)

    def gerar_preview(self):
        v = self._get_values()
        epc = gerar_epc(v["patrimonio"], v["epc"])

        zpl = montar_zpl(
            self.app.conf_width_mm.get(),
            self.app.conf_height_mm.get(),
            int(self.app.conf_dpi.get()),
            epc,
            v
        )
        self.zpl_gerado = zpl

        print("ZPL GERADO:", zpl)

        img = gerar_preview_img(
            zpl,
            self.app.conf_width_mm.get(),
            self.app.conf_height_mm.get()
        )

        print("IMG:", img)

        photo = ImageTk.PhotoImage(img)
        self.lbl_preview.configure(image=photo)
        self.lbl_preview.image = photo

    # ------------------------
    # IMPRIMIR
    # ------------------------
    def imprimir(self):
        v = self._get_values()

        erro = self._validar_campos(v)
        if erro:
            messagebox.showerror("Erro", erro)
            return

        try:
            printer = self.app.printer_var.get()

            epc = gerar_epc(v["patrimonio"], v["epc"])

            zpl = montar_zpl(
                self.app.conf_width_mm.get(),
                self.app.conf_height_mm.get(),
                int(self.app.conf_dpi.get()),
                epc,
                v
            )

            imprimir(printer, zpl)

            registrar_impressao(
                epc,
                v["descricao"],
                v["patrimonio"],
                v["tipo"],
                v["unidade"],
                v["status"]
            )
            if v["epc"].isdigit():
                self.fields["epc"].delete(0, "end")
                self.fields["epc"].insert(0, str(int(v["epc"]) + 1))

            registrar_ativo(
                epc=epc,
                descricao=v["descricao"],
                patrimonio=v["patrimonio"],
                unidade=v["unidade"].upper(),
                tipo=v["tipo"].upper(),
                status=v["status"].upper()
            )

            messagebox.showinfo("Sucesso", "Etiqueta impressa com sucesso!")
            self.app.historico.atualizar_tabela_historico()
            self.gerar_preview()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ------------------------
    # UTIL
    # ------------------------
    def _get_values(self):
        return {k: e.get() for k, e in self.fields.items()}

    def _validar_campos(self, v):
        obrigatorios = ["epc", "descricao", "patrimonio"]

        for campo in obrigatorios:
            if not v[campo]:
                return f"O campo '{campo}' é obrigatório"

        return None
    
    def atualizar_tamanho(self, valor):
        self.tamanho_atual = valor
        self.gerar_preview()