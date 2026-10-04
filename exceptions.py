class CalendarError(Exception):
    """Base exception for all calendar application errors."""
    pass

class PersonNotFoundError(CalendarError):
    """Raised when a requested participant does not exist in the system."""
    def __init__(self, person_name: str):
        super().__init__(f"Participant '{person_name}' was not found in the calendar.")
        self.person_name = person_name

class InvalidTimeSlotError(CalendarError):
    """Raised when meeting duration or time range is invalid."""
    pass

class RepositoryError(CalendarError):
    """Raised when loading or parsing the repository data fails."""
    pass