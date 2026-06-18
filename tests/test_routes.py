import urllib.request
import json
import time

time.sleep(3)

# Test GET /api/categorias
try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/categorias')
    print(f'✓ GET /api/categorias - Status: {response.status}')
    data = json.loads(response.read().decode())
    print(f'  Response: {data}')
except Exception as e:
    print(f'✗ GET /api/categorias - Erro: {e}')

# Test GET /api/produtos
try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/produtos')
    print(f'✓ GET /api/produtos - Status: {response.status}')
    data = json.loads(response.read().decode())
    print(f'  Response: {data}')
except Exception as e:
    print(f'✗ GET /api/produtos - Erro: {e}')

# Test GET /api/clientes
try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/clientes')
    print(f'✓ GET /api/clientes - Status: {response.status}')
    data = json.loads(response.read().decode())
    print(f'  Response: {data}')
except Exception as e:
    print(f'✗ GET /api/clientes - Erro: {e}')

# Test GET /
try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/')
    print(f'✓ GET / - Status: {response.status}')
except Exception as e:
    print(f'✗ GET / - Erro: {e}')

print("\nTodas as rotas testadas!")
