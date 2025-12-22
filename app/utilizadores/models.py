from __future__ import annotations
from flask_login import AnonymousUserMixin

import enum
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView
from flask import request, url_for, redirect, flash
from wtforms import SelectField
from app.extensions import Base, db


if TYPE_CHECKING:
    from app.academia.models import Turma, Inscricao
    from app.historico.models import HistoricoAlteracaoPerfil
    from app.pagamentos.models import Pagamento
    from app.academia.models import Presenca


# -----------------------------
# ENUMS
# -----------------------------
class Especialidade(str, enum.Enum):
    natacao = 'natacao'
    futebol = 'futebol'


class PerfilEnum(str, enum.Enum):
    administrador = 'administrador'
    professor = 'professor'
    aluno = 'aluno'
    cliente = 'cliente'


# -----------------------------
# TABELA PRINCIPAL: UTILIZADORES
# -----------------------------
class Utilizador(UserMixin, Base):
    __tablename__ = 'utilizadores'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    sobrenome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    telefone: Mapped[str] = mapped_column(
        String(15), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    perfil: Mapped[PerfilEnum] = mapped_column(
        Enum(PerfilEnum), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    data_nascimento: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Relações com tabelas auxiliares (1:1)
    dados_aluno: Mapped['DadosAluno'] = relationship('DadosAluno',
                                                     back_populates='utilizador', uselist=False, cascade='all, delete-orphan', lazy='joined')

    dados_professor: Mapped['DadosProfessor'] = relationship('DadosProfessor',
                                                             back_populates='utilizador', uselist=False, cascade='all, delete-orphan', lazy='joined')

    dados_cliente: Mapped['DadosCliente'] = relationship('DadosCliente',
                                                         back_populates='utilizador', uselist=False, cascade='all, delete-orphan', lazy='joined')

    dados_admin: Mapped['DadosAdministrador'] = relationship('DadosAdministrador',
                                                             back_populates='utilizador', uselist=False, cascade='all, delete-orphan', lazy='joined')

    historico_perfis: Mapped[List['HistoricoAlteracaoPerfil']] = relationship(
        'HistoricoAlteracaoPerfil', back_populates='utilizador', passive_deletes=True)

    pagamentos: Mapped[List['Pagamento']] = relationship('Pagamento',
                                                         back_populates='utilizador', cascade='all, delete-orphan', lazy='dynamic')

    # Métodos de segurança
    def definir_senha(self, palavra_passe: str):
        self.senha_hash = generate_password_hash(palavra_passe)

    def verificar_senha(self, palavra_passe: str) -> bool:
        return check_password_hash(self.senha_hash, palavra_passe)

    # Métodos para alterar a senha

    def alterar_perfil(self, novo_perfil, motivo):
        from app.historico.services import registar_alteracao_perfil

        perfil_antigo = self.perfil
        if perfil_antigo != novo_perfil:
            self.perfil = novo_perfil
            db.session.commit()
            registar_alteracao_perfil(
                self.id, motivo, perfil_antigo, novo_perfil)

    # Métodos para pegar os dados do utilizador
    def get_dados(self):
        if self.perfil == PerfilEnum.aluno:
            return self.dados_aluno
        elif self.perfil == PerfilEnum.professor:
            return self.dados_professor
        elif self.perfil == PerfilEnum.cliente:
            return self.dados_cliente
        elif self.perfil == PerfilEnum.administrador:
            return self.dados_admin
        return None

    @property
    def is_admin(self) -> bool:
        return self.perfil == PerfilEnum.administrador

    @property
    def is_aluno(self) -> bool:
        return self.perfil == PerfilEnum.aluno

    @property
    def is_professor(self) -> bool:
        return self.perfil == PerfilEnum.professor

    @property
    def is_cliente(self) -> bool:
        return self.perfil == PerfilEnum.cliente

    def __repr__(self):
        return f'<Utilizador: {self.email} ({self.perfil.value})>'


# -----------------------------
# DADOS ESPECÍFICOS POR PERFIL
# -----------------------------
class DadosAdministrador(Base):
    __tablename__ = 'dados_administradores'

    id: Mapped[int] = mapped_column(
        ForeignKey('utilizadores.id'), primary_key=True)
    utilizador: Mapped['Utilizador'] = relationship('Utilizador',
                                                    back_populates='dados_admin', lazy='joined')

    def __repr__(self):
        return f'<Administrador {self.utilizador.email}>'


class DadosProfessor(Base):
    __tablename__ = 'dados_professores'

    id: Mapped[int] = mapped_column(
        ForeignKey('utilizadores.id'), primary_key=True)
    especialidade: Mapped[Especialidade] = mapped_column(
        Enum(Especialidade), nullable=False)

    utilizador: Mapped['Utilizador'] = relationship(
        back_populates='dados_professor', lazy='joined')

    # Relação com Turmas
    turmas: Mapped[List['Turma']] = relationship(back_populates='professor')

    presencas: Mapped[List['Presenca']] = relationship(
        back_populates='professor')

    def __repr__(self):
        return f'<Professor {self.utilizador.email}>'


class DadosAluno(Base):
    __tablename__ = 'dados_alunos'

    id: Mapped[int] = mapped_column(
        ForeignKey('utilizadores.id'), primary_key=True)
    matricula: Mapped[int] = mapped_column(
        Integer, unique=True, autoincrement=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    utilizador: Mapped[Utilizador] = relationship(back_populates='dados_aluno')

    # Relação com inscrições
    inscricoes: Mapped[List[Inscricao]] = relationship(back_populates='aluno')

    presencas: Mapped[List['Presenca']] = relationship(
        back_populates='aluno')

    def __repr__(self):
        return f'<Aluno {self.utilizador.email}>'


class DadosCliente(Base):
    __tablename__ = 'dados_clientes'

    id: Mapped[int] = mapped_column(
        ForeignKey('utilizadores.id'), primary_key=True)
    utilizador: Mapped[Utilizador] = relationship(
        back_populates='dados_cliente', lazy='joined')

    def __repr__(self):
        return f'<Cliente {self.utilizador.email}>'


# -----------------------------
# FLASK-ADMIN VIEW
# -----------------------------
class ApenasAdminView(ModelView):
    base_form_columns = ['nome', 'sobrenome', 'perfil', 'data_nascimento']
    form_overrides = dict(perfil=SelectField)
    form_args = dict(
        perfil=dict(
            choices=[(e.value, e.name.capitalize()) for e in PerfilEnum]
        )
    )

    def __init__(self, model, session, **kwargs):
        super().__init__(model, session, **kwargs)
        available = set()
        # campos da tabela do próprio model
        if hasattr(model, '__table__'):
            available |= {c.name for c in model.__table__.columns}
        # também aceitar atributos/props na classe
        available |= set(dir(model))
        # filtrar apenas os campos disponíveis
        self.form_columns = [
            c for c in self.base_form_columns if c in available]

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('autenticacao.login', next=request.url))


class Anonymous(AnonymousUserMixin):
    perfil = None  # ou PerfilEnum.cliente, conforme desejado
