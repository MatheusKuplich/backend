"""
Script didático: DDL (create/drop tables) + DML (inserts) com sessão explícita.
Execute na raiz do projeto: python setup_database.py
"""

from datetime import datetime

from sqlalchemy import select

from database import Base, SessionLocal, engine
import models  # noqa: F401 — registra tabelas no metadata


def populate_database():
    print("Limpando e criando tabelas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()

    try:
        print("Inserindo professores...")
        professores = [
            models.Professor(nome="Maria Silva", email="maria@escola.example"),
            models.Professor(nome="João Santos", email="joao.santos@escola.example"),
        ]
        session.add_all(professores)
        session.flush()

        print("Inserindo turmas...")
        turmas = [
            models.Turma(
                nome="Matemática A",
                codigo="MAT-2026-A",
                professor_id=professores[0].id,
            ),
            models.Turma(
                nome="Física B",
                codigo="FIS-2026-B",
                professor_id=professores[0].id,
            ),
            models.Turma(
                nome="Português A",
                codigo="PORT-2026-A",
                professor_id=professores[1].id,
            ),
        ]
        session.add_all(turmas)
        session.flush()

        print("Inserindo alunos...")
        alunos = [
            models.Aluno(
                nome="Ana Costa",
                email="ana@escola.example",
                turma_id=turmas[0].id,
                endereco="asdasdsad"
            ),
            models.Aluno(
                nome="Bruno Lima",
                email="bruno@escola.example",
                turma_id=turmas[0].id,
                endereco="asdasdsad"
            ),
            models.Aluno(
                nome="Carla Dias",
                email="carla@escola.example",
                turma_id=turmas[1].id,
                endereco="asdasdsad"
            ),
            models.Aluno(
                nome="Diego Rocha",
                email="diego@escola.example",
                turma_id=turmas[2].id,
                endereco="asdasdsad"
            ),
        ]
        session.add_all(alunos)


        ######

        print("Inserindo Tipos...")
        tipos = [
            models.Tipo(
                nome="Eletronicos"
            ),
            models.Tipo(
                nome="Livros"
            ),
            models.Tipo(
                nome="Jogos"
            ),
            models.Tipo(
                nome="Esportes"
            ),
        ]
        session.add_all(tipos)
        session.flush()


####

        print("Inserindo Departamentos...")
        departamentos = [
            models.Departamento(
                nome="Contabilidade"
            ),
            models.Departamento(
                nome="Financeiro"
            ),
        ]
        session.add_all(departamentos)
        session.flush()

####

#####
        print("Inserindo TipoAnimais...")
        tipoAnimais = [
            models.TipoAnimal(
                nome="Canino"
            ),
            models.TipoAnimal(
                nome="Felino",
            ),
        ]
        session.add_all(tipoAnimais)
        session.flush()

###
        print("Inserindo Animais...")
        animais = [
            models.Animal(
                nome="Dante",
                id_tipo_animal=tipoAnimais[0].id,
                created_at=datetime.now(),
            ),
            models.Animal(
                nome="Toby",
                id_tipo_animal=tipoAnimais[1].id,
                created_at=datetime.now(),
            ),
        ]
        session.add_all(animais)
        session.flush()


###
        print("Inserindo funcionários...")
        funcionarios = [
            models.Funcionario(
                nome="Daniel Eletronicos",
                email="eletronico@gmail.com",
                senha="123456",
                id_departamento=departamentos[0].id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            models.Funcionario(
                nome="Daniel Livros",
                email="livro@gmail.com",
                senha="123456",
                id_departamento=departamentos[1].id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        session.add_all(funcionarios)

        print("Inserindo produtos...")
        primeiro_tipo_id = tipos[0].id
        produtos = [
            models.Produto(
                nome="Produto 1",
                preco=10.00,
                quantidade=10,
                descricao="Descrição 1",
                disponivel=True,
                id_tipo=primeiro_tipo_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            models.Produto(
                nome="Produto 2",
                preco=20.00,
                quantidade=20,
                descricao="Descrição 2",
                disponivel=True,
                id_tipo=primeiro_tipo_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        session.add_all(produtos)

        session.commit()
        print("\nSucesso! Commit concluído.")

        np = len(session.scalars(select(models.Professor)).all())
        nt = len(session.scalars(select(models.Turma)).all())
        na = len(session.scalars(select(models.Aluno)).all())
        print(f"- Professores: {np}")
        print(f"- Turmas: {nt}")
        print(f"- Alunos: {na}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    populate_database()
