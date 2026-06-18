from unittest.mock import MagicMock, patch
from servicos import cadastrar_categoria

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