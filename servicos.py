import re

from sqlalchemy import select, update

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


def _email_valido(email):
    if email is None:
        return True

    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email))


def listar_produtos_destaque(limit: int = 12):
    session = SessionLocal()
    try:
        linhas = session.scalars(
            select(Produto).where(Produto.destaque == True).limit(limit)
        ).all()

        return [p.to_dict() for p in linhas]
    finally:
        session.close()

#================================================================================Teste Automatizado
def cadastrar_categoria(dados):
    nome = _texto_obrigatorio(dados.get("nome"), "nome")
    email = _texto_opcional(dados.get("email"))

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

        # opcional: preco, imagem, destaque
        preco = dados.get("preco")
        imagem = dados.get("imagem")
        destaque = bool(dados.get("destaque", False))

        produto = Produto(
            nome=nome,
            codigo=codigo,
            categoria_id=categoria.id,
            preco=float(preco) if preco is not None and preco != "" else None,
            imagem=imagem,
            destaque=destaque,
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
    if email is not None and not _email_valido(email):
        raise ValueError("O campo 'email' deve conter um e-mail válido.")

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

        if getattr(categoria, "nome", None) == "Padrão":
            raise ValueError("A categoria 'Padrão' não pode ser removida.")

        # Se a categoria tem produtos, reatribuí-los a uma categoria "Padrão"
        num_produtos = len(getattr(categoria, "produtos", None) or [])
        if num_produtos > 0:
            # Fechar e abrir nova sessão para evitar rastreamento confuso
            session.expunge_all()
            
            # Procurar categoria "Padrão" em nova sessão
            resultado = session.scalars(
                select(Categoria).filter_by(nome="Padrão")
            ).first()
            categoria_padrao = resultado
            
            # Se não existir, criar
            if categoria_padrao is None:
                categoria_padrao = Categoria(nome="Padrão")
                session.add(categoria_padrao)
                session.commit()
                session.refresh(categoria_padrao)
            
            # Reatribuir usando UPDATE SQL direto
            stmt = update(Produto).where(Produto.categoria_id == int(categoria_id)).values(categoria_id=categoria_padrao.id)
            session.execute(stmt)
            session.commit()

        # Atualizar referência da categoria (pode ter mudado)
        categoria = session.get(Categoria, int(categoria_id))
        if categoria:
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

        # Remover associações com clientes antes de excluir o produto para
        # evitar violação de restrições da tabela de associação.
        if getattr(produto, "clientes", None) and len(produto.clientes) > 0:
            produto.clientes = []
            session.add(produto)
            session.flush()

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
    if email is not None and not _email_valido(email):
        raise ValueError("O campo 'email' deve conter um e-mail válido.")

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

        # Limpar associações com produtos antes de remover o cliente,
        # para evitar erros de integridade na tabela de associação.
        if getattr(cliente, "produtos", None) and len(cliente.produtos) > 0:
            cliente.produtos = []
            session.add(cliente)
            session.flush()

        session.delete(cliente)
        session.commit()

        return None

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()