from uuid import uuid4

from app import create_app
from database import SessionLocal
from models import Categoria, Produto


def test_criar_pedido_com_itens():
    app = create_app()

    with app.app_context():
        session = SessionLocal()
        try:
            categoria = Categoria(nome="Teste Checkout")
            session.add(categoria)
            session.commit()
            session.refresh(categoria)

            produto = Produto(
                nome="Camiseta Star Wars",
                codigo=f"CHECKOUT-{uuid4().hex[:8]}",
                categoria_id=categoria.id,
                preco=19.99,
                destaque=False,
            )
            session.add(produto)
            session.commit()
            session.refresh(produto)
            produto_id = produto.id
        finally:
            session.close()

    client = app.test_client()
    response = client.post(
        "/api/pedidos",
        json={
            "cliente_id": None,
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 2,
                    "preco_unitario": 19.99,
                }
            ],
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "pago"
    assert data["total"] == 39.98
    assert len(data["itens"]) == 1
    assert data["itens"][0]["quantidade"] == 2
