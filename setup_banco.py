"""
Script para criar/atualizar tabelas do banco de dados com suporte a Carrinho.
Usa CREATE TABLE IF NOT EXISTS para ser seguro.
"""

from database import engine
from models import Base

def setup_banco():
    """Cria todas as tabelas definidas em models."""
    print("Criando/atualizando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Banco de dados atualizado com sucesso!")

if __name__ == "__main__":
    setup_banco()
