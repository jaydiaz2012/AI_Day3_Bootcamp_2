import streamlit as st
from openai import OpenAI
import warnings

warnings.filterwarnings("ignore")

# --- Page Configuration ---
st.set_page_config(
    page_title="The Shakespeare Bot: Ask William Anything!",
    page_icon="🎭",
    layout="wide"
)

# --- Sidebar ---
with st.sidebar:
    st.image('images/logo1.png')
    st.image('images/logo0.png')

    api_key = st.text_input("Enter your OpenAI API token:", type="password")

    if api_key and api_key.startswith("sk-") and len(api_key) > 40:
        st.success("API key looks good!", icon="👉")
    elif api_key:
        st.warning("Invalid API key format.", icon="⚠️")
    else:
        st.info("Enter your API key to begin.", icon="ℹ️")

    st.markdown("---")
    options = st.radio("Dashboard", ["Home", "About Me", "Ask William"])

# --- System Prompt ---
SYSTEM_PROMPT = """
You are William Shakespeare, the exceptionally brilliant and literary genius of the English drama.
Answer questions about your plays, sonnets, and characters using wit, sharp humour, confidence,
and deep literary insight. Focus strictly on Shakespearean literature.
"""

# --- Conversation Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Home Page ---
if options == "Home":
    st.title("The Shakespeare Bot")
    st.markdown("<p style='color:red; font-weight:bold;'>Enter your API token to use the bot.</p>", unsafe_allow_html=True)
    st.write("Ask William Shakespeare anything about his works!")
    st.write("Explore themes, characters, sonnets, and more.")

# --- About Page ---
elif options == "About Me":
    st.title("About William Shakespeare")
    st.write("""
William Shakespeare (1564–1616) was an English playwright, poet, and actor, regarded as the greatest writer 
in the English language. His works span comedies, tragedies, histories, and 154 sonnets.
""")

# --- Chat Page ---
elif options == "Ask William":
    st.title("Ask William Shakespeare!")
    user_question = st.text_input("What’s your burning question?")

    # Display conversation history
    if st.session_state.messages:
        st.markdown("### Conversation")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            elif msg["role"] == "assistant":
                st.markdown(f"**William Shakespeare:** {msg['content']}")

    col1, col2 = st.columns([1, 1])
    submit = col1.button("Submit")
    clear = col2.button("Clear Conversation")

    if clear:
        st.session_state.messages = []
        st.experimental_rerun()

    if submit:
        if not api_key or not api_key.startswith("sk-"):
            st.warning("Please enter a valid API key in the sidebar.")
        elif not user_question.strip():
            st.warning("Ask a question first.")
        else:
            client = OpenAI(api_key=api_key)

            # Inject system message once
            if not any(msg["role"] == "system" for msg in st.session_state.messages):
                st.session_state.messages.insert(
                    0, {"role": "system", "content": SYSTEM_PROMPT}
                )

            # Add user message
            st.session_state.messages.append(
                {"role": "user", "content": user_question}
            )

            try:
                with st.spinner("The Bard is writing..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages,
                        temperature=0.7,
                        max_tokens=800
                    )

                assistant_reply = response.choices[0].message["content"]
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_reply}
                )

                st.success("Here’s what The Bard says:")
                st.write(assistant_reply)

            except Exception as e:
                st.error(f"OpenAI request failed: {e}")

st.markdown("---")
st.caption("Shakespeare Bot — powered by modern sorcery.")
