from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base

if TYPE_CHECKING:
    from src.features.referrals.models import ReferralCode

user_registration = Table(
    "user_registration",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("code_id", ForeignKey("referral_code.id"), nullable=False),
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str]
    password: Mapped[str]

    referrals: Mapped[list["ReferralCode"]] = relationship(
        "ReferralCode",
        back_populates="owner",
        init=False,
    )
    registration_referral: Mapped["ReferralCode | None"] = relationship(
        secondary=user_registration,
        init=False,
    )
