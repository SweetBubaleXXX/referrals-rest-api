from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base

from ..users.models import user_registration

if TYPE_CHECKING:
    from ..users.models import User


class ReferralCode(Base):
    __tablename__ = "referral_code"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), init=False)
    expiration_date: Mapped[date] = mapped_column(Date())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False,
    )

    owner: Mapped["User"] = relationship("User", back_populates="referrals", init=False)
    referees: Mapped[list["User"]] = relationship(
        secondary=user_registration,
        overlaps="registration_referral",
        init=False,
    )
