"""
Serviços de autenticação: login, registro, hash de senha, verificação de token.
"""

import re
import secrets

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from database import SessionLocal
from models import Cliente


def _email_valido(email):
    if email is None:
        return False

    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()))

def registrar_cliente(nome, email, senha):
    """Registra um novo cliente com senha criptografada."""
    if not _email_valido(email):
        raise ValueError("Informe um e-mail válido para criar a conta.")

    session = SessionLocal()
    try:
        # Verificar se cliente já existe
        cliente_existente = session.scalars(
            select(Cliente).where(Cliente.email == email.lower().strip())
        ).first()
        
        if cliente_existente:
            raise ValueError(f"Email '{email}' já está cadastrado.")
        
        # Hash da senha
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        
        # Criar cliente
        cliente = Cliente(
            nome=nome.strip(),
            email=email.lower().strip(),
            senha_hash=senha_hash
        )
        
        session.add(cliente)
        session.commit()
        session.refresh(cliente)
        
        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "token": gerar_token_sessao(cliente.id)  # Retorna token de sessão
        }
    
    except Exception:
        session.rollback()
        raise
    
    finally:
        session.close()


def login_cliente(email, senha):
    """Faz login do cliente e retorna token de sessão."""
    session = SessionLocal()
    try:
        cliente = session.scalars(
            select(Cliente).where(Cliente.email == email.lower().strip())
        ).first()
        
        if not cliente:
            raise ValueError("Email ou senha incorretos.")
        
        # Verificar senha
        if not check_password_hash(cliente.senha_hash or "", senha):
            raise ValueError("Email ou senha incorretos.")
        
        # Gerar token de sessão
        token = gerar_token_sessao(cliente.id)
        
        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "token": token
        }
    
    finally:
        session.close()


def login_por_nome_email(nome, email):
    """Autentica um cliente usando nome + e-mail no fluxo simplificado de acesso."""
    if not _email_valido(email):
        raise ValueError("Informe um e-mail válido para entrar.")

    session = SessionLocal()
    try:
        cliente = session.scalars(
            select(Cliente).where(Cliente.email == email.lower().strip())
        ).first()

        if not cliente:
            raise ValueError("Nome ou e-mail incorretos.")

        if cliente.nome.strip().lower() != nome.strip().lower():
            raise ValueError("Nome ou e-mail incorretos.")

        token = gerar_token_sessao(cliente.id)

        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "token": token,
        }
    finally:
        session.close()


def gerar_token_sessao(cliente_id):
    """Gera um token de sessão (JWT simples ou string aleatória)."""
    # Para simplicidade, usar uma string aleatória (em produção usar JWT)
    return secrets.token_urlsafe(32)


def verificar_cliente_autenticado(cliente_id):
    """Verifica se cliente existe e está ativo."""
    session = SessionLocal()
    try:
        cliente = session.get(Cliente, int(cliente_id))
        if cliente is None:
            raise ValueError(f"Cliente {cliente_id} não encontrado.")
        
        return cliente.to_dict()
    
    finally:
        session.close()
