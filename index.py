import streamlit as st
from datetime import datetime, timedelta
from calendar_source import NylasCalendar
from page_init import page_init
from zoneinfo import ZoneInfo


def main():

  c1, c2 = page_init()
  calendar = NylasCalendar()

  # with c1:
  #   st.markdown("# Hi, I'm Kyan Nelson")
  #   st.markdown("##### *BS  Dual Emphasis in Finance and Information Management with Computer Science Integration*")
  #   st.markdown('''
  #               - Phone Number: 303-802-9736
  #               - Email: kyan.nelson@colorado.edu
  #               - LinkedIn: https://www.linkedin.com/in/kyan-nelson/                        
  #               ''')
    
  #   with open("Official_Resume.pdf", "rb") as file:
  #       btn = st.download_button(
  #           label="Click Here to Download Resume",
  #           data=file,
  #           file_name="resume.pdf",
  #           mime="application/pdf"
  #       )

  # with c2:
  #   st.image("static/headshot.png", width=400)
  # render_header(c1, c2)

##################
  with c1:
    st.title("Hi, I'm Kyan Nelson")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["### 🎓 Education", "### 📞 Contact"])
    
    with tab1:
        st.markdown("### My Degree:")
        col1, col2, col3, col4= st.columns(4)
        with col1:
            st.metric("Emphasis", "Finance", "📈")
        with col2:
            st.metric("Emphasis", "Info Mgmt", "📊")
        with col3:
            st.metric("Integration", "Comp Sci", "💻")
        with col4:
           st.metric("Minor", "Spanish", "🇪🇸")
    
    with tab2:
        # Contact info as expandable sections
        st.write("📱 Phone: 303-802-9736")
        st.write("📧 Email: kyan.nelson@colorado.edu")
        st.write("💼 LinkedIn: https://www.linkedin.com/in/kyan-nelson")

    # Resume button with animation
    with open("Official_Resume.pdf", "rb") as file:
        st.download_button(
            "📄 Download Resume",
            file,
            "resume.pdf",
            "application/pdf"
        )

  with c2:
    st.image("static/headshot.png", use_column_width=True)
#################




  st.header("Schedule a Meeting:")
  # Date selection
  mt_time = datetime.now(ZoneInfo("America/Denver"))

  selected_date = st.date_input(
      "Select a potential date",
      min_value=mt_time.date(),
      max_value=mt_time.date() + timedelta(days=90),
      value=mt_time.date() + timedelta(days=1)
  )
  # Convert to datetime for our calendar functions
  date = datetime.combine(selected_date, datetime.min.time())

  # Get available slots
  slots = calendar.get_available_slots(date)

  # Display available slots
  # st.markdown("### Time Details.")

  if not slots:
      st.error(f"Unfortunately, I have no availabilities on {selected_date.month}/{selected_date.day}.")
  else:
      # Create a slot selector
      slot_options = [f"{slot['start_str']} - {slot['end_str']}" for slot in slots]
      selected_slot = st.selectbox("Choose a time", slot_options)

      timezone = st.selectbox("Choose your time zone", calendar.timzone_dict.keys())
      
      if selected_slot:
        with st.form("schedule_form"):
          # st.write(f"Selected time: {selected_slot}")
          
          # Get meeting details
          name = st.text_input("Your Name")
          email = st.text_input("Your Email")
          notes = st.text_area("Any notes you would like to include (Optional)")
          
          # Submit button
          if st.form_submit_button("Schedule Meeting"):
              if name and email:
                  try:
                      # Create the event
                      event_details = calendar.create_event(
                          timeslot=selected_slot,
                          date=date,
                          timezone=timezone,
                          title=f"Meeting with Kyan X {name}",
                          description=notes,
                          email=email
                      )
                      st.success("✅ Meeting scheduled successfully!")

                      with st.expander("Meeting details"):
                        st.markdown(f'#### *{event_details['title']}*')
                        st.markdown(f'Start: {event_details['start']}')
                        st.markdown(f'End: {event_details['end']}')
                        st.markdown(f'Zoom Link: {event_details['location']}')

                  except Exception as e:
                      st.error(f"Error scheduling meeting: {str(e)}")
              else:
                  st.warning("Please fill in all required fields.")



if __name__ == "__main__":
    main()