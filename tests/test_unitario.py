from servicos import _texto_obrigatorio
import pytest

def test_texto_obrigatorio_valido():
    resultado = _texto_obrigatorio("Texto válido", "campo")
    assert resultado == "Texto válido"
    
def test_texto_obrigatorio_vazio():
    with pytest.raises(ValueError):
        _texto_obrigatorio("", "campo")