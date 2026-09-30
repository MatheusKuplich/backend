from app import create_app


def test_produtos_destaques_endpoint():
    app = create_app()
    client = app.test_client()

    resp = client.get('/api/produtos/destaques')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
