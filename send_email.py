from dataclasses import dataclass
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import os
from icalendar import Calendar, Event, vText
from dotenv import load_dotenv
import streamlit as st
@dataclass
class MeetingDetails:
    title: str
    description: str
    location: str
    duration_minutes: int = 30

class CalendarInviteSender:
    def __init__(self, sender_email: str, sender_name: str):
        load_dotenv()  # Load environment variables from .env file
        
            
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.sender_formatted = f"{sender_name} <{sender_email}>"
        
        self.email_password = st.secrets['EMAIL_APP_PASSWORD']
        if not self.email_password:
            raise ValueError("EMAIL_APP_PASSWORD environment variable not set")

    def create_ical(self, start_time: datetime, meeting: MeetingDetails, attendee_email: str) -> str:
        """Create iCal content using icalendar library."""
        cal = Calendar()
        cal.add('prodid', '-//Scheduling Website//EN')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')

        event = Event()
        event.add('summary', meeting.title)
        event.add('description', meeting.description)
        event.add('dtstart', start_time)
        event.add('dtend', start_time + timedelta(minutes=meeting.duration_minutes))
        event.add('dtstamp', datetime.now())
        
        # Add organizer
        event['organizer'] = vText(f'mailto:{self.sender_email}')
        
        # Add attendee
        event.add('attendee', f'mailto:{attendee_email}', parameters={
            'cn': attendee_email,
            'role': 'REQ-PARTICIPANT',
            'rsvp': 'TRUE',
            'partstat': 'NEEDS-ACTION',
            'cutype': 'INDIVIDUAL'
        })
        
        event.add('location', meeting.location)
        event['uid'] = f"{datetime.now().strftime('%Y%m%dT%H%M%SZ')}-{self.sender_email}"
        
        cal.add_component(event)
        return cal.to_ical().decode('utf-8')

    def send_invite(self, start_time: datetime, meeting: MeetingDetails, attendee_email: str) -> None:
        """Send a calendar invite email."""

        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Reply-To'] = self.sender_formatted
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = meeting.title
        msg['From'] = self.sender_formatted
        msg['To'] = attendee_email
        
        # Create HTML email body with better formatting
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">{meeting.title}</h2>
            <p style="margin: 15px 0;">{meeting.description}</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p style="margin: 5px 0;"><b>When:</b> {start_time.strftime('%A, %B %d, %Y at %I:%M %p')}</p>
              <p style="margin: 5px 0;"><b>Duration:</b> {meeting.duration_minutes} minutes</p>
              <p style="margin: 5px 0;"><b>Location:</b> {meeting.location}</p>
            </div>
          </body>
        </html>
        """
        
        # Attach parts to email
        part_html = MIMEText(html_body, 'html')
        part_cal = MIMEText(self.create_ical(start_time, meeting, attendee_email), 
                           'calendar;method=REQUEST')
        
        msg.attach(part_html)
        msg.attach(part_cal)

        # Send email using context manager
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.email_password)
                server.send_message(msg)
        except smtplib.SMTPException as e:
            raise RuntimeError(f"Failed to send email: {e}")

def test():
    sender = CalendarInviteSender(
        sender_email="kyan.nelson.meeting.scheduler@gmail.com",
        sender_name="Kyan Nelson"
    )
    
    meeting = MeetingDetails(
        title="Coffee Chat",
        description="This is a test for the deployed version.",
        location="Zoom (link will be provided)",
        duration_minutes=30
    )
    
    sender.send_invite(
        start_time=datetime.now() + timedelta(days=1),
        meeting=meeting,
        attendee_email="Kyan.Nelson@colorado.edu"
    )

if __name__ == "__main__":
    # Example usage
    sender = CalendarInviteSender(
        sender_email="kyan.nelson.meeting.scheduler@gmail.com",
        sender_name="Kyan Nelson"
    )
    
    meeting = MeetingDetails(
        title="Coffee Chat",
        description="Let's discuss potential opportunities and my background.",
        location="Zoom (link will be provided)",
        duration_minutes=30
    )
    
    sender.send_invite(
        start_time=datetime.now() + timedelta(days=1),
        meeting=meeting,
        attendee_email="Kyan.Nelson@colorado.edu"
    )