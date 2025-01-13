import streamlit as st
from datetime import datetime, timedelta
from calendar_source import NylasCalendar

st.title("Calendar Test App")

# Initialize calendar
calendar = NylasCalendar()

# Date selection
selected_date = st.date_input(
    "Select a date",
    min_value=datetime.now().date(),
    value=datetime.now().date()
)

# Convert to datetime for our calendar functions
date = datetime.combine(selected_date, datetime.min.time())

# Get available slots
slots = calendar.get_available_slots(date)

# Display available slots
st.write("### Available Slots")

if not slots:
    st.warning("No available slots for this date")
else:
    # Create a slot selector
    slot_options = [f"{slot['start_str']} - {slot['end_str']}" for slot in slots]
    selected_slot_str = st.selectbox("Choose a time", slot_options)
    
    # Find the selected slot object
    selected_slot = next(
        (slot for slot in slots 
         if f"{slot['start_str']} - {slot['end_str']}" == selected_slot_str),
        None
    )
    
    if selected_slot:
        with st.form("schedule_form"):
            st.write(f"Selected time: {selected_slot_str}")
            
            # Get meeting details
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            notes = st.text_area("Meeting Notes", 
                "Let's discuss potential opportunities.")
            
            # Submit button
            if st.form_submit_button("Schedule Meeting"):
                if name and email:
                    try:
                        # Create the event
                        calendar.create_event(
                            start_time=selected_slot['start'],
                            title=f"Meeting with {name}",
                            description=notes,
                            participants=[email]
                        )
                        st.success("✅ Meeting scheduled successfully!")
                        
                    except Exception as e:
                        st.error(f"Error scheduling meeting: {str(e)}")
                else:
                    st.warning("Please fill in all required fields.")

# Add a section to show calendar details
if st.checkbox("Show Calendar Details"):
    st.write("### Calendar Info")
    st.write("Today's busy times:")
    busy_times = calendar.get_busy_times(date)
    
    if busy_times:
        for time in busy_times:
            st.write(f"- {time['start'].strftime('%I:%M %p')} - "
                    f"{time['end'].strftime('%I:%M %p')}")
    else:
        st.write("No busy times found for today")