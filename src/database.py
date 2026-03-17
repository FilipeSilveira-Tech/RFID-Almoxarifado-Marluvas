import sqlite3
from datetime import datetime
from tkinter import messagebox

DB_NAME = "historico_rfid.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS impressoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            epc INTEGER UNIQUE,
            campo1 TEXT,
            campo2 TEXT,
            campo3 TEXT,
            campo4 TEXT
        )
    """)
    conn.commit()
    conn.close()


def registrar_impressao(epc, produto, patrimonio, setor, responsavel):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    try:
        cursor.execute(
            "INSERT INTO impressoes (data_hora, epc, campo1, campo2, campo3, campo4) VALUES (?,?,?,?,?,?)",
            (
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                epc,
                produto,
                patrimonio,
                setor,
                responsavel
            )
        )
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("EPC Duplicado", f"O EPC {epc} já foi utilizado!")

    conn.close()

def buscar_historico():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, data_hora, epc, campo1, campo2, campo3, campo4 FROM impressoes ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def obter_proximo_epc():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(epc) FROM impressoes")
    resultado = cursor.fetchone()
    conn.close()

    if resultado[0] is None:
        return 10001 # Primeiro EPC se banco estiver em branco
    else:
        return int(resultado[0]) + 1