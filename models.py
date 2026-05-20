from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# Categoria de produtos Star Wars
class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=True)

    produtos = relationship("Produto", back_populates="categoria")

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "email": self.email}

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
    clientes = relationship("Cliente", back_populates="produto")

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
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)

    produto = relationship("Produto", back_populates="clientes")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "produto_id": self.produto_id,
        }

    def __repr__(self):
        return f"<Cliente {self.id} {self.nome!r}>"