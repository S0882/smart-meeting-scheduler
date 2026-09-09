import unittest
from datetime import datetime, date
from dataclasses import FrozenInstanceError
from models.event import Event
from models.time_slot import TimeSlot

class TestImmutableModels(unittest.TestCase):
    """Unit tests to verify that Event and TimeSlot models are immutable."""

    def test_event_immutability(self):
        event = Event(
            person_name="Alice",
            subject="Sync Meeting",
            start_time="09:00",
            end_time="10:00",
            event_date="2026-09-09"
        )

        self.assertEqual(event.person_name, "Alice")
        self.assertEqual(event.event_date, date(2026, 9, 9))

        # Test immutability via setattr to avoid static Linter/IDE errors
        with self.assertRaises(FrozenInstanceError):
            setattr(event, 'person_name', "Bob")

        with self.assertRaises(FrozenInstanceError):
            setattr(event, 'start_time', datetime.strptime("10:00", "%H:%M"))

    def test_time_slot_immutability(self):
        start = datetime.strptime("14:00", "%H:%M")
        end = datetime.strptime("15:00", "%H:%M")
        slot = TimeSlot(start_time=start, end_time=end)

        self.assertEqual(str(slot), "14:00 - 15:00")

        with self.assertRaises(FrozenInstanceError):
            setattr(slot, 'start_time', datetime.strptime("10:00", "%H:%M"))

        with self.assertRaises(FrozenInstanceError):
            setattr(slot, 'end_time', datetime.strptime("11:00", "%H:%M"))

if __name__ == '__main__':
    unittest.main()