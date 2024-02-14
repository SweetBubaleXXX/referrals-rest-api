from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, FutureDate


class ReferralCodeIn(BaseModel):
    expiration_date: FutureDate


class ReferralCodeOut(BaseModel):
    id: UUID
    owner_id: int
    expiration_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
