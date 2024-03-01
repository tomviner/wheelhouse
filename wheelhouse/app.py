"""app.py

Usage:
    streamlit run wheelhouse/app.py
"""
import streamlit as st
from joblib import Memory
from openai import OpenAI
from streamlit_chat import message

LOCATION = "./cachedir"
MEMORY = Memory(LOCATION, verbose=0)
CLIENT = OpenAI()


@MEMORY.cache
def generate_response(prompt, model="gpt-4-turbo-preview"):
    """Prompt GPT API for a chat completion response."""
    st.session_state["context"].append({"role": "user", "content": prompt})

    completion = CLIENT.chat.completions.create(model=model, messages=st.session_state["context"])
    response = completion.choices[0].message.content
    st.session_state["context"].append({"role": "assistant", "content": response})

    return response


# Initialize session state variables
if "context" not in st.session_state:
    initial_prompt = """
    I am at a conference with lots of exhibitors. Your job is to help me find interesting exhibitors to speak to. First, I will provide you with some information about the event.

    Then I would like you to learn about me and my interests so you can best advise me about which exhibitors I would most be interested in visiting.

    Later, you will be given some information about the full list of exhibitors, but for now I will share some information about the event, and then you can ask your first question.

    Once I have responded to your first question, you may ask a second question.
    Once I have responded to your second question, you may ask a third question.

    You can only ask one question at a time. Please wait for my answer before asking your next question.

    Here's some information about the event.

    Security & Policing 2024, the official UK Government global security event, is set to take place from 12 to 14 March 2024 at the Farnborough International Exhibition and Conference Centre. Hosted by the Home Office's Joint Security & Resilience Centre (JSaRC), this event has been a pivotal fixture in the security industry for over four decades, emphasizing its status as a critical platform for UK suppliers to exhibit the latest in equipment, training, and support. It targets a professional audience from police services, government departments, and agencies both from the UK and overseas, making it a unique 'closed' event that requires Home Office approval for attendance. The focus is on showcasing cutting-edge technology and innovative solutions aimed at crime prevention, terrorism detection, illegal immigration control, and fostering growth.

    The event serves as a vital forum for fostering collaborations between the government, industry, and academia, aimed at developing products and services to enhance national security and reduce crime. It offers an unparalleled opportunity for stakeholders to share their needs and understand available capabilities, thereby strengthening the UK's security alliances globally. Senior Government Officials, including those from various UK Government security departments, support and attend the event, leading an extensive program of conferences and briefings. This initiative underscores the Home Office's commitment to leveraging partnerships to address security challenges effectively.

    Security & Policing 2024 not only facilitates a deep dive into the latest security solutions and discussions with leading figures in the sector but also offers additional features like Security and Policing+, a secure platform for attendees to access on-demand content, network, and set up meetings. The platform aims to enhance the visitor experience by allowing them to connect with peers, arrange in-person or virtual meetings, and explore over 300 exhibitor profiles showcasing innovative security solutions. This approach underscores the event's role in bridging operational needs with relevant solutions within a secure environment, catering exclusively to professionals in policing, law enforcement, and security tasked with national resilience and protection duties.
    """
    st.session_state["context"] = [{"role": "system", "content": initial_prompt}]
    output = generate_response("You can now ask your first question.")
    st.session_state["generated"] = [output]

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []


# Containers
response_container = st.container()
chat_container = st.container()


with chat_container:
    with st.form(key="my_form", clear_on_submit=True):
        user_input = st.text_area("You:", key="input", height=100)
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state["past"].append(user_input)
        st.session_state["generated"].append(output)


if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state["generated"])):
            message(st.session_state["generated"][i], key=f"{i}")  # bot
            if len(st.session_state["past"]) > i:
                message(st.session_state["past"][i - 1], is_user=True, key=f"{i}_user")  # user