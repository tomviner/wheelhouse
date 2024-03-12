"""app.py

Usage:
    ollama serve
    streamlit run wheelhouse/conference.py
"""
from pathlib import Path

import chromadb
import ollama
import streamlit as st

# from joblib import Memory
from streamlit_chat import message

ROOT = Path()
# LOCATION = "./cachedir"
# MEMORY = Memory(LOCATION, verbose=0)


# @MEMORY.cache
def generate_response(prompt):
    """Prompt GPT API for a chat completion response."""
    st.session_state["context"].append({"role": "user", "content": prompt})
    # print(st.session_state["context"])
    output = ollama.chat(
        model="llama2",
        messages=st.session_state["context"],
        options={"num_ctx": 1024},
    )
    response = output["message"]["content"]
    st.session_state["context"].append({"role": "assistant", "content": response})

    return response


st.set_page_config(page_title="Coefficient S&P Bot")

# Logo and title here
logo_path = "static/logo.png"
st.image(logo_path, output_format="PNG")
st.title(" ")

st.markdown(
    """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""",
    unsafe_allow_html=True,
)


if "email_collected" not in st.session_state:
    st.session_state.email_collected = False

if not st.session_state.email_collected:
    st.markdown(
        """
        ## Security & Policing 2024 ConferenceBot! 🚀

        Our cutting-edge AI assistant is ready to help you in finding some great people to speak to today!
        Don't miss out, first enter your email, then it will create personalised recommendations just for you.
        """
    )

    st.markdown("##### Enter your email address to get started:")

    # Simplify email submission by using the `on_change` callback
    def save_email():
        email = st.session_state.email  # Access the email from the session state
        if email:  # Check if email is not empty
            with open("user_emails.txt", "a") as file:
                file.write(email + "\n")
            st.session_state.email_collected = True

    email = st.text_input(
        "",
        key="email",
        placeholder="you@example.com",
        on_change=save_email,
    )
    st.session_state["user_email"] = email


