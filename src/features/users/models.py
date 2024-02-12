from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models import Base

if TYPE_CHECKING:
    from src.features.referrals.models import ReferralCode


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str]
    password: Mapped[str]

    referrals: Mapped["ReferralCode"] = relationship(
        "ReferralCode",
        back_populates="owner",
        init=False,
    )
