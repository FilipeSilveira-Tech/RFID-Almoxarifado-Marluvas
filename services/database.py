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
        data_criacao DATETIME,
        epc TEXT UNIQUE,
        descricao TEXT,
        patrimonio TEXT,
        tipo TEXT,
        unidade TEXT,
        status TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ativos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        epc TEXT UNIQUE,
        descricao TEXT,
        patrimonio TEXT,
        tipo TEXT,
        unidade TEXT,
        status TEXT,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()


def registrar_impressao(epc, descricao, patrimonio, tipo, unidade, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO impressoes (data_criacao, epc, descricao, patrimonio, unidade, tipo, status) VALUES (?,?,?,?,?,?,?)",
            (
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                epc,
                descricao,
                patrimonio,
                unidade,
                tipo,
                status
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
        "SELECT id, data_criacao, epc, descricao, patrimonio, unidade, tipo, status FROM impressoes ORDER BY id DESC"
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

def get_connection():
    return sqlite3.connect(DB_NAME)

def execute(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_one(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result

def fetch_all(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result