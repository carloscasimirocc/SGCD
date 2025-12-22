from app.app import create_app, db
from app.utilizadores.models import Utilizador
from sqlalchemy.exc import SQLAlchemyError


app = create_app()

with app.app_context():

    def actualizar(chave_filtro, valor_filtro, chave_update, valor_update):

        if hasattr(Utilizador, chave_filtro):
            user = db.session.query(Utilizador).filter(
                getattr(Utilizador, chave_filtro) == valor_filtro).first()

            if user:
                try:
                    setattr(user, chave_update, valor_update)
                    db.session.add(user)
                    db.session.commit()
                    return f'actualização feita com sucesso'

                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'erro': f'erro ao actualizar {(e)}'}, 500

            else:
                return 'utilizador não encontrado', 404

        else:
            return 'atributo não existe', 400


"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Boolean
from wtforms import SelectField
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect, flash
from app.extensions import db
from app.academia.models import Turma, Inscricao
from typing import List, Any


class Especialidade(str, enum.Enum):
    natacao = 'natacao'
    futebol = 'futebol'


class PerfilEnum(str, enum.Enum):
    administrador = 'administrador'
    professor = 'professor'
    aluno = 'aluno'
    cliente = 'cliente'


class Utilizador(UserMixin, Base):
    __tablename__ = 'utilizadores'

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100),
                                      nullable=False)
    sobrenome: Mapped[str] = mapped_column(String(100),
                                           nullable=False)
    email: Mapped[str] = mapped_column(String(120),
                                       unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(128),
                                            nullable=False)

    telefone: Mapped[str] = mapped_column(String(15),
                                          unique=True, nullable=False)
    perfil: Mapped[str] = mapped_column(String(15))
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )

    data_nascimento: Mapped[datetime] = mapped_column(Date, nullable=True)

    def definir_senha(self, palavra_passe: str):
        self.senha_hash = generate_password_hash(palavra_passe)

    def verificar_senha(self, palavra_passe: str) -> bool:
        return check_password_hash(self.senha_hash, palavra_passe)

    @property
    def is_admin(self) -> bool:
        """"""Verifica se o utilizador tem perfil de administrador.'''
        return self.perfil == PerfilEnum.administrador

    __mapper_args__ = {
        'polymorphic_on': perfil,
        "polymorphic_identity": 'utilizador',
    }

    def __repr__(self):
        return f'<Utilizador: {self.email}>'


class Administrador(Utilizador):
    __tablename__ = 'administradores'

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey('utilizadores.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': PerfilEnum.administrador.value,
    }

    def __repr__(self):
        return f'<Administrador {self.email}>'


class Professor(Utilizador):
    __tablename__ = 'professores'

    id: Mapped[int] = mapped_column(Integer,
                                    ForeignKey('utilizadores.id'), primary_key=True)

    especialidade: Mapped[Especialidade] = mapped_column(
        Enum(Especialidade), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': PerfilEnum.professor.value,
    }

    # Definir a relação "1 para muitos" a partir de Professor para Turma
    turmas: Mapped[Turma] = relationship(
        back_populates='professor')

    def __repr__(self):
        return f'<Professor {self.email}>'


class Aluno(Utilizador):
    __tablename__ = 'alunos'

    id: Mapped[int] = mapped_column(Integer,
                                    ForeignKey('utilizadores.id'), primary_key=True)

    matricula: Mapped[int] = mapped_column(Integer,
                                           unique=True, autoincrement=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': PerfilEnum.aluno.value,
    }

    # Definir a relação "muitos para 1" a partir de Inscricao para Aluno
    inscricoes: Mapped[List[Inscricao]] = relationship(
        back_populates='aluno')

    def __repr__(self):
        return f'<Aluno {self.email}>'


class Cliente(Utilizador):
    __tablename__ = 'clientes'

    id: Mapped[int] = mapped_column(Integer,
                                    ForeignKey('utilizadores.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': PerfilEnum.cliente.value,
    }

    def __repr__(self):
        return f'<Cliente {self.email}>'


class ApenasAdminView(ModelView):

    can_create = True
    can_edit = True
    can_delete = True
    can_update = True
    form_columns = ['nome', 'sobrenome',
                    'perfil', 'data_nascimento']
    form_overrides = dict(perfil=SelectField)
    form_args = dict(
        perfil=dict(
            choices=[(e.value, e.name.capitalize()) for e in PerfilEnum]
        )
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('autenticacao.login', next=request.url))

"""
