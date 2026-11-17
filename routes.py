from flask import Blueprint, render_template, request, redirect, url_for
from models import (
    obter_resumo_financeiro,
    registrar_transacao,
    listar_transacoes,
    deletar_transacao,
    registrar_conta,
    listar_contas,
    quitar_conta,
    deletar_conta,
    salvar_meta_diaria,
    criar_recebimentos_parcelados,
    listar_recebimentos,
    baixar_recebimento,
    deletar_recebimento
)

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    resumo = obter_resumo_financeiro()
    transacoes = listar_transacoes()
    contas = listar_contas()
    recebimentos = listar_recebimentos()
    aba_ativa = request.args.get("aba", "painel")
    return render_template(
        "index.html",
        **resumo,
        transacoes=transacoes,
        contas=contas,
        recebimentos=recebimentos,
        aba_ativa=aba_ativa
    )

@main_bp.route("/transacao", methods=["POST"])
def add_transacao():
    registrar_transacao(
        tipo=request.form["tipo"],
        categoria=request.form["categoria"],
        descricao=request.form.get("descricao", ""),
        valor=request.form["valor"],
        data=request.form["data"]
    )
    return redirect(url_for("main.index", aba="painel"))

@main_bp.route("/excluir_transacao/<int:id>", methods=["POST"])
def excluir_transacao(id):
    deletar_transacao(id)
    return redirect(url_for("main.index", aba="historico"))

@main_bp.route("/conta", methods=["POST"])
def add_conta():
    registrar_conta(
        titulo=request.form["titulo"],
        categoria=request.form["categoria"],
        valor=request.form["valor"],
        vencimento=request.form["vencimento"]
    )
    return redirect(url_for("main.index", aba="contas"))

@main_bp.route("/pagar_conta/<int:id>", methods=["POST"])
def pagar_conta(id):
    quitar_conta(id)
    return redirect(url_for("main.index", aba="contas"))

@main_bp.route("/excluir_conta/<int:id>", methods=["POST"])
def excluir_conta(id):
    deletar_conta(id)
    return redirect(url_for("main.index", aba="contas"))

@main_bp.route("/meta", methods=["POST"])
def atualizar_meta():
    salvar_meta_diaria(request.form["meta_diaria"])
    return redirect(url_for("main.index", aba="painel"))

@main_bp.route("/recebimento", methods=["POST"])
def add_recebimento():
    criar_recebimentos_parcelados(
        cliente=request.form["cliente"],
        servico=request.form["servico"],
        valor_parcela=request.form["valor"],
        qtd_parcelas=request.form["parcelas"],
        primeiro_vencimento=request.form["vencimento"]
    )
    return redirect(url_for("main.index", aba="clientes"))

@main_bp.route("/baixar_recebimento/<int:id>", methods=["POST"])
def pagar_recebimento(id):
    baixar_recebimento(id)
    return redirect(url_for("main.index", aba="clientes"))

@main_bp.route("/excluir_recebimento/<int:id>", methods=["POST"])
def excluir_recebimento(id):
    deletar_recebimento(id)
    return redirect(url_for("main.index", aba="clientes"))
