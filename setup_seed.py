import os
import sqlite3
from database import _db_path, engine, SessionLocal
from servicos import cadastrar_categoria, cadastrar_produto, listar_categorias
from models import Categoria, Produto

# Ensure DB has new columns (preco, imagem, destaque)
def ensure_columns():
    conn = sqlite3.connect(_db_path)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(produtos)")
    cols = [row[1] for row in cur.fetchall()]
    changed = False
    if 'preco' not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN preco REAL")
        changed = True
    if 'imagem' not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
        changed = True
    if 'destaque' not in cols:
        cur.execute("ALTER TABLE produtos ADD COLUMN destaque INTEGER DEFAULT 0")
        changed = True
    if changed:
        print('Colunas adicionadas ao banco: ', _db_path)
    else:
        print('Colunas já existem')
    conn.commit()
    conn.close()


def seed():
    ensure_columns()

    # create some categories if not present
    existing = listar_categorias()
    existing_names = {c['nome'].lower(): c for c in existing}

    sample_cats = ['Figuras', 'Réplicas', 'Posters', 'Filmes', 'Jogos', 'Livros', 'Mídias', 'Colecionáveis']
    cat_ids = {}
    for nome in sample_cats:
        if nome.lower() not in existing_names:
            cat = cadastrar_categoria({'nome': nome})
            cat_ids[nome] = cat['id']
        else:
            cat_ids[nome] = existing_names[nome.lower()]['id']

    # create sample products
    session = SessionLocal()
    try:
        # check if products exist
        from servicos import listar_produtos
        produtos = listar_produtos()
        if produtos:
            print('Produtos já existem, não serão re-criados.')
            return
    finally:
        session.close()

    sample_products = [
        {'nome': 'Action Figure Luke Skywalker', 'codigo': 'LSK-001', 'categoria_id': cat_ids['Figuras'], 'preco': 199.90, 'imagem': '/static/img/products/luke.svg', 'destaque': True},
        {'nome': 'Sabre de Luz Réplica', 'codigo': 'SAB-100', 'categoria_id': cat_ids['Réplicas'], 'preco': 349.50, 'imagem': '/static/img/products/sabre.svg', 'destaque': True},
        {'nome': 'Poster Star Wars Clássico', 'codigo': 'PST-01', 'categoria_id': cat_ids['Posters'], 'preco': 49.90, 'imagem': '/static/img/products/poster.svg', 'destaque': True},
        {'nome': 'Box Filmes Star Wars', 'codigo': 'BOX-STAR', 'categoria_id': cat_ids['Filmes'], 'preco': 129.90, 'imagem': '/static/img/products/box.svg', 'destaque': True},
    ]

    for p in sample_products:
        try:
            cadastrar_produto(p)
            print('Produto criado:', p['nome'])
        except Exception as e:
            print('Erro ao criar produto', p['nome'], e)


if __name__ == '__main__':
    seed()
