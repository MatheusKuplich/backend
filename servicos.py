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

#/================================================================================Teste Unitario
def _texto_obrigatorio(valor, campo):
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"O campo '{campo}' é obrigatório.")

    return str(valor).strip()


def _texto_opcional(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    return texto or None

#================================================================================Teste Automatizado
def cadastrar_categoria(dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")
    # email = _texto_opcional(dados.get("email"))

    session = SessionLocal()

    try:
        categoria = Categoria(nome=nome) #email=email)

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
    produtos_ids = dados.get("produtos_ids", [])
    if not isinstance(produtos_ids, list):
        raise ValueError("O campo 'produtos_ids' deve ser uma lista de IDs de produtos.")

    session = SessionLocal()
    try:
        produtos = []
        for pid in produtos_ids:
            produto = session.get(Produto, int(pid))
            if produto is None:
                raise ValueError(f"Produto {pid} não encontrado.")
            produtos.append(produto)

        cliente = Cliente(
            nome=nome,
            email=email,
            produtos=produtos
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


def atualizar_categoria(categoria_id, dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")

    session = SessionLocal()
    try:
        categoria = session.get(Categoria, int(categoria_id))
        if categoria is None:
            raise ValueError(f"Categoria {categoria_id} não encontrada.")

        categoria.nome = nome

        session.add(categoria)
        session.commit()
        session.refresh(categoria)

        return categoria.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def remover_categoria(categoria_id):
    session = SessionLocal()
    try:
        categoria = session.get(Categoria, int(categoria_id))
        if categoria is None:
            raise ValueError(f"Categoria {categoria_id} não encontrada.")

        session.delete(categoria)
        session.commit()

        return None

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def atualizar_produto(produto_id, dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")
    codigo = _texto_obrigatorio(dados.get("codigo"), "codigo")

    categoria_id = dados.get("categoria_id")
    if not categoria_id:
        raise ValueError("O campo 'categoria_id' é obrigatório.")

    session = SessionLocal()
    try:
        produto = session.get(Produto, int(produto_id))
        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")

        categoria = session.get(Categoria, int(categoria_id))
        if categoria is None:
            raise ValueError(f"Categoria {categoria_id} não encontrada.")

        produto.nome = nome
        produto.codigo = codigo
        produto.categoria_id = categoria.id

        session.add(produto)
        session.commit()
        session.refresh(produto)

        return produto.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def remover_produto(produto_id):
    session = SessionLocal()
    try:
        produto = session.get(Produto, int(produto_id))
        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")

        session.delete(produto)
        session.commit()

        return None

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def atualizar_cliente(cliente_id, dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")
    email = _texto_opcional(dados.get("email"))
    produtos_ids = dados.get("produtos_ids", [])
    if not isinstance(produtos_ids, list):
        raise ValueError("O campo 'produtos_ids' deve ser uma lista de IDs de produtos.")

    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        produtos = []
        for pid in produtos_ids:
            produto = session.get(Produto, int(pid))
            if produto is None:
                raise ValueError(f"Produto {pid} não encontrado.")
            produtos.append(produto)

        cliente.nome = nome
        cliente.email = email
        cliente.produtos = produtos

        session.add(cliente)
        session.commit()
        session.refresh(cliente)
        return cliente.to_dict()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Funções para gerenciar associação de produtos ao cliente
def listar_produtos_do_cliente(cliente_id):
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")
        return [produto.to_dict() for produto in cliente.produtos]
    finally:
        session.close()

def adicionar_produto_ao_cliente(cliente_id, produto_id):
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")
        produto = session.get(Produto, int(produto_id))
        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")
        if produto not in cliente.produtos:
            cliente.produtos.append(produto)
            session.add(cliente)
            session.commit()
        return [p.to_dict() for p in cliente.produtos]
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def remover_produto_do_cliente(cliente_id, produto_id):
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")
        produto = session.get(Produto, int(produto_id))
        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")
        if produto in cliente.produtos:
            cliente.produtos.remove(produto)
            session.add(cliente)
            session.commit()
        return [p.to_dict() for p in cliente.produtos]
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def remover_cliente(cliente_id):
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        session.delete(cliente)
        session.commit()

        return None

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()