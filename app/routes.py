import flask as fk
from sqlalchemy.exc import IntegrityError

from servicos import (
    cadastrar_categoria,
    listar_categorias,
    cadastrar_produto,
    listar_produtos,
    cadastrar_cliente,
    listar_clientes,
)

bp = fk.Blueprint("api", __name__, url_prefix="/api")


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


paginas = fk.Blueprint("paginas", __name__)


@paginas.get("/")
def home():
    return fk.render_template("index.html")
