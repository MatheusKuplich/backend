#!/usr/bin/env python
"""
Script para fazer commit de todas as mudanças e criar uma PR (ou fazer push direto).
Uso:
  python commit_changes.py [--push] [--pr]
  
Flags:
  --push: fazer push para remote (default main)
  --pr: criar PR (requer github CLI - gh)
"""
import subprocess
import sys
import os
from datetime import datetime

def run_cmd(cmd, check=True):
    """Executa comando e retorna output."""
    print(f"► {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Comando falhou: {' '.join(cmd)}")
    return result

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    push = '--push' in sys.argv
    create_pr = '--pr' in sys.argv
    
    print("=" * 60)
    print("Commit de Mercado StarWars - Marketplace Home")
    print("=" * 60)
    
    # 1) Verificar status
    print("\n[1] Status do repositório:")
    run_cmd(['git', 'status', '-s'])
    
    # 2) Adicionar arquivos
    print("\n[2] Adicionando arquivos modificados:")
    run_cmd(['git', 'add', '-A'])
    run_cmd(['git', 'status'])
    
    # 3) Criar commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"""feat: Marketplace homepage com quick-view, filtros e SEO

- Corrigir hero (remover sobreposição de títulos)
- Remover categorias indesejadas (Eletrônicos, Figuras, Mídias, Posters)
- Implementar Quick-view modal para visualização rápida de produtos
- Adicionar handler "Comprar" com opção de quantidade
- Implementar paginação (8 itens por página) na seção "Mais Produtos"
- Adicionar filtros por categoria
- Adicionar JSON-LD structured data para SEO
- Adicionar meta tags OpenGraph
- Criar endpoint /api/produtos/destaques (já estava)
- Atualizar home.js com fetch de destaques, categorias e pagination
- Atualizar home.html com modal, filtros e seção de paginação

Timestamp: {timestamp}
"""
    
    print(f"\n[3] Criando commit:")
    print(f"Mensagem: {message[:100]}...")
    run_cmd(['git', 'commit', '-m', message])
    
    # 4) Push (opcional)
    if push:
        print("\n[4] Fazendo push para remote:")
        branch = run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()
        run_cmd(['git', 'push', 'origin', branch])
        print(f"✓ Commit feito push para '{branch}'")
    else:
        print("\n[4] Skipping push (use --push para fazer)")
    
    # 5) PR (opcional)
    if create_pr:
        print("\n[5] Criando PR (requer 'gh' CLI):")
        try:
            run_cmd(['gh', 'pr', 'create', '--title', 'feat: Marketplace homepage',
                     '--body', message, '--base', 'main'])
            print("✓ PR criada com sucesso!")
        except Exception as e:
            print(f"⚠ Erro ao criar PR: {e}")
            print("  Instalei 'gh'? https://github.com/cli/cli")
    else:
        print("\n[5] Skipping PR creation (use --pr para criar)")
    
    print("\n" + "=" * 60)
    print("✓ Commit concluído com sucesso!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Erro: {e}", file=sys.stderr)
        sys.exit(1)
