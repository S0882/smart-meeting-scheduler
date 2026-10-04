import logging
from datetime import datetime, timedelta, date
from typing import List, Optional
from models.event import Event
from models.time_slot import TimeSlot
from repository.base_repository import BaseRepository
from config import DEFAULT_DAY_START, DEFAULT_DAY_END
from exceptions import PersonNotFoundError, InvalidTimeSlotError

# Initialize module-specific logger
logger = logging.getLogger(__name__)


class AvailabilityFinder:
    """Service responsible for finding available time slots for a single day using an injected repository."""

    def __init__(
        self,
        repository: BaseRepository,
        work_start_hour: Optional[int] = None,
        work_end_hour: Optional[int] = None
    ) -> None:
        # Inject the repository via constructor and use default values from config if needed
        self.repository = repository
        self.work_start_hour = work_start_hour if work_start_hour is not None else int(DEFAULT_DAY_START.split(":")[0])
        self.work_end_hour = work_end_hour if work_end_hour is not None else int(DEFAULT_DAY_END.split(":")[0])

    def find_available_slots(
        self,
        target_people: List[str],
        duration_minutes: int,
        target_date: Optional[date] = None
    ) -> List[TimeSlot]:
        """
        Loads events directly via the injected repository and finds available meeting slots.
        Validates participants against all repository events before filtering by target_date.
        """
        # Validate meeting duration
        if duration_minutes <= 0:
            logger.warning(f"Invalid duration provided: {duration_minutes}")
            raise InvalidTimeSlotError("Meeting duration must be greater than zero.")

        # Load all events internally through the injected repository
        events = self.repository.load_events()

        if not target_people:
            logger.warning("No target participants provided.")
            return []

        # 1. Validate that all requested participants exist in the FULL repository data (before date filtering)
        all_participants = {event.person_name for event in events}
        for person in target_people:
            if person not in all_participants:
                logger.warning(f"Participant not found in repository data: {person}")
                raise PersonNotFoundError(person)

        # 2. If a target date is provided, filter events for that specific date AFTER participant validation
        if target_date:
            date_str = target_date.strftime("%Y-%m-%d")
            events = [e for e in events if e.event_date == date_str]

        logger.debug(
            f"Searching daily availability for participants: {target_people} with duration: {duration_minutes} mins on date: {target_date}"
        )

        # 3. Conversion to set allows O(1) lookup time for each event check
        target_set = set(target_people)

        # 4. Filter events for target participants and sort them early (O(n log n))
        relevant_events = sorted(
            [event for event in events if event.person_name in target_set],
            key=lambda e: e.start_time
        )
        logger.debug(f"Filtered and sorted {len(relevant_events)} relevant events out of total events.")

        # 5. Define working hours for the current context
        start_of_day = datetime.strptime(f"{self.work_start_hour:02d}:00", "%H:%M")
        end_of_day = datetime.strptime(f"{self.work_end_hour:02d}:00", "%H:%M")

        available_slots: List[TimeSlot] = []
        current_time = start_of_day
        meeting_delta = timedelta(minutes=duration_minutes)

        # 6. Search for valid time slots
        while current_time + meeting_delta <= end_of_day:
            slot_end = current_time + meeting_delta
            has_conflict = False

            for event in relevant_events:
                # Check for overlap with existing scheduled events
                if not (slot_end <= event.start_time or current_time >= event.end_time):
                    has_conflict = True
                    break

            if not has_conflict:
                available_slots.append(
                    TimeSlot(start_time=current_time, end_time=slot_end)
                )

            # Move forward in 30-minute steps
            current_time += timedelta(minutes=30)

        logger.info(f"Daily search completed. Found {len(available_slots)} available time slot(s).")
        return available_slots