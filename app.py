import streamlit as st
from datetime import date
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

# Page configuration
st.set_page_config(page_title="Meeting Scheduler", layout="wide")

st.title("📅 Smart Meeting Scheduler")


# 1. Initialize Repository and Load Data (Cached)
@st.cache_data
def load_calendar_data():
    repo = CSVRepository("repository/calendar.csv")
    events = repo.load_events()
    return repo, events

# Create repository instance and load events with error handling
try:
    repository, events = load_calendar_data()
except RepositoryError as e:
    st.error(f"Repository Error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Failed to load calendar data: {e}")
    st.stop()

# Initialize AvailabilityFinder using Constructor Injection (passing the repository)
daily_finder = AvailabilityFinder(repository=repository)

# Extract list of unique people from events
all_people = sorted(list({event.person_name for event in events}))

# Sidebar Controls
st.sidebar.header("Search Parameters")

selected_people = st.sidebar.multiselect(
    "Select Participants:",
    options=all_people,
    default=all_people[:2] if len(all_people) >= 2 else all_people
)

meeting_duration = st.sidebar.number_input(
    "Meeting Duration (minutes):",
    min_value=15,
    max_value=240,
    value=30,
    step=15
)

search_type = st.sidebar.radio(
    "Search Mode:",
    options=["Daily", "Weekly", "Monthly"]
)

# 2. Main Area Action
if st.button("Find Available Slots"):
    if not selected_people:
        st.warning("Please select at least one participant.")
    else:
        st.subheader(f"Results for {', '.join(selected_people)}")

        try:
            # DAILY SEARCH
            if search_type == "Daily":
                # Calling find_available_slots without 'events' argument (handled internally by the repository)
                slots = daily_finder.find_available_slots(
                    target_people=selected_people,
                    duration_minutes=meeting_duration
                )
                if slots:
                    st.success(f"Found {len(slots)} available slots:")
                    for slot in slots:
                        st.write(f"- 🕒 {slot}")
                else:
                    st.info("No available slots found for today.")

            # WEEKLY SEARCH
            elif search_type == "Weekly":
                week_finder = WeekFinder(base_finder=daily_finder)
                start_date = st.date_input("Select Week Start Date:", value=date.today())

                weekly_result = week_finder.find_for_week(
                    events=events,
                    target_people=selected_people,
                    duration_minutes=meeting_duration,
                    start_of_week=start_date
                )

                for day in weekly_result.days:
                    with st.expander(f"Date: {day.day_date}"):
                        if day.available_slots:
                            for slot in day.available_slots:
                                st.write(f"- {slot}")
                        else:
                            st.write("No slots available.")

            # MONTHLY SEARCH
            elif search_type == "Monthly":
                month_finder = MonthFinder(week_finder=WeekFinder(base_finder=daily_finder))
                selected_month = st.slider("Select Month:", 1, 12, date.today().month)
                selected_year = st.number_input("Select Year:", value=date.today().year)

                monthly_result = month_finder.find_for_month(
                    events=events,
                    target_people=selected_people,
                    duration_minutes=meeting_duration,
                    year=selected_year,
                    month=selected_month
                )

                for week in monthly_result.weeks:
                    st.markdown(f"### Week {week.week_number}")
                    cols = st.columns(len(week.days))
                    for idx, day in enumerate(week.days):
                        with cols[idx]:
                            st.caption(str(day.day_date))
                            if day.available_slots:
                                for slot in day.available_slots:
                                    st.write(f"🕒 {slot}")
                            else:
                                st.write("None")

        except PersonNotFoundError as e:
            st.error(f"Participant Error: {e}")
        except InvalidTimeSlotError as e:
            st.error(f"Time Slot Error: {e}")
        except CalendarError as e:
            st.error(f"Application Error: {e}")