import customtkinter as ctk
from tkinter import ttk
from services.database import buscar_historico

class TabHistorico:
    def __init__(self, parent, app):
        self.app = app

        self.tree_frame = ctk.CTkFrame(parent , fg_color="transparent")
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
            self.tree.column(col, width=100 if col != "data_criacao" else 150, anchor="center")
        self.tree.pack(expand=True, fill="both")
        self.atualizar_tabela_historico()

    def atualizar_tabela_historico(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in buscar_historico():
            self.tree.insert("", "end", values=r)