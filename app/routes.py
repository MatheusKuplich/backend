import functools
import flask as fk
from datetime import date
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import Cliente, Pedido, PedidoItem, Produto
from servicos_autenticacao import login_por_nome_email, registrar_cliente
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
    listar_produtos_destaque,
)

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
        # Apenas "não encontrada" retorna 404
        return _erro(str(exc), 404)
    except IntegrityError as exc:
        # Erro de integridade no banco (FK, etc.)
        return _erro("Não foi possível excluir a categoria por restrição de integridade.", 409)


@bp.get("/produtos")
def produtos():
    return fk.jsonify(listar_produtos())


@bp.get('/produtos/destaques')
def produtos_destaques_api():
    # Retorna JSON com os produtos marcados como destaque
    destaque = listar_produtos_destaque()
    return fk.jsonify(destaque)


@bp.get("/produtos/<int:produto_id>")
def get_produto(produto_id):
    """Obtém um produto específico."""
    try:
        from database import SessionLocal
        from models import Produto
        session = SessionLocal()
        produto = session.get(Produto, int(produto_id))
        session.close()
        
        if produto is None:
            return _erro(f"Produto {produto_id} não encontrado.", 404)
        
        return fk.jsonify(produto.to_dict())
    except Exception as exc:
        return _erro(str(exc), 400)


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
        # Diferenciar: produto não encontrado (404) vs. outros erros de negócio (409)
        msg = str(exc).lower()
        if "não encontrado" in msg:
            return _erro(str(exc), 404)
        else:
            return _erro(str(exc), 409)
    except IntegrityError as exc:
        return _erro("Não foi possível excluir o produto por restrição de integridade.", 409)


@bp.get("/clientes")
def clientes():
    return fk.jsonify(listar_clientes())


@bp.post("/pedidos")
def criar_pedido():
    dados = fk.request.get_json(silent=True) or {}
    itens = dados.get("itens") or []

    if not isinstance(itens, list) or len(itens) == 0:
        return _erro("Adicione pelo menos um item ao carrinho para finalizar a compra.", 400)

    cliente_id = dados.get("cliente_id")
    session = SessionLocal()
    try:
        cliente = None
        if cliente_id not in (None, "", 0):
            cliente = session.get(Cliente, int(cliente_id))
            if cliente is None:
                raise ValueError(f"Cliente {cliente_id} não encontrado.")

        pedido = Pedido(cliente=cliente, status="pago", total=0.0)
        session.add(pedido)
        session.flush()

        total = 0.0
        for item in itens:
            produto_id = item.get("produto_id")
            quantidade = item.get("quantidade", 1)
            preco_unitario = item.get("preco_unitario", 0)

            if not produto_id:
                raise ValueError("Cada item do pedido precisa de um produto_id.")
            if not isinstance(quantidade, int) or quantidade < 1:
                raise ValueError("A quantidade de cada item deve ser um número inteiro maior que zero.")

            produto = session.get(Produto, int(produto_id))
            if produto is None:
                raise ValueError(f"Produto {produto_id} não encontrado.")

            subtotal = float(preco_unitario or 0) * quantidade
            total += subtotal

            pedido_item = PedidoItem(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=float(preco_unitario or 0),
            )
            session.add(pedido_item)

        pedido.total = total
        session.commit()
        session.refresh(pedido)
        return fk.jsonify(pedido.to_dict()), 201
    except ValueError as exc:
        session.rollback()
        return _erro(str(exc), 400)
    except Exception as exc:
        session.rollback()
        return _erro(str(exc), 400)
    finally:
        session.close()


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
        # Diferenciar: cliente não encontrado (404) vs. outros erros de negócio (409)
        msg = str(exc).lower()
        if "não encontrado" in msg:
            return _erro(str(exc), 404)
        else:
            return _erro(str(exc), 409)
    except IntegrityError as exc:
        return _erro("Não foi possível excluir o cliente por restrição de integridade.", 409)


ADMIN_EMAILS = {"admin@admin.com"}

paginas = fk.Blueprint("paginas", __name__)
admin = fk.Blueprint("admin", __name__, url_prefix="/admin")


