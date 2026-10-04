import csv
import logging
from datetime import date
from typing import List
from models.event import Event
from repository.base_repository import BaseRepository
from exceptions import RepositoryError  # Import custom exception

# Initialize the module-specific logger for tracking data layer operations
logger = logging.getLogger(__name__)


class CSVRepository(BaseRepository):
    """Repository implementation to load calendar events from a CSV file."""

    def __init__(self, file_path: str):
        """Initializes the repository with the target CSV file path."""
        self.file_path = file_path

    def load_events(self) -> List[Event]:
        """
        Loads and parses calendar events from the configured CSV file.
        Returns a list of Event objects.
        """
        logger.debug(f"Attempting to load events from CSV file: {self.file_path}")
        events = []

        # Define a fallback date (today's date) if the event date column is empty
        today_str = date.today().strftime("%Y-%m-%d")

        try:
            # Open the CSV file safely with UTF-8 encoding
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Skip the CSV header row
                logger.debug(f"CSV header successfully skipped: {header}")

                # Iterate through each row in the CSV file
                for row in reader:
                    # Ensure the row contains enough columns for basic event data
                    if len(row) >= 4:
                        # Check if the date column exists and is not empty
                        has_date = len(row) > 4 and row[4].strip()

                        # Assign the event date (use provided value or fallback to today)
                        event_date_val = row[4].strip() if has_date else today_str

                        # Instantiate the Event object and add it to the list
                        event = Event(
                            person_name=row[0],
                            subject=row[1],
                            start_time=row[2],
                            end_time=row[3],
                            event_date=event_date_val
                        )
                        events.append(event)
                    else:
                        # Log a warning for malformed rows instead of crashing
                        logger.warning(f"Skipping malformed row with insufficient columns: {row}")

            logger.info(f"Successfully loaded {len(events)} events from {self.file_path}.")
            return events

        except FileNotFoundError as e:
            logger.error(f"CSV file not found at path: {self.file_path}")
            raise RepositoryError(f"CSV file not found at path: {self.file_path}") from e
        except Exception as e:
            logger.error(f"Error reading or parsing CSV file {self.file_path}: {e}", exc_info=True)
            raise RepositoryError(f"Error reading or parsing CSV file {self.file_path}: {e}") from e