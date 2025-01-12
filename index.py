import streamlit as st
from page_init import page_init
from send_email import test
from calendar_source import OutlookCalendar
from datetime import datetime

c1, c2 = page_init()
calendar = OutlookCalendar()

st.header("Schedule a Coffee Chat:")
# insert_meeting_form()
if st.button("Send"):
    st.write(calendar.get_available_slots(datetime.now().date()))
    print(calendar.get_available_slots(datetime.now().date()))
    test()

# def main():
#     # calendar = OutlookCalendar()

#     # c1, c2 = page_init()
#     st.header("Schedule a Coffee Chat:")
#     # # insert_meeting_form()
#     # if st.button("Send"):
#     #     st.write(calendar.get_available_slots(datetime.now().date()))
#     #     print(calendar.get_available_slots(datetime.now().date()))
#     #     test()

# if __name__ == "__main__":
#     main()