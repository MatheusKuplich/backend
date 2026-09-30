from uuid import uuid4

from app import create_app


def test_email_invalido_retorna_mensagem_clara_na_criacao():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/criar-conta",
        data={
            "nome": "Teste Email",
            "email": "email-sem-arroba",
            "senha": "123456",
            "confirmar_senha": "123456",
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert b"e-mail v\xc3\xa1lido" in response.data.lower()


def test_criar_conta_e_entrar_redirecionam_para_home_com_sessao():
    app = create_app()
    client = app.test_client()
    email = f"testeauth-{uuid4().hex[:8]}@teste.com"

    cadastro = client.post(
        "/criar-conta",
        data={
            "nome": "Teste Auth",
            "email": email,
            "senha": "123456",
        },
        follow_redirects=False,
    )
    assert cadastro.status_code in {302, 303}

    login = client.post(
        "/cadastro",
        data={
            "nome": "Teste Auth",
            "email": email,
        },
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    with client.session_transaction() as sess:
        assert sess.get("cliente_id") is not None
        assert sess.get("cliente_nome") == "Teste Auth"
