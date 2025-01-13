import streamlit as st
from datetime import datetime, timedelta
from page_init import page_init
from send_email import test
from calendar_source import OutlookCalendar

def main():
    c1, c2 = page_init()
    calendar = OutlookCalendar()

    st.header("Schedule a Coffee Chat:")

    # Date selection with min/max dates
    min_date = datetime.now().date()
    max_date = min_date + timedelta(days=30)  # Allow booking up to 30 days in advance
    selected_date = st.date_input(
        "Select Date", 
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )

    # Show available slots
    if selected_date:
        available_slots = calendar.get_available_slots(selected_date)
        if available_slots:
            st.write("Available time slots:")
            
            # Create columns for better layout
            cols = st.columns(3)
            for idx, slot in enumerate(available_slots):
                col_idx = idx % 3
                with cols[col_idx]:
                    if st.button(f"{slot['start']} - {slot['end']}", key=f"slot_{idx}"):
                        # Handle slot selection
                        st.session_state['selected_slot'] = slot
                        st.success(f"Selected time slot: {slot['start']} - {slot['end']}")
        else:
            st.info("No available slots found for this date.")

    # If a slot is selected, show the booking form
    if 'selected_slot' in st.session_state:
        st.write("---")
        st.subheader("Complete your booking")
        with st.form("booking_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            company = st.text_input("Company (Optional)")
            notes = st.text_area("Additional Notes (Optional)")
            
            if st.form_submit_button("Schedule Meeting"):
                if name and email:
                    # Here you would call your email sending function
                    try:
                        test()  # Replace with your actual booking logic
                        st.success("Meeting scheduled successfully!")
                        del st.session_state['selected_slot']
                    except Exception as e:
                        st.error(f"Failed to schedule meeting: {str(e)}")
                else:
                    st.error("Please fill in your name and email.")

if __name__ == "__main__":
    main()