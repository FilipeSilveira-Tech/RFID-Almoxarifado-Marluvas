import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image

from services.ativo_service import buscar_ativos
from services.database import buscar_historico
from services.export_service import export_para_excel
from src.config import resource_path

class TabAtivos:
    def __init__(self, parent, app):
        self.app = app
        self.frame = parent

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        filtro_frame = ctk.CTkFrame(parent, fg_color="#F8F9FA")
        filtro_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.entry_busca = ctk.CTkEntry(filtro_frame, placeholder_text="Buscar...", width=250)
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
            parent,
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

        # BOTÃO: Export Excel
        excel_icon_path = resource_path("assets/icon/excel.png")
        icon_img_atualizar = Image.open(excel_icon_path)
        excel_icon = ctk.CTkImage(
            light_image=icon_img_atualizar,
            dark_image=icon_img_atualizar,
            size=(20,20)
        )

        ctk.CTkButton(
            filtro_frame,
            text="EXPORT EXCEL",
            height=30,
            font=("Segoe UI", 12, "bold"),
            fg_color="#1D6F42",
            hover_color="#185C36",
            corner_radius=10,
            image=excel_icon,
            command=self.acao_exportar
        ).grid(row=0, column=4, padx=10)

    # ---------------
    # FUNÇÕES DA TELA
    # ---------------

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

    def acao_exportar(self):
        try:
            dados = buscar_historico()

            colunas = ["id", "Data de Criação", "EPC", "Descrição", "Patrimônio", "Tipo", "Unidade", "Status"]
            dados = [
                dict(zip(colunas, row))
                for row in buscar_historico()
            ]
            print(dados[:2])

            caminho = export_para_excel(dados)
            if caminho:
                messagebox.showinfo("Sucesso!", "Arquivo exportado com sucesso")
        except Exception as e:
            messagebox.showerror("ERRO", str(e))