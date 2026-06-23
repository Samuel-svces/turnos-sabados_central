import streamlit as st
from streamlit_calendar import calendar

st.title('Calendar Test')
events = [{'title': 'Dr. Juan', 'start': '2026-06-20', 'id': 'e1'}]
options = {'editable': True, 'initialView': 'dayGridMonth'}
state = calendar(events=events, options=options, key='cal')
st.write(state)
