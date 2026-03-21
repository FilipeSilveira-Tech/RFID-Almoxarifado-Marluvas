from services.database import execute, fetch_one, fetch_all

def criar_ativo(epc, descricao, patrimonio, tipo, unidade, status="ativo"):
    execute(
        """
        INSERT INTO ativos (epc, descricao, patrimonio, status, tipo, unidade)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (epc, descricao, patrimonio, status, tipo, unidade)
    )

def buscar_ativo_por_epc(epc):
    return fetch_one(
        "SELECT * FROM ativos WHERE epc = ?",
        (epc,)
    )

def listar_ativos():
    return fetch_all("SELECT * FROM ativos ORDER by id DESC")

def atualizar_status(epc, novo_status):
    execute(
        "UPDATE ativos SET status = ? WHERE epc = ?",
        (novo_status, epc)
    )

def deletar_ativo(epc):
    execute(
        "DELETE FROM ativos WHERE epc = ?",
        (epc,)
    )