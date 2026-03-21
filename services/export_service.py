import pandas as pd
from tkinter import filedialog

from services.database import buscar_historico

def export_para_excel(dados):
    if not dados:
        raise ValueError("Nenhum dado para exportar")
    
    caminho = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Salvar como"
    )

    if not caminho:
        return # Cancelamento do usuário
    
    df = pd.DataFrame(dados)
    df.to_excel(caminho, index=False)

    return caminho

