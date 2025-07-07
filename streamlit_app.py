import datetime
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from streamlit_extras.stylable_container import stylable_container

st.logo("static/logo.png", size="large")

# create connections for google sheets
conn_questions = st.connection("gsheets_questions", type=GSheetsConnection)
conn_responses = st.connection("gsheets_responses", type=GSheetsConnection)

# read questions/responses data from google sheets
df_questions = conn_questions.read()
df_responses = conn_responses.read()

# disable the submit button after it is clicked
def disable_submit():
    st.session_state.disabled = True

# initialize disabled for form_submit_button to False
if "disabled" not in st.session_state:
    st.session_state.disabled = False

# fetch today's question
current_date = datetime.date.today().strftime("%Y-%m-%d")
current_question = df_questions[df_questions['Date'] == current_date]
if current_question.empty:
    st.warning("No question available for today.")

# create form for user input
with st.form("question_form"):
    st.subheader("Today's Question")
    st.write(f"Today: {current_date}")
    st.write(current_question['Question'].values[0] if not current_question.empty else "No question for today.")
    user_guess = st.number_input(
        "Your Guess", 
        value=None, 
        placeholder="Type a number...",
        step=1,
        disabled=st.session_state.disabled
    )

    submitted = st.form_submit_button(
        label="Gimme Your Digits",
        on_click=disable_submit, 
        disabled=st.session_state.disabled
    )

    if submitted:
        if user_guess is not None:
            st.write(f"Your guess is: {user_guess}")
            if user_guess == current_question['Answer'].values[0]:
                st.success("Correct!")
            else:
                st.error("Incorrect!")
                st.write(f"Correct answer was: {int(current_question['Answer'].values[0])}")
            st.write(f"Fact: {current_question['Fact'].values[0]}")    
            user_response = {
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "user_id": st.session_state.get('user_id', 'anonymous'),
                "question_id": current_question['Question ID'].values[0] if not current_question.empty else None,
                "user_response": user_guess,
                "correct_answer": int(current_question['Answer'].values[0]) if not current_question.empty else None,
                "is_correct": user_guess == int(current_question['Answer'].values[0]) if not current_question.empty else None
            }

            st.write(len(df_responses), "responses before update")

            # append the response data to the responses dataframe
            if df_responses.empty:
                df_responses_combined = pd.DataFrame([user_response])
            else:
                df_responses_combined = pd.concat([df_responses, pd.DataFrame([user_response])], ignore_index=True)
            
            # update the responses in google sheets      
            df_responses_updated = conn_responses.update(
                data=pd.DataFrame(df_responses_combined)
            )

            # display statistics of user guesses
            st.subheader("Statistics")
            df_responses = df_responses_updated
            if not df_responses.empty:
                st.write("Total Responses:", len(df_responses))
                correct_guesses = df_responses[df_responses['user_response'] == df_responses['correct_answer']]
                st.write("Correct Guesses:", len(correct_guesses))
                st.write("Incorrect Guesses:", len(df_responses) - len(correct_guesses))
                st.write("Accuracy:", f"{(len(correct_guesses) / len(df_responses) * 100):.2f}%" if len(df_responses) > 0 else "N/A")
            else:
                st.write("No responses recorded yet.")
            st.cache_data.clear()


c_statistics = stylable_container(
    key="today_question",
    css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px);
            background-color: #51342c;
        }
        h2 {
            color: #333;
        }
        .stNumberInput input {
            background-color: #f0f0f0;
            width: 100%;
            color: #34292a;
        }
        .st-c4 {
            caret-color: #34292a;
        }
    """
)


css="""
<style>
    [data-testid="stForm"] {
        background: #51342c;
    }
    [data-baseweb="input"] {
        background-color: #f0f0f0;
        color: #34292a;
        border: 1px solid #efebc4;
    }
    .stNumberInput input::placeholder {
        color: #51342c;
    }
    
</style>
"""

st.markdown(css, unsafe_allow_html=True)

