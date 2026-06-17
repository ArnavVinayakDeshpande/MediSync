"""

"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


def calculate_expected_delivery_date(last_menstrual_period_date: date) -> date:
    return last_menstrual_period_date + timedelta(weeks = 40)

@dataclass
class PregnancyData:
    patient_id: str
    last_menstrual_period_date: date
    expected_delivery_date: date = field(init = False)
    delivery_date: datetime | None = None
    created_at: datetime = field(default_factory = datetime.now)

    def __post_init__(self) -> None:
        self.expected_delivery_date: date = calculate_expected_delivery_date(
            last_menstrual_period_date = self.last_menstrual_period_date
        )

    @property
    def current_week(self) -> int:
        clamp = lambda x, mi, mx: min(mx, max(mi, x))

        return clamp(
            ((date.today() - self.last_menstrual_period_date).days // 7) + 1,
            0, 40
        )

    @property
    def has_delivered(self) -> bool:
        return (
            self.delivery_date is not None and
            self.delivery_date <= datetime.now()
        )

