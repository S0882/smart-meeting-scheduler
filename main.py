import logging
from datetime import datetime, date
from repository.csv_repository import CSVRepository
from services.availability_finder import AvailabilityFinder
from services.week_finder import WeekFinder
from services.month_finder import MonthFinder
from exceptions import (
    CalendarError,
    RepositoryError,
    PersonNotFoundError,
    InvalidTimeSlotError
)

# Configure global logging settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),  # Save logs to file
        logging.StreamHandler()  # Output logs to console
    ]
)

# Initialize module-specific logger
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Smart Meeting Scheduler application.")

    # 1. Initialize the CSV repository and inject it into the AvailabilityFinder
    try:
        repository = CSVRepository("repository/calendar.csv")
        # Constructor Injection: passing the repository directly to AvailabilityFinder
        daily_finder = AvailabilityFinder(repository=repository)

        # Load events from repository to display available participants
        events = repository.load_events()
        logger.info(f"Successfully loaded {len(events)} events from repository.")

    except RepositoryError as e:
        logger.error(f"Repository error occurred: {e}", exc_info=True)
        print(f"Error: {e}")
        return
    except Exception as e:
        logger.error(f"Failed to load calendar repository: {e}", exc_info=True)
        print("Error loading calendar data. Exiting program.")
        return

    # Extract all unique participants available in the calendar data
    all_people = list({event.person_name for event in events})

    print("=== Smart Meeting Scheduler ===")
    print(f"Available participants in system: {', '.join(all_people)}\n")

    # 2. Get participant names and meeting duration
    raw_people = input("Enter participant names (comma-separated, e.g., Alice, Bob): ")
    target_people = [p.strip() for p in raw_people.split(",") if p.strip()]

    if not target_people:
        logger.warning("No target participants provided by user.")
        print("No participants were provided. Exiting program.")
        return

    try:
        meeting_duration = int(input("Enter meeting duration in minutes (e.g., 30): "))
        logger.info(f"Target participants: {target_people}, Duration: {meeting_duration} minutes")
    except ValueError:
        logger.error("Invalid input for meeting duration. Integer expected.")
        print("Invalid input. Meeting duration must be an integer.")
        return

    # 3. Select Search Mode
    print("\nSelect Search Mode:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    search_mode = input("Choose mode (1, 2, or 3): ").strip()

    try:
        # --- DAILY SEARCH ---
        if search_mode == "1":
            logger.info("Executing Daily Search mode.")
            print(f"\n=== Daily Search for: {', '.join(target_people)} ===")
            slots = daily_finder.find_available_slots(target_people, meeting_duration)

            if slots:
                logger.info(f"Daily search completed. Found {len(slots)} slots.")
                print(f"Found {len(slots)} available slot(s) for today:")
                for slot in slots:
                    print(f" - 🕒 {slot}")
            else:
                logger.info("Daily search completed. No available slots found.")
                print("No available slots found for today.")

        # --- WEEKLY SEARCH ---
        elif search_mode == "2":
            logger.info("Executing Weekly Search mode.")
            start_date_str = input("Enter week start date (YYYY-MM-DD, e.g., 2026-09-07): ").strip()
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                logger.error(f"Invalid date format provided: {start_date_str}")
                print("Invalid date format. Expected YYYY-MM-DD.")
                return

            week_finder = WeekFinder(base_finder=daily_finder)
            weekly_result = week_finder.find_for_week(
                events=events,
                target_people=target_people,
                duration_minutes=meeting_duration,
                start_of_week=start_date
            )

            logger.info(f"Weekly search completed for week {weekly_result.week_number}.")
            print(f"\n=== Weekly Results for Week {weekly_result.week_number} ===")
            for day in weekly_result.days:
                print(f"\nDate {day.day_date}:")
                if day.available_slots:
                    for slot in day.available_slots:
                        print(f" - {slot}")
                else:
                    print(" No available slots.")

        # --- MONTHLY SEARCH ---
        elif search_mode == "3":
            logger.info("Executing Monthly Search mode.")
            try:
                year = int(input("Enter year (e.g., 2026): "))
                month = int(input("Enter month number (1-12): "))
            except ValueError:
                logger.error("Invalid input for year or month.")
                print("Invalid input for year or month.")
                return

            month_finder = MonthFinder(week_finder=WeekFinder(base_finder=daily_finder))
            monthly_result = month_finder.find_for_month(
                events=events,
                target_people=target_people,
                duration_minutes=meeting_duration,
                year=year,
                month=month
            )

            logger.info(f"Monthly search completed for {monthly_result.year}-{monthly_result.month:02d}.")
            print(f"\n=== Monthly Results for {monthly_result.year}-{monthly_result.month:02d} ===")
            for week in monthly_result.weeks:
                print(f"\n--- Week {week.week_number} ---")
                for day in week.days:
                    print(f" Date {day.day_date}:")
                    if day.available_slots:
                        for slot in day.available_slots:
                            print(f"   - 🕒 {slot}")
                    else:
                        print("   No available slots.")

        else:
            logger.warning(f"Invalid search mode selected: {search_mode}")
            print("Invalid selection. Exiting.")

    except PersonNotFoundError as e:
        logger.error(f"Participant search error: {e}")
        print(f"Error: {e}")
    except InvalidTimeSlotError as e:
        logger.error(f"Invalid time slot error: {e}")
        print(f"Error: {e}")
    except CalendarError as e:
        logger.error(f"Application error occurred: {e}", exc_info=True)
        print(f"System Error: {e}")

    logger.info("Smart Meeting Scheduler application finished execution.")


if __name__ == "__main__":
    main()