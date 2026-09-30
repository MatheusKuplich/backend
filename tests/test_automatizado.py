import pytest
from unittest.mock import MagicMock, patch
from servicos import cadastrar_categoria, remover_categoria

def test_cadastrar_categoria_valido():
    
    cadastro_fake = MagicMock()
    
    #Arrange
    cadastro_fake.to_dict.return_value = {
        "id": 1, 
        "nome": "Eletrônicos",
        "email": "cadastro@gmail.com"
    }
    
    session_fake = MagicMock()
    # Act
    with patch("servicos.SessionLocal", return_value=session_fake):
        with patch("servicos.Categoria", return_value=cadastro_fake):
        
            resultado = cadastrar_categoria({
                "nome": "Eletrônicos",
                "email": "cadastro@gmail.com"
            })
            
    # Assert
    assert resultado["nome"] == "Eletrônicos"


def test_remover_categoria_padrao_nao_permitido():
    categoria_fake = MagicMock()
    categoria_fake.id = 1
    categoria_fake.nome = "Padrão"

    session_fake = MagicMock()
    session_fake.get.return_value = categoria_fake

    with patch("servicos.SessionLocal", return_value=session_fake):
        with pytest.raises(ValueError, match="não pode ser removida"):
            remover_categoria(1)