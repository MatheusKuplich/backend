def soma(a, b):
    return a + b

def test_soma_positiva():
    # Testa se a soma de dois números positivos está correta
    assert soma(2, 3) == 5

def test_soma_negativa():
    # Testa se a soma com número negativo funciona
    assert soma(2, -1) == 1