def _usuario_eh_admin():
    email = fk.session.get("cliente_email")
    return email is not None and email.lower() in ADMIN_EMAILS


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if not _usuario_eh_admin():
            return fk.redirect(fk.url_for("paginas.home_page"))
        return view(*args, **kwargs)
    return wrapped_view


@paginas.get("/")
def root_page():
    return fk.redirect(fk.url_for("paginas.home_page"))


@admin.get("/")
@admin_required
def admin_page():
    session = SessionLocal()
    try:
        total_clientes = session.query(func.count(Cliente.id)).scalar() or 0
        total_produtos = session.query(func.count(Produto.id)).scalar() or 0
        total_pedidos = session.query(func.count(Pedido.id)).scalar() or 0
        total_vendas = session.query(func.coalesce(func.sum(Pedido.total), 0.0)).scalar() or 0.0
        hoje = date.today()
        pedidos_hoje = (
            session.query(func.count(Pedido.id))
            .filter(func.date(Pedido.criado_em) == hoje)
            .scalar()
            or 0
        )
    finally:
        session.close()

    return fk.render_template(
        "index.html",
        total_clientes=total_clientes,
        total_produtos=total_produtos,
        total_pedidos=total_pedidos,
        total_vendas=total_vendas,
        pedidos_hoje=pedidos_hoje,
    )


@paginas.get("/home")
def home_page():
    """Renderiza a página estática `home.html` usada pela UI."""
    # buscar destaques e categorias para renderizar a home
    try:
        produtos_destaque = listar_produtos_destaque(limit=12)
    except Exception:
        produtos_destaque = []

    try:
        categorias_principais = listar_categorias()[:8]
    except Exception:
        categorias_principais = []

    return fk.render_template("home.html", produtos_destaque=produtos_destaque, categorias_principais=categorias_principais)


@paginas.route("/cadastro", methods=["GET", "POST"])
def cadastro_page():
    """Renderiza e processa o acesso simples do cliente."""
    if fk.request.method == "POST":
        nome = (fk.request.form.get("nome") or "").strip()
        email = (fk.request.form.get("email") or "").strip()

        try:
            cliente = login_por_nome_email(nome, email)
        except ValueError as exc:
            return fk.render_template("cadastro.html", erro=str(exc)), 400

        fk.session.clear()
        fk.session["cliente_id"] = cliente["id"]
        fk.session["cliente_nome"] = cliente["nome"]
        fk.session["cliente_email"] = cliente["email"]
        fk.session["cliente_token"] = cliente["token"]
        fk.session["is_admin"] = cliente["email"].lower() in ADMIN_EMAILS

        if fk.session["is_admin"]:
            return fk.redirect(fk.url_for("admin.admin_page"))

        return fk.redirect(fk.url_for("paginas.home_page"))

    return fk.render_template("cadastro.html")


@paginas.route("/criar-conta", methods=["GET", "POST"])
def criar_conta_page():
    """Renderiza e processa a criação de conta do cliente."""
    if fk.request.method == "POST":
        nome = (fk.request.form.get("nome") or "").strip()
        email = (fk.request.form.get("email") or "").strip()
        senha = fk.request.form.get("senha") or ""
        confirmar_senha = fk.request.form.get("confirmar_senha") or ""

        if confirmar_senha and senha != confirmar_senha:
            return fk.render_template("criar_conta.html", erro="As senhas devem coincidir."), 400

        try:
            cliente = registrar_cliente(nome, email, senha)
        except ValueError as exc:
            return fk.render_template("criar_conta.html", erro=str(exc)), 400

        fk.session.clear()
        fk.session["cliente_id"] = cliente["id"]
        fk.session["cliente_nome"] = cliente["nome"]
        fk.session["cliente_email"] = cliente["email"]
        fk.session["cliente_token"] = cliente["token"]
        fk.session["is_admin"] = cliente["email"].lower() in ADMIN_EMAILS

        if fk.session["is_admin"]:
            return fk.redirect(fk.url_for("admin.admin_page"))

        return fk.redirect(fk.url_for("paginas.home_page"))

    return fk.render_template("criar_conta.html")


@paginas.get("/logout")
def logout_page():
    """Encerra a sessão do cliente e redireciona para a home."""
    fk.session.clear()
    return fk.redirect(fk.url_for("paginas.home_page"))


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
