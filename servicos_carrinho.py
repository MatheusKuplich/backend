"""Serviços relacionados a Carrinho e Pedidos."""

from sqlalchemy import select
from database import SessionLocal
from models import Carrinho, CarrinhoItem, Produto, Cliente, StatusCarrinho


def obter_ou_criar_carrinho_aberto(cliente_id):
    """Obtém o carrinho aberto do cliente ou cria um novo."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        # Procura carrinho aberto
        carrinho = session.scalars(
            select(Carrinho).where(
                (Carrinho.cliente_id == int(cliente_id)) &
                (Carrinho.status == StatusCarrinho.ABERTO.value)
            )
        ).first()

        # Se não existe, cria novo
        if carrinho is None:
            carrinho = Carrinho(cliente_id=int(cliente_id), status=StatusCarrinho.ABERTO.value)
            session.add(carrinho)
            session.commit()
            session.refresh(carrinho)

        return carrinho.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def adicionar_item_ao_carrinho(cliente_id, produto_id, quantidade=1):
    """Adiciona ou atualiza item no carrinho."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        produto = session.get(Produto, int(produto_id))
        if produto is None:
            raise ValueError(f"Produto {produto_id} não encontrado.")

        # Obter ou criar carrinho aberto
        carrinho = session.scalars(
            select(Carrinho).where(
                (Carrinho.cliente_id == int(cliente_id)) &
                (Carrinho.status == StatusCarrinho.ABERTO.value)
            )
        ).first()

        if carrinho is None:
            carrinho = Carrinho(cliente_id=int(cliente_id), status=StatusCarrinho.ABERTO.value)
            session.add(carrinho)
            session.flush()

        # Verificar se o produto já está no carrinho
        item_existente = session.scalars(
            select(CarrinhoItem).where(
                (CarrinhoItem.carrinho_id == carrinho.id) &
                (CarrinhoItem.produto_id == int(produto_id))
            )
        ).first()

        if item_existente:
            # Atualizar quantidade
            item_existente.quantidade += int(quantidade)
            session.add(item_existente)
        else:
            # Criar novo item
            item = CarrinhoItem(
                carrinho_id=carrinho.id,
                produto_id=int(produto_id),
                quantidade=int(quantidade),
                preco_unitario=produto.preco or 0.0
            )
            session.add(item)

        session.commit()
        session.refresh(carrinho)

        return carrinho.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def remover_item_do_carrinho(cliente_id, item_id):
    """Remove um item do carrinho."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        item = session.get(CarrinhoItem, int(item_id))
        if item is None:
            raise ValueError(f"Item {item_id} não encontrado.")

        carrinho = item.carrinho
        if carrinho.cliente_id != int(cliente_id):
            raise ValueError("Este item não pertence ao carrinho do cliente.")

        session.delete(item)
        session.commit()
        session.refresh(carrinho)

        return carrinho.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def listar_carrinho(cliente_id):
    """Lista o carrinho aberto do cliente."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        carrinho = session.scalars(
            select(Carrinho).where(
                (Carrinho.cliente_id == int(cliente_id)) &
                (Carrinho.status == StatusCarrinho.ABERTO.value)
            )
        ).first()

        if carrinho is None:
            # Retornar carrinho vazio
            return {
                "id": None,
                "cliente_id": int(cliente_id),
                "status": StatusCarrinho.ABERTO.value,
                "data_criacao": None,
                "itens": [],
                "total": 0.0,
            }

        return carrinho.to_dict()

    finally:
        session.close()


def finalizar_carrinho(cliente_id):
    """Finaliza (fecha) o carrinho, convertendo em pedido."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        carrinho = session.scalars(
            select(Carrinho).where(
                (Carrinho.cliente_id == int(cliente_id)) &
                (Carrinho.status == StatusCarrinho.ABERTO.value)
            )
        ).first()

        if carrinho is None:
            raise ValueError("Nenhum carrinho aberto para este cliente.")

        if len(carrinho.itens) == 0:
            raise ValueError("Carrinho vazio. Adicione produtos antes de finalizar.")

        carrinho.status = StatusCarrinho.FINALIZADO.value
        session.add(carrinho)
        session.commit()
        session.refresh(carrinho)

        return carrinho.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def limpar_carrinho(cliente_id):
    """Limpa todos os itens do carrinho."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")

        carrinho = session.scalars(
            select(Carrinho).where(
                (Carrinho.cliente_id == int(cliente_id)) &
                (Carrinho.status == StatusCarrinho.ABERTO.value)
            )
        ).first()

        if carrinho is None:
            raise ValueError("Nenhum carrinho aberto para este cliente.")

        # Remover todos os itens
        for item in carrinho.itens:
            session.delete(item)

        session.commit()
        session.refresh(carrinho)

        return carrinho.to_dict()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
