from repositories.ativo_repository import (
    criar_ativo,
    buscar_ativo_por_epc
)
from services.database import get_connection


def registrar_ativo(epc, descricao, patrimonio, tipo, unidade, status):
    if not epc or not descricao:
        raise Exception("EPC e Descrição são obrigatórios")

    ativo = buscar_ativo_por_epc(epc)

    if ativo:
        raise Exception("EPC já cadastrado")

    criar_ativo(epc, descricao, patrimonio, tipo, unidade, status)

def buscar_ativos(filtro_texto=None, status=None, unidade=None):
    query = "SELECT epc, descricao, patrimonio, unidade, tipo, status FROM ativos WHERE 1=1"
    params = []

    if filtro_texto:
        query += """
        AND(
            descricao LIKE ?
            OR patrimonio LIKE ?
            OR unidade LIKE ?
            OR epc LIKE ?
        )
        """
        termo = f"%{filtro_texto}%"
        params.extend([termo, termo, termo, termo])

    if status:
        query += " AND UPPER(TRIM(status)) = UPPER(TRIM(?))"
        params.append(status)

    if unidade:
        query += " AND UPPER(TRIM(unidade)) = UPPER(TRIM(?))"
        params.append(unidade)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()