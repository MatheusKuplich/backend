"""
Script para adicionar coluna senha_hash à tabela clientes e criar tabelas de carrinho
"""

from database import engine
from sqlalchemy import text

def migrar():
    with engine.connect() as conn:
        try:
            # Adicionar coluna senha_hash se não existir
            conn.execute(text("""
                ALTER TABLE clientes ADD COLUMN senha_hash VARCHAR(255) DEFAULT NULL;
            """))
            conn.commit()
            print("✓ Coluna senha_hash adicionada à tabela clientes")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Coluna senha_hash já existe")
            else:
                print(f"Aviso: {e}")
                conn.rollback()

    # Criar todas as tabelas
    from models import Base
    print("Criando/atualizando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Banco de dados atualizado com sucesso!")

if __name__ == "__main__":
    migrar()
