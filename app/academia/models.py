from __future__ import annotations
import enum
from datetime import datetime, timezone, time

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base
from typing import List


class DiaSemanaEnum(enum.Enum):
    segunda = 'Segunda'
    terca = 'Terça'
    quarta = 'Quarta'
    quinta = 'Quinta'
    sexta = 'Sexta'
    sabado = 'Sábado'
    domingo = 'Domingo'


class Modalidade(Base):
    __tablename__ = 'modalidades'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True
                                    )
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(Text(), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Definir a relação "1 para muitos" a partir de Modalidade para TipoTreino
    tipos_treino: Mapped[List['TipoTreino']] = relationship(
        back_populates='modalidade')

    def __repr__(self) -> str:
        return f'<Modalidade: {self.nome}>'


class TipoTreino(Base):
    __tablename__ = 'tipos_treino'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(Text(), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    modalidade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('modalidades.id'))

    # DefinirDefinir a relação "muitos para 1" a partir de TipoTreino para Modalidade
    modalidade: Mapped['Modalidade'] = relationship(
        back_populates='tipos_treino')

    # Definir a relação "1 para muitos" a partir de TipoTreino para Turma
    turmas: Mapped[List['Turma']] = relationship(
        back_populates='tipo_treino')


class CategoriaIdade(Base):
    __tablename__ = 'categorias_idade'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    idade_min: Mapped[int] = mapped_column(Integer, nullable=False)
    idade_max: Mapped[int] = mapped_column(Integer, nullable=False)

    # Definir a relação "1 para muitos" a partir de CategoriaIdade para Turma
    turmas: Mapped[List['Turma']] = relationship(
        back_populates='categoria_idade')

    def __repr__(self) -> str:
        return f'< {self.nome} | {self.idade_min} - {self.idade_max} anos>'


class Turma(Base):
    __tablename__ = 'turmas'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tipo_treino_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('tipos_treino.id'))
    categoria_idade_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('categorias_idade.id'))
    professor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('dados_professores.id'))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Definir a relação "muitos para 1" a partir de Turma para TipoTreino
    tipo_treino: Mapped['TipoTreino'] = relationship(
        back_populates='turmas')

    # Definir a relação "muitos para 1" a partir de Turma para CategoriaIdade
    categoria_idade: Mapped['CategoriaIdade'] = relationship(
        back_populates='turmas')

    # Definir a relação "muitos para 1" a partir de Turma para Professor
    professor: Mapped['DadosProfessor'] = relationship(  # type: ignore
        back_populates='turmas')

    # Definir a relação "1 para muitos" a partir de Turma para Horario
    horarios: Mapped[List['Horario']] = relationship(back_populates='turma')

    # Definir a relação "1 para muitos" a partir de Turma para inscricao
    inscricoes: Mapped[List['Inscricao']] = relationship(
        back_populates='turma')

    # Definir a relação "1 para muitos" a partir de Turma para presenca
    presencas: Mapped[List['Presenca']] = relationship(back_populates='turma')

    def __repr__(self) -> str:
        return f'<Turma: {self.nome} | Activo: {self.activo}>'


class Horario(Base):
    __tablename__ = 'horarios'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    turma_id: Mapped[int] = mapped_column(Integer, ForeignKey('turmas.id'))
    dia_semana: Mapped[DiaSemanaEnum] = mapped_column(
        Enum(DiaSemanaEnum, name='dia_semana_enum'), nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[time] = mapped_column(Time, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Definir a relação "muitos para 1" a partir de Horario para Turma
    turma: Mapped['Turma'] = relationship(back_populates='horarios')

    def __repr__(self):
        return f'<Horario {self.dia_semana} | {self.hora_inicio}-{self.hora_fim}>'


class Inscricao(Base):
    __tablename__ = 'inscricoes'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    aluno_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('dados_alunos.id'), nullable=False)
    turma_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('turmas.id'), nullable=False)
    data_inscricao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Definir a relação "muitos para 1" a partir de Inscricao para Aluno
    aluno: Mapped['DadosAluno'] = relationship(  # type: ignore
        back_populates='inscricoes')

    # Definir a relação "muitos para 1" a partir de Inscricao para Turma
    turma: Mapped['Turma'] = relationship(back_populates='inscricoes')

    def cancelar(self):
        from app.utilizadores.models import PerfilEnum
        self.activo = False
        self.aluno.perfil = PerfilEnum.cliente

    def __repr__(self):
        return f'<Inscrição do aluno: {self.aluno_id} | Turma: {self.turma_id} | data da inscrição: {self.data_inscricao}>'


class Presenca(Base):
    __tablename__ = 'presencas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[int] = mapped_column(
        DateTime, nullable=False, default=datetime.now(timezone.utc))
    presente: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)

    aluno_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('dados_alunos.id'), nullable=False)
    turma_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('turmas.id'), nullable=False)
    professor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('dados_professores.id'), nullable=False)

    # Relações (ORM)
    from app.utilizadores.models import DadosAluno, DadosProfessor

    aluno: Mapped['DadosAluno'] = relationship(
        'DadosAluno', back_populates='presencas')
    turma: Mapped['Turma'] = relationship(back_populates='presencas')
    professor: Mapped['DadosProfessor'] = relationship(
        'DadosProfessor', back_populates='presencas')
