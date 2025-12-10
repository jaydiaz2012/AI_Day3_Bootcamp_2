# app.py
import os
import openai
import streamlit as st
import warnings

warnings.filterwarnings("ignore")

# --- Page config ---
st.set_page_config(page_title="The Shakespeare Bot: Ask William Anything!", page_icon="🎭", layout="wide")

# --- Sidebar / API key input ---
with st.sidebar:
    st.image('images/logo1.png')
    st.image('images/logo0.png')

    api_key = st.text_input("Enter your OpenAI API token:", type="password")
    if api_key and (api_key.startswith("sk-") and len(api_key) > 40):
        st.success("API key looks good. Proceed to Ask William.", icon="👉")
    elif api_key:
        st.warning("The API token does not appear valid. It should start with 'sk-'.", icon="⚠️")
    else:
        st.info("Enter your OpenAI API key to use the chatbot.", icon="ℹ️")

    # small spacer
    st.markdown("---")
    options = st.radio("Dashboard", ("Home", "About Me", "Ask William"))

# --- Initialize session state for messages ---
if 'messages' not in st.session_state:
    # seed with system prompt so model always sees it
    st.session_state.messages = []

# --- System prompt (keeps the Bard persona) ---
SYSTEM_PROMPT = """You are William Shakespeare, the exceptionally brilliant and literary genius of the English drama and the English language.
You possess an extensive knowledge of your plays and sonnets. Your mission: to answer questions in a way that’s not only highly informative but infused with your distinct blend of overconfidence, dry English humour, and nerdy references.
Deliver accurate literary answers, from basics to advanced inquiries, with precision and a touch of flair. Stay focused on questions about Shakespeare's works. Keep explanations thorough yet focused.
"""

# --- Pages ---
if options == "Home":
    st.title('The Shakespeare Bot')
    st.markdown("<p style='color:red; font-weight:bold;'>Note: You need to enter your OpenAI API token to use this tool.</p>", unsafe_allow_html=True)
    st.write("Welcome to the Shakespeare Bot, where you can ask William Shakespeare anything about his plays and sonnets!")
    st.write("## How It Works")
    st.write("Type a question and the model will respond in the persona of William Shakespeare.")

elif options == "About Me":
    st.title('About William Shakespeare (THE BARD)')
    st.write("William Shakespeare (1564–1616) was an English playwright, poet, and actor, often regarded as one of the greatest writers in the English language.")
    st.write("He wrote plays, sonnets, and narrative poems exploring themes such as love, power, ambition and betrayal.")
    st.markdown("Learn more: https://www.shakespeare.org.uk/")
    st.write("\n")

elif options == "Ask William":
    st.title('Ask William Shakespeare!')
    user_question = st.text_input("What's your burning question?", key="user_input")

    # display conversation history
    if st.session_state.messages:
        st.markdown("### Conversation")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"**William Shakespeare:** {msg['content']}")

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        submit = st.button("Submit")
    with col2:
        clear = st.button("Clear conversation")
    with col3:
        st.write("")  # placeholder

    # Clear conversation
    if clear:
        st.session_state.messages = []
        st.experimental_rerun()

    # Validate API key presence before calling OpenAI
    if submit:
        if not api_key or not api_key.startswith("sk-"):
            st.warning("Enter a valid OpenAI API key in the sidebar before submitting.")
        elif not user_question or not user_question.strip():
            st.warning("Please enter a question before submitting.")
        else:
            # prepare messages: include system prompt at the start (if not already)
            if not any(m['role'] == 'system' for m in st.session_state.messages):
                st.session_state.messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

            # append user message
            st.session_state.messages.append({"role": "user", "content": user_question.strip()})

            # set key for openai
            openai.api_key = api_key

            # call the API (synchronous)
            try:
                with st.spinner("William is composing his reply..."):
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages,
                        temperature=0.7,
                        max_tokens=800
                    )

                assistant_message = response["choices"][0]["message"]["content"].strip()

                # append assistant reply to history and display
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})

                st.success("Here's what The Bard says:")
                st.write(assistant_message)

            except Exception as e:
                st.error(f"OpenAI request failed: {e}")

    # if no submit yet, show hint
    if not submit:
        st.info("Type a question and press Submit. Press 'Clear conversation' to start over.")

# Footer / small note
st.markdown("---")
st.caption("Built for demonstration. Keep questions focused on Shakespeare's works.")
