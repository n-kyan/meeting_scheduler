import streamlit as st
from nylas import Client
from datetime import datetime

API_KEY = st.secrets['NYLAS_API_KEY']
GRANT_ID = st.secrets['NYLAS_GRANT_ID']

nylas = Client(
    API_KEY
)

calendars = nylas.calendars.list(GRANT_ID)
for calendar in calendars[0]:
    print("\n" + "="*50)
    print(calendar.name)
    print("Calendar: {}".format(calendar.name))
    print("Id: {}".format(calendar.id))
    print("Description: {}".format(calendar.description))
    print("Read Only: {}".format(calendar.read_only))
    print("-"*50)

    events = nylas.events.list(
        GRANT_ID,
        query_params={
            "calendar_id": calendar.id
        }
    )

    if events[0]:  # If there are events
        for event in events[0]:
            print("\nEvent: {}".format(event.title))
            
            # Handle different types of 'when' objects
            if hasattr(event.when, 'start_time'):
                start = datetime.fromtimestamp(event.when.start_time)
                end = datetime.fromtimestamp(event.when.end_time)
                print("Time: {} to {}".format(
                    start.strftime("%Y-%m-%d %I:%M %p"),
                    end.strftime("%Y-%m-%d %I:%M %p")
                ))
                print("Timezone: {}".format(event.when.start_timezone))
            elif hasattr(event.when, 'start_date'):
                print("Date: {} to {}".format(
                    event.when.start_date,
                    event.when.end_date
                ))

            print("Location: {}".format(event.location or "No location"))
            print("Busy: {}".format(event.busy))
            if event.organizer:
                print("Organizer: {} ({})".format(
                    event.organizer.get('name', 'N/A'),
                    event.organizer.get('email', 'N/A')
                ))
            print("-"*30)
    else:
        print("No events in this calendar\n")