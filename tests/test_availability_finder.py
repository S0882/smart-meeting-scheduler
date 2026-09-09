import unittest
from datetime import datetime
from unittest.mock import MagicMock
from models.event import Event
from services.availability_finder import AvailabilityFinder


class TestAvailabilityFinder(unittest.TestCase):
    """Unit tests for the availability search logic and repository independence."""

    def setUp(self):
        self.finder = AvailabilityFinder(work_start_hour=9, work_end_hour=17)

    def test_find_slots_no_events(self):
        """1. Verify slots are found when participants have no existing events."""
        events = []
        target_people = ["Alice"]
        slots = self.finder.find_available_slots(events, target_people, duration_minutes=60)

        self.assertTrue(len(slots) > 0)
        self.assertEqual(slots[0].start_time.strftime("%H:%M"), "09:00")

    def test_find_slots_with_conflict(self):
        """2. Verify overlapping time slots are excluded when a conflict exists."""
        events = [
            Event(
                person_name="Alice",
                subject="Busy",
                start_time="09:00",
                end_time="10:00",
                event_date="2026-09-09"
            )
        ]
        target_people = ["Alice"]
        slots = self.finder.find_available_slots(events, target_people, duration_minutes=30)

        # Verify that 09:00 - 09:30 is not in the available slots
        for slot in slots:
            self.assertNotEqual(slot.start_time.strftime("%H:%M"), "09:00")

    def test_find_slots_multiple_people(self):
        """3. Verify logic works for multiple participants with separate conflicts."""
        events = [
            Event("Alice", "Meeting A", "09:00", "10:00", "2026-09-09"),
            Event("Bob", "Meeting B", "10:00", "11:00", "2026-09-09")
        ]
        target_people = ["Alice", "Bob"]
        slots = self.finder.find_available_slots(events, target_people, duration_minutes=60)

        # First common available slot for 60 min should be 11:00
        self.assertTrue(len(slots) > 0)
        self.assertEqual(slots[0].start_time.strftime("%H:%M"), "11:00")

    def test_invalid_input_early_exit(self):
        """4. Verify early exit when target people list is empty."""
        slots = self.finder.find_available_slots([], [], duration_minutes=30)
        self.assertEqual(slots, [])

    def test_finder_with_mock_repository(self):
        """5. Verify business logic operates using a Mock Repository without loading external CSV files."""
        # Create a Fake/Mock Repository
        mock_repo = MagicMock()

        # Define simulated behavior - return events purely from memory
        mock_repo.load_events.return_value = [
            Event("Alice", "Sync", "09:00", "10:00", "2026-09-09"),
            Event("Bob", "Planning", "10:00", "11:00", "2026-09-09")
        ]

        # Fetch data via mock
        events = mock_repo.load_events()

        # Run availability finder logic
        slots = self.finder.find_available_slots(events, ["Alice", "Bob"], duration_minutes=60)

        # Validate results and confirm repository method invocation
        self.assertTrue(len(slots) > 0)
        self.assertEqual(slots[0].start_time.strftime("%H:%M"), "11:00")
        mock_repo.load_events.assert_called_once()


if __name__ == '__main__':
    unittest.main()