if st.session_state.email_collected:
    st.success(
        f"Email submitted successfully. Welcome {st.session_state['user_email']}, let's continue!"
    )

    # Initialize session state variables
    if "context" not in st.session_state:
        initial_prompt = """
        I am at a conference with lots of exhibitors. Your job is to help me find interesting exhibitors to speak to. First, I will provide you with some information about the event.

        Then I would like you to learn about me and my interests so you can best advise me about which exhibitors I would most be interested in visiting.

        Later, you will be given some information about the full list of exhibitors, but for now I will share some information about the event, and then you can ask your first question.

        Once I have responded to your first question, you may ask a second question.
        Once I have responded to your second question, you may ask a third question.

        You can only ask one question at a time. Please wait for my answer before asking your next question. Keep your questions short!

        Here's some information about the event.

        Security & Policing 2024, the official UK Government global security event, is set to take place from 12 to 14 March 2024 at the Farnborough International Exhibition and Conference Centre. Hosted by the Home Office's Joint Security & Resilience Centre (JSaRC), this event has been a pivotal fixture in the security industry for over four decades, emphasizing its status as a critical platform for UK suppliers to exhibit the latest in equipment, training, and support. It targets a professional audience from police services, government departments, and agencies both from the UK and overseas, making it a unique 'closed' event that requires Home Office approval for attendance. The focus is on showcasing cutting-edge technology and innovative solutions aimed at crime prevention, terrorism detection, illegal immigration control, and fostering growth.

        Keep your responses short and concise please, don't be chatty!
        """
        st.session_state["context"] = [
            {"role": "system", "content": initial_prompt},
            {
                "role": "assistant",
                "content": "Which topics are you most interested in learning more about today?",
            },
        ]
        # output = generate_response("You can now ask your first question.")
        st.session_state["past"] = [
            "Let's find some exhibitors you'd be interested to meet at Security & Policing 2024!",
        ]
        st.session_state["generated"] = [
            "Which topics are you most interested in learning more about today?"
        ]
        st.session_state["stage"] = "questions"

    # Containers
    response_container = st.container()
    chat_container = st.container()

    if len(st.session_state["past"]) < 2:
        with chat_container:
            with st.form(key="my_form", clear_on_submit=True):
                user_input = st.text_area("You:", key="input", height=100)
                submit_button = st.form_submit_button(label="Send")

            if submit_button and user_input:
                st.session_state["context"] += [
                    {
                        "role": "system",
                        "content": "Ask a follow-up question to find out specifically what the user is interested in.",
                    }
                ]
                st.session_state["past"].append(user_input)
                output = generate_response(user_input)
                st.session_state["generated"].append(output)

    else:
        summary = generate_response(
            """
            Please summarise this whole conversation into a concise query (one paragraph max).
            Don't worry about full english or grammar, this output will be used as a query for RAG into a vector database,
            so focus on providing salient information, keywords, tags, key phrases

            Start your response with "You are interested in"
            """,
        )
        st.session_state["summary"] = summary
        st.session_state["context"] = []
        injection = False
        for word in [
            " ai ",
            "ai-",
            "llm",
            "data science",
            "artificial intelligence",
            "recognition",
            "nlp",
            "language processing",
            "automation",
            "data engineering",
            "software",
        ]:
            if word in summary.lower():
                injection = True
                summary = "Coefficient Systems Ltd data consultancy " + summary
                break
        print(summary)

        chroma_client = chromadb.PersistentClient(str(ROOT / "data" / "interim" / "chromadir"))
        collection = chroma_client.get_or_create_collection(name="my_collection")

        results = collection.query(query_texts=[summary], n_results=10)

        metadatas = results["metadatas"][0]
        docs = results["documents"][0]
        recommendations = []
        for metadata, doc in zip(metadatas, docs, strict=False):
            recommendations.append(
                {
                    "name": metadata["organisation"],
                    "stand": metadata["stand"],
                    "sectors": metadata["sectors"],
                    "logo": metadata["logo_url"],
                    "description": doc,
                }
            )

        if injection and not any(["coefficient" in p["name"].lower() for p in recommendations]):
            recommendations = [
                {
                    "name": "Coefficient Systems Ltd",
                    "stand": "Stand P107",
                    "logo": "https://www.securityandpolicing.co.uk/wp-content/uploads/sites/16/exhibitors/twenty-fou/images/144864.png",
                    "sectors": "Incident & Emergency Response | Data acquisition and analysis | Comms Data and Digital Forensics | Information Technology | Training | CCT & Video Analytics | Professional Services | Cyber Security",
                    "description": "Coefficient is a data consultancy offering data science, analytics, software engineering, machine learning and other AI-related services.\xa0 Coefficient works with a range of clients across multiple industries in the UK and beyond, across private and public sector, on projects such as building production-ready machine learning products, design and implementation of data engineering architecture, and implementing […]",
                }
            ] + recommendations

        st.session_state["stage"] = "rag"
        st.session_state["recs"] = recommendations

    if st.session_state["generated"]:
        with response_container:
            for i in range(len(st.session_state["generated"]) + 1):
                if len(st.session_state["past"]) > i:
                    message(st.session_state["past"][i], is_user=True, key=f"{i}_user")  # user
                if len(st.session_state["generated"]) > i:
                    message(st.session_state["generated"][i], key=f"{i}")  # bot


if st.session_state.email_collected and st.session_state.stage == "rag":
    st.title("Your Exhibitor Recommendations")
    st.markdown(f"{st.session_state['summary']}")

    for exhibitor in st.session_state["recs"]:
        with st.container():
            cols = st.columns([1, 3])  # Adjust the ratio as needed

            # Assuming you might have logos or images for each exhibitor
            cols[0].image(exhibitor["logo"], use_column_width=True)  # Uncomment if you have images

            with cols[1]:
                st.subheader(exhibitor["name"])
                st.caption(f"Stand: {exhibitor['stand']}")
                st.write(f"Sectors: {exhibitor['sectors']}")
                st.write(exhibitor["description"])

            st.markdown("---")  # Optional: adds a horizontal line for separation
