from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Union

@dataclass(frozen=True)
class Event:
    """Represents an immutable calendar event with associated date and times."""
    person_name: str
    subject: str
    start_time: Union[str, datetime]
    end_time: Union[str, datetime]
    event_date: Optional[Union[str, date]] = None
    time_format: str = "%H:%M"
    date_format: str = "%Y-%m-%d"

    def __post_init__(self):
        # Clean string inputs
        object.__setattr__(self, 'person_name', self.person_name.strip())
        object.__setattr__(self, 'subject', self.subject.strip())

        # Parse start_time string to datetime object if necessary
        if isinstance(self.start_time, str):
            parsed_start = datetime.strptime(self.start_time.strip(), self.time_format)
            object.__setattr__(self, 'start_time', parsed_start)

        # Parse end_time string to datetime object if necessary
        if isinstance(self.end_time, str):
            parsed_end = datetime.strptime(self.end_time.strip(), self.time_format)
            object.__setattr__(self, 'end_time', parsed_end)

        # Parse event_date string to date object if necessary
        if isinstance(self.event_date, str) and self.event_date.strip():
            parsed_date = datetime.strptime(self.event_date.strip(), self.date_format).date()
            object.__setattr__(self, 'event_date', parsed_date)