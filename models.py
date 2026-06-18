from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

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
        }

    def __repr__(self):
        return f"<Produto {self.id} {self.codigo!r}>"



# Cliente da loja
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=True)

    produtos = relationship(
        "Produto",
        secondary=cliente_produto,
        back_populates="clientes"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "produtos": [produto.id for produto in self.produtos],
        }

    def __repr__(self):
        return f"<Cliente {self.id} {self.nome!r}>"