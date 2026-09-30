from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# Tabela de associação Cliente-Produto
cliente_produto = Table(
    'cliente_produto', Base.metadata,
    Column('cliente_id', Integer, ForeignKey('clientes.id'), primary_key=True),
    Column('produto_id', Integer, ForeignKey('produtos.id'), primary_key=True)
)


# Categoria de produtos Star Wars
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    # email = Column(String(120), unique=True, nullable=True)

    produtos = relationship("Produto", back_populates="categoria")

    def to_dict(self):
        return {"id": self.id, "nome": self.nome}

    def __repr__(self):
        return f"<Categoria {self.id} {self.nome!r}>"


# Produto Star Wars
class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    codigo = Column(String(40), unique=True, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    preco = Column(Float, nullable=True)
    imagem = Column(String(255), nullable=True)
    destaque = Column(Boolean, default=False, nullable=False)

    categoria = relationship("Categoria", back_populates="produtos")
    clientes = relationship(
        "Cliente",
        secondary=cliente_produto,
        back_populates="produtos"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo,
            "categoria_id": self.categoria_id,
            "preco": float(self.preco) if self.preco is not None else None,
            "imagem": self.imagem,
            "destaque": bool(self.destaque),
        }

    def __repr__(self):
        return f"<Produto {self.id} {self.codigo!r}>"



# Cliente da loja
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    senha_hash = Column(String(255), nullable=True)  # Para autenticação futura

    produtos = relationship(
        "Produto",
        secondary=cliente_produto,
        back_populates="clientes"
    )
    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "produtos": [produto.id for produto in self.produtos],
        }

    def __repr__(self):
        return f"<Cliente {self.id} {self.nome!r}>"


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    status = Column(String(40), nullable=False, default="pago")
    total = Column(Float, nullable=False, default=0.0)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="pedidos")
    itens = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "status": self.status,
            "total": float(self.total) if self.total is not None else 0.0,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "itens": [item.to_dict() for item in self.itens],
        }


class PedidoItem(Base):
    __tablename__ = "pedido_itens"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    preco_unitario = Column(Float, nullable=False, default=0.0)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")

    def to_dict(self):
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "produto_id": self.produto_id,
            "produto_nome": self.produto.nome if self.produto else None,
            "quantidade": self.quantidade,
            "preco_unitario": float(self.preco_unitario) if self.preco_unitario is not None else 0.0,
        }