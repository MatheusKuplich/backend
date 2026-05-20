import urllib.request
import json
import time

time.sleep(1)

# Test POST /api/categorias
try:
    data = json.dumps({"nome": "Eletrônicos", "email": "eletro@example.com"}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/categorias',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req)
    print(f'✓ POST /api/categorias - Status: {response.status}')
    result = json.loads(response.read().decode())
    categoria_id = result['id']
    print(f'  Categoria criada: {result}')
except Exception as e:
    print(f'✗ POST /api/categorias - Erro: {e}')
    categoria_id = 1

# Test POST /api/produtos
try:
    data = json.dumps({"nome": "Notebook", "codigo": "NB-001", "categoria_id": categoria_id}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/produtos',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req)
    print(f'✓ POST /api/produtos - Status: {response.status}')
    result = json.loads(response.read().decode())
    produto_id = result['id']
    print(f'  Produto criado: {result}')
except Exception as e:
    print(f'✗ POST /api/produtos - Erro: {e}')
    produto_id = 1

# Test POST /api/clientes
try:
    data = json.dumps({"nome": "João Silva", "email": "joao@example.com", "produto_id": produto_id}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/clientes',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req)
    print(f'✓ POST /api/clientes - Status: {response.status}')
    result = json.loads(response.read().decode())
    print(f'  Cliente criado: {result}')
except Exception as e:
    print(f'✗ POST /api/clientes - Erro: {e}')

# Verify GET endpoints with data
print("\n--- Verificando dados cadastrados ---")

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/categorias')
    print(f'✓ GET /api/categorias - Status: {response.status}')
    data = json.loads(response.read().decode())
    print(f'  Categorias: {data}')
except Exception as e:
    print(f'✗ GET /api/categorias - Erro: {e}')

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/produtos')
    print(f'✓ GET /api/produtos - Status: {response.status}')
    data = json.loads(response.read().decode())
    print(f'  Produtos: {data}')
except Exception as e:
    print(f'✗ GET /api/produtos - Erro: {e}')

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/clientes')
    print(f'✓ GET /api/clientes - Status: {response.status}')
    data = json.loads(response.read().decode())
    print(f'  Clientes: {data}')
except Exception as e:
    print(f'✗ GET /api/clientes - Erro: {e}')

print("\nTeste completo finalizado!")
