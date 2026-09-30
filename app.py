# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, redirect, url_for
from database import conectar, criar_banco

app = Flask(__name__)

criar_banco()


@app.route("/")
def index():

    conexao = conectar()

    total = conexao.execute(
        "SELECT COUNT(*) FROM chamados"
    ).fetchone()[0]

    abertos = conexao.execute(
        "SELECT COUNT(*) FROM chamados WHERE status = 'ABERTO'"
    ).fetchone()[0]

    atendimento = conexao.execute(
        "SELECT COUNT(*) FROM chamados WHERE status = 'EM ATENDIMENTO'"
    ).fetchone()[0]

    fechados = conexao.execute(
        "SELECT COUNT(*) FROM chamados WHERE status = 'FECHADO'"
    ).fetchone()[0]

    conexao.close()

    return render_template(
        "index.html",
        total=total,
        abertos=abertos,
        atendimento=atendimento,
        fechados=fechados
    )


@app.route("/chamados")
def listar_chamados():

    conexao = conectar()

    chamados = conexao.execute(
        "SELECT * FROM chamados ORDER BY id DESC"
    ).fetchall()

    conexao.close()

    return render_template(
        "chamados.html",
        chamados=chamados
    )


@app.route("/chamados/novo", methods=["GET", "POST"])
def novo_chamado():

    if request.method == "POST":

        solicitante = request.form["solicitante"]
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        prioridade = request.form["prioridade"]

        conexao = conectar()

        conexao.execute(
            """
            INSERT INTO chamados
            (solicitante, titulo, descricao, prioridade, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                solicitante,
                titulo,
                descricao,
                prioridade,
                "ABERTO"
            )
        )

        conexao.commit()
        conexao.close()

        return redirect(url_for("listar_chamados"))

    return render_template("novo_chamado.html")


@app.route("/chamados/<int:id>")
def visualizar_chamado(id):

    conexao = conectar()

    chamado = conexao.execute(
        "SELECT * FROM chamados WHERE id = ?",
        (id,)
    ).fetchone()

    conexao.close()

    if chamado is None:
        return "Chamado não encontrado", 404

    return render_template(
        "chamado.html",
        chamado=chamado
    )


@app.route("/chamados/<int:id>/status", methods=["POST"])
def alterar_status(id):

    status = request.form["status"]

    conexao = conectar()

    conexao.execute(
        """
        UPDATE chamados
        SET status = ?
        WHERE id = ?
        """,
        (status, id)
    )

    conexao.commit()
    conexao.close()

    return redirect(
        url_for("visualizar_chamado", id=id)
    )


@app.route("/chamados/<int:id>/excluir", methods=["POST"])
def excluir_chamado(id):

    conexao = conectar()

    conexao.execute(
        "DELETE FROM chamados WHERE id = ?",
        (id,)
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("listar_chamados"))


if __name__ == "__main__":
    app.run(debug=True)