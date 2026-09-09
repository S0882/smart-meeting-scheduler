from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class TimeSlot:
    """Represents an immutable time slot with start and end times."""
    start_time: datetime
    end_time: datetime

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"