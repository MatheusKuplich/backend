"""Remove unwanted categories from database and reassign products to first available category."""
from database import SessionLocal
from models import Categoria, Produto
from sqlalchemy import select

session = SessionLocal()
try:
    # Categories to remove: Eletrônicos, Figuras, Mídias, Posters
    unwanted = ['Eletrônicos', 'Figuras', 'Mídias', 'Posters']
    
    # Get first remaining category for reassignment
    first_remaining = session.scalars(
        select(Categoria).order_by(Categoria.id).limit(1)
    ).first()
    
    if not first_remaining:
        print("Nenhuma categoria disponível! Crie uma categoria antes de remover.")
    else:
        for nome in unwanted:
            cat = session.scalars(
                select(Categoria).where(Categoria.nome == nome)
            ).first()
            if cat:
                # Reassign products to first remaining category
                produtos = session.scalars(
                    select(Produto).where(Produto.categoria_id == cat.id)
                ).all()
                for prod in produtos:
                    prod.categoria_id = first_remaining.id
                    session.add(prod)
                session.delete(cat)
                print(f"Deletada categoria: {nome} (produtos reatribuídos)")
            else:
                print(f"Categoria não encontrada: {nome}")
        
        session.commit()
        print("Operação concluída com sucesso.")
finally:
    session.close()
