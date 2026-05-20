from sqlalchemy import select

from database import SessionLocal
from models import Categoria, Produto, Cliente


def listar_categorias():
    session = SessionLocal()
    try:
        linhas = session.scalars(
            select(Categoria).order_by(Categoria.nome)
        ).all()

        return [c.to_dict() for c in linhas]
    finally:
        session.close()


def listar_produtos():
    session = SessionLocal()
    try:
        linhas = session.scalars(
            select(Produto).order_by(Produto.codigo)
        ).all()

        return [p.to_dict() for p in linhas]
    finally:
        session.close()


def listar_clientes():
    session = SessionLocal()
    try:
        linhas = session.scalars(
            select(Cliente).order_by(Cliente.nome)
        ).all()

        return [c.to_dict() for c in linhas]
    finally:
        session.close()


def _texto_obrigatorio(valor, campo):
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"O campo '{campo}' é obrigatório.")

    return str(valor).strip()


def _texto_opcional(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    return texto or None


def cadastrar_categoria(dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")
    email = _texto_opcional(dados.get("email"))

    session = SessionLocal()

    try:
        categoria = Categoria(nome=nome, email=email)

        session.add(categoria)
        session.commit()
        session.refresh(categoria)

        return categoria.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def cadastrar_produto(dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")
    codigo = _texto_obrigatorio(dados.get("codigo"), "codigo")

    categoria_id = dados.get("categoria_id")

    if not categoria_id:
        raise ValueError("O campo 'categoria_id' é obrigatório.")

    session = SessionLocal()

    try:
        categoria = session.get(Categoria, int(categoria_id))

        if categoria is None:
            raise ValueError(f"Categoria {categoria_id} não encontrada.")

        produto = Produto(
            nome=nome,
            codigo=codigo,
            categoria_id=categoria.id,
        )

        session.add(produto)
        session.commit()
        session.refresh(produto)

        return produto.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def cadastrar_cliente(dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")

    email = _texto_opcional(dados.get("email"))

    produto_id = dados.get("produto_id")

    if not produto_id:
        raise ValueError("O campo 'produto_id' é obrigatório.")

    session = SessionLocal()

    try:
        produto = session.get(Produto, int(produto_id))

        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")

        cliente = Cliente(
            nome=nome,
            email=email,
            produto_id=produto.id,
        )

        session.add(cliente)
        session.commit()
        session.refresh(cliente)

        return cliente.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()