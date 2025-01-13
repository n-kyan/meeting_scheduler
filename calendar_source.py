import requests
from datetime import datetime, timedelta
import streamlit as st

class OutlookCalendar:
    def __init__(self):
        self.auth_server_url = "https://microsoft-auth-server.onrender.com"
    
    def get_available_slots(self, date, duration_minutes=30):
        """Get available time slots for a specific date"""
        try:
            response = requests.get(
                f"{self.auth_server_url}/calendar/available-slots",
                params={"date": date.strftime('%Y-%m-%d')}
            )
            
            if response.status_code != 200:
                st.error(f"Failed to get calendar events. Please try again later.")
                return []
            
            events = response.json()
            return self._process_events(events, date, duration_minutes)
            
        except Exception as e:
            st.error(f"Error fetching calendar data: {str(e)}")
            return []
    
    def _process_events(self, events, date, duration_minutes):
        """Process calendar events into available slots"""
        try:
            busy_times = [(datetime.fromisoformat(e['start']['dateTime'].replace('Z', '')),
                          datetime.fromisoformat(e['end']['dateTime'].replace('Z', '')))
                         for e in events.get('value', [])]
            
            # Generate available slots (9 AM to 5 PM)
            available_slots = []
            current_time = datetime.combine(date, datetime.min.time()).replace(hour=9)
            end_time = datetime.combine(date, datetime.min.time()).replace(hour=17)
            
            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                is_available = True
                
                for busy_start, busy_end in busy_times:
                    if not (slot_end <= busy_start or current_time >= busy_end):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'start': current_time.strftime('%I:%M %p'),
                        'end': slot_end.strftime('%I:%M %p')
                    })
                
                current_time += timedelta(minutes=duration_minutes)
            
            return available_slots
        except Exception as e:
            st.error(f"Error processing events: {str(e)}")
            return []