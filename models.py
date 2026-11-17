from datetime import datetime, timedelta
from database import get_connection

def obter_resumo_financeiro():
    conn = get_connection()
    hoje = datetime.now().strftime("%Y-%m-%d")
    mes_atual = datetime.now().strftime("%Y-%m")

    ganhos_mes = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'ganho' AND data LIKE ?",
        (f"{mes_atual}%",)
    ).fetchone()[0]

    gastos_mes = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'gasto' AND data LIKE ?",
        (f"{mes_atual}%",)
    ).fetchone()[0]

    lucro_mes = ganhos_mes - gastos_mes

    ganhos_hoje = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'ganho' AND data = ?",
        (hoje,)
    ).fetchone()[0]

    gastos_hoje = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = 'gasto' AND data = ?",
        (hoje,)
    ).fetchone()[0]

    lucro_hoje = ganhos_hoje - gastos_hoje

    meta_row = conn.execute("SELECT valor FROM config WHERE chave = 'meta_diaria'").fetchone()
    meta_diaria = float(meta_row[0]) if meta_row else 200.0

    progresso = min(max((lucro_hoje / meta_diaria) * 100, 0), 100) if meta_diaria > 0 else 0

    categorias_rows = conn.execute("""
        SELECT categoria, SUM(valor) as total
        FROM transacoes
        WHERE tipo = 'gasto' AND data LIKE ?
        GROUP BY categoria
    """, (f"{mes_atual}%",)).fetchall()

    cat_labels = [row["categoria"] for row in categorias_rows]
    cat_valores = [row["total"] for row in categorias_rows]

    conn.close()

    return {
        "hoje": hoje,
        "ganhos_mes": ganhos_mes,
        "gastos_mes": gastos_mes,
        "lucro_mes": lucro_mes,
        "lucro_hoje": lucro_hoje,
        "meta_diaria": meta_diaria,
        "progresso": progresso,
        "cat_labels": cat_labels,
        "cat_valores": cat_valores
    }

def registrar_transacao(tipo, categoria, descricao, valor, data):
    conn = get_connection()
    conn.execute(
        "INSERT INTO transacoes (tipo, categoria, descricao, valor, data) VALUES (?, ?, ?, ?, ?)",
        (tipo, categoria, descricao, float(valor), data)
    )
    conn.commit()
    conn.close()

def listar_transacoes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM transacoes ORDER BY data DESC, id DESC LIMIT 50").fetchall()
    conn.close()
    return rows

def deletar_transacao(transacao_id):
    conn = get_connection()
    conn.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
    conn.commit()
    conn.close()

def registrar_conta(titulo, categoria, valor, vencimento):
    conn = get_connection()
    conn.execute(
        "INSERT INTO contas (titulo, categoria, valor, vencimento, pago) VALUES (?, ?, ?, ?, 0)",
        (titulo, categoria, float(valor), vencimento)
    )
    conn.commit()
    conn.close()

def listar_contas():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM contas ORDER BY pago ASC, vencimento ASC").fetchall()
    conn.close()
    return rows

def quitar_conta(conta_id):
    conn = get_connection()
    cursor = conn.cursor()
    conta = cursor.execute("SELECT * FROM contas WHERE id = ?", (conta_id,)).fetchone()
    if conta and conta["pago"] == 0:
        hoje = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE contas SET pago = 1 WHERE id = ?", (conta_id,))
        cursor.execute(
            "INSERT INTO transacoes (tipo, categoria, descricao, valor, data) VALUES ('gasto', ?, ?, ?, ?)",
            (conta["categoria"], f"Pgto conta: {conta['titulo']}", conta["valor"], hoje)
        )
    conn.commit()
    conn.close()

def deletar_conta(conta_id):
    conn = get_connection()
    conn.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
    conn.commit()
    conn.close()

def salvar_meta_diaria(nova_meta):
    conn = get_connection()
    conn.execute("UPDATE config SET valor = ? WHERE chave = 'meta_diaria'", (str(float(nova_meta)),))
    conn.commit()
    conn.close()

def criar_recebimentos_parcelados(cliente, servico, valor_parcela, qtd_parcelas, primeiro_vencimento):
    conn = get_connection()
    cursor = conn.cursor()
    data_base = datetime.strptime(primeiro_vencimento, "%Y-%m-%d")
    cliente_limpo = cliente.strip()

    for i in range(1, int(qtd_parcelas) + 1):
        venc = (data_base + timedelta(days=30 * (i - 1))).strftime("%Y-%m-%d")
        parcela_info = f"Parcela {i}/{qtd_parcelas}"
        cursor.execute("""
            INSERT INTO recebimentos (cliente, servico, parcela_info, valor, vencimento, recebido)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (cliente_limpo, servico.strip(), parcela_info, float(valor_parcela), venc))

    conn.commit()
    conn.close()

def listar_recebimentos():
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM recebimentos
        ORDER BY LOWER(cliente) ASC, id ASC
    """).fetchall()
    conn.close()
    return rows

def baixar_recebimento(rec_id):
    conn = get_connection()
    cursor = conn.cursor()
    rec = cursor.execute("SELECT * FROM recebimentos WHERE id = ?", (rec_id,)).fetchone()
    if rec and rec["recebido"] == 0:
        hoje = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE recebimentos SET recebido = 1 WHERE id = ?", (rec_id,))
        desc = f"{rec['cliente']} - {rec['servico']} ({rec['parcela_info']})"
        cursor.execute("""
            INSERT INTO transacoes (tipo, categoria, descricao, valor, data)
            VALUES ('ganho', 'Honorários / Serviços', ?, ?, ?)
        """, (desc, rec["valor"], hoje))
    conn.commit()
    conn.close()

def deletar_recebimento(rec_id):
    conn = get_connection()
    conn.execute("DELETE FROM recebimentos WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
