import datetime
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.logo("static/logo.png", size="large")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

c_today = st.container()

df = conn.read()

current_date = datetime.date.today().strftime("%Y-%m-%d")
current_question = df[df['Date'] == current_date]
if current_question.empty:
    st.warning("No question available for today.")

c_today.write(f"Today: {current_date}")
c_today.write(current_question['Question'].values[0] if not current_question.empty else "No question for today.")

user_guess = c_today.number_input(
    "User Guess", 
    value=None, 
    placeholder="Type a number...",
    step=1,
    label_visibility="hidden"
)

if user_guess is not None:
    c_today.write(f"Your guess is: {user_guess}")
    if user_guess == current_question['Answer'].values[0]:
        c_today.success("Correct!")
    else:
        c_today.error("Incorrect, try again!")
