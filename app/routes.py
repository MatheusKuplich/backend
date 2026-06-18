import flask as fk
from sqlalchemy.exc import IntegrityError

from servicos import (
    cadastrar_categoria,
    listar_categorias,
    atualizar_categoria,
    remover_categoria,
    cadastrar_produto,
    listar_produtos,
    atualizar_produto,
    remover_produto,
    cadastrar_cliente,
    listar_clientes,
    atualizar_cliente,
    remover_cliente,
    listar_produtos_do_cliente,
    adicionar_produto_ao_cliente,
    remover_produto_do_cliente,
)

bp = fk.Blueprint("api", __name__, url_prefix="/api")

bp = fk.Blueprint("api", __name__, url_prefix="/api")

# Rotas para gerenciar produtos de um cliente
@bp.get("/clientes/<int:cliente_id>/produtos")
def get_produtos_do_cliente(cliente_id):
    try:
        return fk.jsonify(listar_produtos_do_cliente(cliente_id))
    except ValueError as exc:
        return _erro(str(exc), 404)

@bp.post("/clientes/<int:cliente_id>/produtos/<int:produto_id>")
def post_produto_ao_cliente(cliente_id, produto_id):
    try:
        return fk.jsonify(adicionar_produto_ao_cliente(cliente_id, produto_id)), 201
    except ValueError as exc:
        return _erro(str(exc), 404)

@bp.delete("/clientes/<int:cliente_id>/produtos/<int:produto_id>")
def delete_produto_do_cliente(cliente_id, produto_id):
    try:
        return fk.jsonify(remover_produto_do_cliente(cliente_id, produto_id))
    except ValueError as exc:
        return _erro(str(exc), 404)


def _erro(mensagem, status=400):
    return fk.jsonify({"erro": mensagem}), status


@bp.get("/categorias")
def categorias():
    return fk.jsonify(listar_categorias())


@bp.post("/categorias")
def criar_categoria():
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(cadastrar_categoria(dados)), 201
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Já existe uma categoria com este e-mail.", 409)


@bp.put("/categorias/<int:categoria_id>")
def atualizar_categoria_route(categoria_id):
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(atualizar_categoria(categoria_id, dados))
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Já existe uma categoria com este e-mail.", 409)


@bp.delete("/categorias/<int:categoria_id>")
def excluir_categoria_route(categoria_id):
    try:
        remover_categoria(categoria_id)
        return "", 204
    except ValueError as exc:
        return _erro(str(exc), 404)


@bp.get("/produtos")
def produtos():
    return fk.jsonify(listar_produtos())


@bp.post("/produtos")
def criar_produto():
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(cadastrar_produto(dados)), 201
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Já existe um produto com este código.", 409)


@bp.put("/produtos/<int:produto_id>")
def atualizar_produto_route(produto_id):
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(atualizar_produto(produto_id, dados))
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Já existe um produto com este código.", 409)


@bp.delete("/produtos/<int:produto_id>")
def excluir_produto_route(produto_id):
    try:
        remover_produto(produto_id)
        return "", 204
    except ValueError as exc:
        return _erro(str(exc), 404)


@bp.get("/clientes")
def clientes():
    return fk.jsonify(listar_clientes())


@bp.post("/clientes")
def criar_cliente():
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(cadastrar_cliente(dados)), 201
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError as exc:
        orig = str(exc.orig) if getattr(exc, "orig", None) else str(exc)
        orig_l = orig.lower()
        if "unique" in orig_l and "email" in orig_l:
            return _erro("Já existe um cliente com este e-mail.", 409)
        return _erro(
            "Não foi possível cadastrar o cliente (restrição do banco de dados).",
            409,
        )


@bp.put("/clientes/<int:cliente_id>")
def atualizar_cliente_route(cliente_id):
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(atualizar_cliente(cliente_id, dados))
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError as exc:
        orig = str(exc.orig) if getattr(exc, "orig", None) else str(exc)
        orig_l = orig.lower()
        if "unique" in orig_l and "email" in orig_l:
            return _erro("Já existe um cliente com este e-mail.", 409)
        return _erro(
            "Não foi possível atualizar o cliente (restrição do banco de dados).",
            409,
        )


@bp.delete("/clientes/<int:cliente_id>")
def excluir_cliente_route(cliente_id):
    try:
        remover_cliente(cliente_id)
        return "", 204
    except ValueError as exc:
        return _erro(str(exc), 404)


paginas = fk.Blueprint("paginas", __name__)


@paginas.get("/")
def home():
    return fk.render_template("index.html")


@paginas.get("/home")
def home_page():
    """Renderiza a página estática `home.html` usada pela UI."""
    return fk.render_template("home.html")


@paginas.get("/cadastro")
def cadastro_page():
    """Renderiza a página de cadastro (cadastro.html)."""
    return fk.render_template("cadastro.html")


@paginas.get("/faq")
def faq_page():
    return fk.render_template_string('<h1>FAQ</h1><p>Em construção.</p><p><a href="' + fk.url_for("paginas.home_page") + '">Voltar</a></p>')


@paginas.get("/trabalhe")
def trabalhe_page():
    return fk.render_template_string('<h1>Trabalhe Conosco</h1><p>Em construção.</p><p><a href="' + fk.url_for("paginas.home_page") + '">Voltar</a></p>')


@paginas.get("/filmes")
def filmes_page():
    return fk.render_template_string('<h1>Filmes</h1><p>Em construção.</p><p><a href="' + fk.url_for("paginas.home_page") + '">Voltar</a></p>')


@paginas.get("/termos")
def termos_page():
    return fk.render_template_string('<h1>Termos e Políticas</h1><p>Em construção.</p><p><a href="' + fk.url_for("paginas.home_page") + '">Voltar</a></p>')
