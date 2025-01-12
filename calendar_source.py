from msal import PublicClientApplication, SerializableTokenCache
import requests
from datetime import datetime, timedelta
import streamlit as st
import os
import json

class OutlookCalendar:
    def __init__(self):
        self.client_id = st.secrets['OUTLOOK_CLIENT_ID']
        self.authority = "https://login.microsoftonline.com/consumers"
        self.scope = ["Calendars.Read"]
        self.token_cache_file = ".token_cache.json"
        
        # Initialize token cache
        self.cache = SerializableTokenCache()
        
        # Load existing cache if it exists
        if os.path.exists(self.token_cache_file):
            try:
                with open(self.token_cache_file, 'r') as f:
                    self.cache.deserialize(f.read())
            except Exception as e:
                print(f"Error loading token cache: {e}")
        
        self.app = PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.cache
        )

    def _save_cache(self):
        """Save the token cache if it has changed"""
        if self.cache.has_state_changed:
            try:
                with open(self.token_cache_file, 'w') as f:
                    f.write(self.cache.serialize())
            except Exception as e:
                print(f"Error saving token cache: {e}")

    def get_token(self):
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scope, account=accounts[0])
            if result:
                self._save_cache()
                return result['access_token']
        
        # If no valid cached token, get new one
        result = self.app.acquire_token_interactive(scopes=self.scope)
        if result:
            self._save_cache()
            return result['access_token']
        return None

    def get_calendar_events(self, start_date=None, end_date=None):
        """Get calendar events between start_date and end_date"""
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=7)

        token = self.get_token()
        if not token:
            raise Exception("Failed to acquire token")

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        start_str = start_date.isoformat() + 'Z'
        end_str = end_date.isoformat() + 'Z'

        url = 'https://graph.microsoft.com/v1.0/me/calendarView'
        params = {
            'startDateTime': start_str,
            'endDateTime': end_str,
            '$select': 'subject,start,end,showAs'
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to get calendar events: {response.text}")
        return response.json()

    def get_available_slots(self, date, duration_minutes=30):
        """Get available time slots for a specific date"""
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        events = self.get_calendar_events(start_of_day, end_of_day)
        busy_times = [(datetime.fromisoformat(e['start']['dateTime'].replace('Z', '')),
                      datetime.fromisoformat(e['end']['dateTime'].replace('Z', '')))
                     for e in events.get('value', [])]
        
        # Generate available slots (9 AM to 5 PM)
        available_slots = []
        current_time = start_of_day.replace(hour=9)  # Start at 9 AM
        end_time = start_of_day.replace(hour=17)     # End at 5 PM
        
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