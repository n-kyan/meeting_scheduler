from datetime import datetime, timedelta
import streamlit as st
from nylas import Client
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional

class NylasCalendar:
    def __init__(self):
        """Initialize Nylas client with credentials from Streamlit secrets."""
        self.api_key = st.secrets["NYLAS_API_KEY"]
        self.grant_id = st.secrets["NYLAS_GRANT_ID"]
        self.nylas = Client(self.api_key)
        self.timzone_dict = {
            # North America
            'MST': 'America/Denver',       # Mountain Time
            'MDT': 'America/Denver',
            'EST': 'America/New_York',     # Eastern Time
            'EDT': 'America/New_York',
            'CST': 'America/Chicago',      # Central Time
            'CDT': 'America/Chicago',
            'PST': 'America/Los_Angeles',  # Pacific Time
            'PDT': 'America/Los_Angeles',
            'AKST': 'America/Anchorage',   # Alaska Time
            'AKDT': 'America/Anchorage',
            'HST': 'Pacific/Honolulu',     # Hawaii Time
            
            # Europe
            'GMT': 'GMT',                  # Greenwich Mean Time
            'UTC': 'UTC',                  # Coordinated Universal Time
            'WET': 'Europe/London',        # Western European Time
            'WEST': 'Europe/London',
            'CET': 'Europe/Paris',         # Central European Time
            'CEST': 'Europe/Paris',
            'EET': 'Europe/Athens',        # Eastern European Time
            'EEST': 'Europe/Athens',
            
            # Asia/Pacific
            'IST': 'Asia/Kolkata',         # Indian Standard Time
            'JST': 'Asia/Tokyo',           # Japan Standard Time
            'CST_CHINA': 'Asia/Shanghai',  # China Standard Time
            'HKT': 'Asia/Hong_Kong',       # Hong Kong Time
            'SGT': 'Asia/Singapore',       # Singapore Time
            'AEST': 'Australia/Sydney',    # Australian Eastern Time
            'AEDT': 'Australia/Sydney',
            'AWST': 'Australia/Perth',     # Australian Western Time
            
            # Other Regions
            'NZST': 'Pacific/Auckland',    # New Zealand Time
            'NZDT': 'Pacific/Auckland',
            'BST': 'Europe/London',        # British Summer Time
            'WAT': 'Africa/Lagos',         # West Africa Time
            'CAT': 'Africa/Maputo',        # Central Africa Time
            'EAT': 'Africa/Nairobi',       # East Africa Time
        }

    def get_busy_times(self, date: datetime, calendar_id: Optional[str] = None) -> List[Dict]:
        """
        Get list of busy time slots for a specific date
        
        Args:
            date (datetime): The date to check
            calendar_id (str, optional): Specific calendar to check. If None, checks all calendars
            
        Returns:
            List of busy time slots with start and end times
        """
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        busy_times = []
        calendars = self.nylas.calendars.list(self.grant_id)

        # If no specific calendar_id is provided, check all calendars
        calendar_ids = [calendar_id] if calendar_id else [cal.id for cal in calendars[0]]
        
        for cal_id in calendar_ids:
            events = self.nylas.events.list(
                self.grant_id,
                query_params={
                    "calendar_id": cal_id,
                }
            )

            for event in events[0]:
                # Skip non-busy events
                if not event.busy:
                    continue
                    
                # Handle timespan events
                if hasattr(event.when, 'start_time'):
                    event_start = datetime.fromtimestamp(event.when.start_time)
                    event_end = datetime.fromtimestamp(event.when.end_time)
                # Handle datespan events
                elif hasattr(event.when, 'start_date'):
                    event_start = datetime.strptime(event.when.start_date, '%Y-%m-%d')
                    event_end = datetime.strptime(event.when.end_date, '%Y-%m-%d')
                else:
                    continue

                # Only include if event overlaps with the requested date
                if (event_start <= end_of_day and event_end >= start_of_day):
                    busy_times.append({
                        'start': max(event_start, start_of_day),
                        'end': min(event_end, end_of_day)
                    })
        
        return sorted(busy_times, key=lambda x: x['start'])

    def get_available_slots(self, date: datetime, duration_minutes: int = 30,
                          start_hour: int = 9, end_hour: int = 17) -> List[Dict]:
        """
        Get available time slots for a specific date
        
        Args:
            date (datetime): The date to check
            duration_minutes (int): Length of each slot in minutes
            start_hour (int): Hour to start checking from (24-hour format)
            end_hour (int): Hour to end checking at (24-hour format)
            
        Returns:
            List of available time slots
        """
        # Don't show availability for past dates
        if date.date() < datetime.now().date():
            return []
            
        # Don't show availability for weekends
        if date.weekday() >= 5:
            return []

        busy_times = self.get_busy_times(date)
        
        # Set up the time slots to check
        start_of_day = datetime.combine(date, datetime.min.time().replace(hour=start_hour))
        end_of_day = datetime.combine(date, datetime.min.time().replace(hour=end_hour))
        
        available_slots = []
        current_time = start_of_day
        
        while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            is_available = True
            
            # Check if slot conflicts with any busy times
            for busy in busy_times:
                if not (slot_end <= busy['start'] or current_time >= busy['end']):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append({
                    'start': current_time,
                    'end': slot_end,
                    'start_str': current_time.strftime('%I:%M %p'),
                    'end_str': slot_end.strftime('%I:%M %p'),
                })
            
            current_time += timedelta(minutes=duration_minutes)
        
        return available_slots
    
    def timeslot_to_unix(self, timeslot: str, date: datetime, timezone: str):
      start_str, end_str = timeslot.split(" - ")
      
      # Create timezone aware datetimes
      start_time = datetime.strptime(start_str, "%I:%M %p").replace(
          year=date.year,
          month=date.month,
          day=date.day,
      ).astimezone(ZoneInfo(timezone))  # Convert to specified timezone
      
      end_time = datetime.strptime(end_str, "%I:%M %p").replace(
          year=date.year,
          month=date.month,
          day=date.day,
      ).astimezone(ZoneInfo(timezone))  # Convert to specified timezone
      
      # Convert to UTC timestamp
      return int(start_time.timestamp()), int(end_time.timestamp())

    def create_event(self, timeslot: str, date:datetime, timezone:str, duration_minutes: int = 30, 
                    title: str = "Meeting", description: str = "", 
                    email: str = None) -> Dict:
        """
        Create a new calendar event
        
        Args:
            timeslot (str): selected timeslot
            timezone (str): timezone abreviation
            duration_minutes (int): Duration of the event in minutes
            title (str): Event title
            description (str): Event description
            participants (List[str]): List of participant email addresses
            
        Returns:
            Dict with event details
        """
        # end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Get primary calendar
        calendars = self.nylas.calendars.list(self.grant_id)
        primary_calendar = next((cal for cal in calendars[0] 
                               if not cal.read_only), None)
        
        if not primary_calendar:
            raise ValueError("No writable calendar found")
            
        # Prepare request body and query params
        print(f'Timeslot: {timeslot}')
        print(type(timeslot))
        timezone = self.timzone_dict[timezone]
        start_time, end_time = self.timeslot_to_unix(timeslot, date, timezone)

        st.write(start_time)
        st.write(end_time)
        st.write(timezone)

        request_body = {
            "title": title,
            "description": description,
            "location" : "https://cuboulder.zoom.us/u/awb8m7zVz",
            "when": {
                "start_time": start_time,
                "end_time": end_time,
                "start_timezone": timezone,
                "end_timezone": timezone
            },
            "participants" : [{
                "email" : email
            }],
            "busy": True
        }
        
        query_params = {
            "calendar_id": primary_calendar.id
        }
        
        created_event = self.nylas.events.create(
            self.grant_id,
            request_body=request_body,
            query_params=query_params,
        )
        
        # Print response for debugging
        # print("Event creation response:", created_event)
        
        return {
            'title': request_body['title'],
            'start': datetime.fromtimestamp(request_body['when']['start_time']).strftime("%I:%M %p"),
            'end': datetime.fromtimestamp(request_body['when']['end_time']).strftime("%I:%M %p"),
            'location' : request_body['location']
        }

# Example usage
if __name__ == "__main__":
    calendar = NylasCalendar()
    
    # Get today's date
    today = datetime.now()
    
    # Get available slots for today
    slots = calendar.get_available_slots(today)
    
    # Print available slots
    print(f"\nAvailable slots for {today.strftime('%Y-%m-%d')}:")
    for slot in slots:
        print(f"{slot['start_str']} - {slot['end_str']}")