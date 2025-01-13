# index.py
import streamlit as st
from datetime import datetime, timedelta
from page_init import page_init
from calendar_source import NylasCalendar

def main():
    c1, c2 = page_init()
    calendar = NylasCalendar()

    with c1:
        st.header("Schedule a Coffee Chat")
        
        # Date selection
        selected_date = st.date_input(
            "Select a date",
            min_value=datetime.now().date(),
            max_value=datetime.now().date() + timedelta(days=30)
        )

        # Get available slots for selected date
        available_slots = calendar.get_available_slots(selected_date)
        
        if not available_slots:
            st.warning("No available slots for this date. Please select another date.")
        else:
            # Create time slots selection
            time_options = [f"{slot['start']} - {slot['end']}" for slot in available_slots]
            selected_time_str = st.selectbox("Select a time", time_options)
            
            # Meeting details form
            with st.form("meeting_form"):
                email = st.text_input("Your Email")
                name = st.text_input("Your Name")
                
                submitted = st.form_submit_button("Schedule Meeting")
                
                if submitted:
                    if not email or not name:
                        st.error("Please fill in all fields")
                    else:
                        # Find selected slot
                        selected_index = time_options.index(selected_time_str)
                        selected_slot = available_slots[selected_index]
                        
                        # Schedule the meeting
                        start_time = datetime.fromtimestamp(selected_slot['timestamp'])
                        
                        try:
                            calendar.schedule_meeting(
                                start_time=start_time,
                                duration_minutes=30,
                                attendee_email=email,
                                title=f"Coffee Chat with {name}",
                                description="Looking forward to our conversation!"
                            )
                            st.success("Meeting scheduled successfully! You'll receive a calendar invite shortly.")
                        except Exception as e:
                            st.error(f"Failed to schedule meeting: {str(e)}")

    with c2:
        st.header("About Me")
        # Add your personal information and any other relevant details here

if __name__ == "__main__":
    main()