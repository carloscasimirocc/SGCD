from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import Base


class Mensagem(Base):
    __tablename__ = 'mensagens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    data_envio: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc))
