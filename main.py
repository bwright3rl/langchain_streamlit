import os
from dotenv import load_dotenv
import streamlit as st
import re
from llms.llm_switcher import get_llm
from chains.chain_switcher import run_chain
from langchain.memory import ConversationBufferMemory, StreamlitChatMessageHistory
import mimetypes
import pandas as pd


load_dotenv()
llm = get_llm()
history = StreamlitChatMessageHistory(key="chat_messages")
memory = ConversationBufferMemory(
    memory_key="chat_history", chat_memory=history, return_messages=True
)

st.markdown("<style>p { white-space: pre-wrap; }</style>", unsafe_allow_html=True)

header = st.container()
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

header_space = st.container()
header_space.write("""<div class='fixed-header-space'/>""", unsafe_allow_html=True)

st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: fixed;
        background-color: white;
        z-index: 999;
        top: 2rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header-space) {
        position: sticky;
        z-index: 998;
    }
    .gradient-footer {
        background: linear-gradient(to bottom, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0));
        border-bottom: 1px solid #f1f1f1;
        padding-bottom: 1rem;
    }
</style>
    """,
    unsafe_allow_html=True,
)


# chain = header.selectbox(
#     'Select a chain',
#     ('Ask Kendra',
#      'Text-to-SQL (Snowflake)',
#      'Text-to-SQL'
#      ),
#     label_visibility="hidden")

chain = "Text-to-SQL (Snowflake)"

header.write("""<div class="gradient-footer"></div>""", unsafe_allow_html=True)


# Set message(chat history) in the Streamlit session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to format intermediate steps
def format_intermediate_steps(intermediate_steps):
    return "\n```\n" + intermediate_steps + "\n```\n"


# Function to format sources
def format_sources(source):
    page_number = ""
    if "_excerpt_page_number" in source.metadata["document_attributes"]:
        page_number = " - Page " + str(
            source.metadata["document_attributes"]["_excerpt_page_number"]
        )

    source_string = (
        "**"
        + str(source.metadata["title"])
        + "**"
        + page_number
        + "\n"
        + str(source.metadata["source"])
        + "\n"
    )
    return source_string


# Display chat history from session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):

        # Show intermediate steps
        if message.get("intermediate_steps") is not None:
            with st.expander("Show work"):
                st.write(format_intermediate_steps(message["intermediate_steps"]))

        # Show messages in markdown
        st.markdown(message["content"])

        # Show sources
        if message.get("sources") is not None:
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.markdown(format_sources(source))

# Prompt text input
if prompt := st.chat_input("Ask a question"):

    st.session_state.messages.append({"role": "user", "content": prompt, "work": None})
    history.add_user_message(prompt)

    # Add user input to displayed chat history
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):

        # Spinner while we wait for LLM chain response
        with st.spinner("I'm working on it..."):

            # Send prompt to LLM chain
            full_response, sources, intermediate_steps = run_chain(
                llm, chain, memory, prompt
            )

            # Show intermediate steps
            if intermediate_steps is not None:
                with st.expander("Show work"):
                    st.write(format_intermediate_steps(intermediate_steps))

            # Show chain response in markdown
            st.markdown(full_response)

            # Show sources
            if sources is not None:
                with st.expander("Sources"):
                    for source in sources:
                        st.markdown(format_sources(source))

    # Add user and assistant messages to session
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
            "sources": sources,
            "intermediate_steps": intermediate_steps,
        }
    )
    history.add_ai_message(full_response)
