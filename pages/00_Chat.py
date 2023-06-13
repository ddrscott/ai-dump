import logging
from glob import glob
import os

import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import SystemMessage, HumanMessage, AIMessage

import yaml
import json

from dataturd.dump import data

HISTORY_CONTEXT_LENGTH = 2048

ROLE_TO_CLASS = {
    'system': SystemMessage,
    'human': HumanMessage,
    'ai': AIMessage
}

st.set_page_config(
    layout="wide",
    page_title="Dumpster Fire",
    page_icon="🗑️🔥",
)

bot_path = "bots"

if 'all_bots' not in st.session_state:
    st.session_state.all_bots = [
        {
            'path': path,
            'title': os.path.basename(path).split(".")[0].replace("-", " ").title(),
            'base': os.path.basename(path).split(".")[0],
            'tokens': [],
            'history': [],
            **yaml.safe_load(open(path))
        }
        for path in sorted(glob(f"{bot_path}/*.yaml"))
    ]

all_bots = st.session_state.all_bots

if 'bot' not in st.session_state:
    st.session_state.bot = st.session_state.all_bots[0]

with st.sidebar:
    selection = st.sidebar.radio("Who do you wanna talk to?", (bot['title'] for bot in all_bots))
    if selection:
        st.session_state.bot = filter(lambda b: b['title'] == selection, all_bots).__next__()

headers = _get_websocket_headers() or {}

st.subheader(st.session_state.bot['title'])

class MyCallbackHandler(StreamingStdOutCallbackHandler):

    def __init__(self, on_new_token):
        self.on_new_token = on_new_token

    def on_llm_new_token(self, token: str, **_) -> None:
        self.on_new_token(token)

bot = st.session_state.bot
tokens = st.session_state.bot['tokens']
history = st.session_state.bot['history']

def on_new_token(token):
    tokens.append(token)
    render_tokens()

def submit_text():
    chat = ChatOpenAI(client=None,
                      openai_api_key=os.environ['OPENAI_API_KEY'],
                      streaming=True,
                      callbacks=[MyCallbackHandler(on_new_token=on_new_token)],
                      temperature=bot.get('temperature', 0.7),
                      verbose=True)

    tokens.append(f" \n> {st.session_state.human} \n\n")
    render_tokens()

    history.append({'role': 'human', 'content': st.session_state.human})

    messages = [ROLE_TO_CLASS[h['role']](content=h['content']) for h in history]
    logger = logging.getLogger(__name__)
    logger.debug(f"History: {messages}")
    resp = chat(messages)

    log_chat(history, st.session_state.human, resp.content)

    history.append({'role': 'ai', 'content': resp.content})

    # only keep the last X history items
    st.session_state.bot['history'] = history[-HISTORY_CONTEXT_LENGTH:]
    st.session_state.human = ''

def log_chat(history, question, answer):
    import json
    from datetime import datetime
    logger = logging.getLogger('json')
    doc = {
        'timestamp': datetime.now().isoformat(),
        'bot': bot['base'],
        'question': question,
        'answer': answer,
        'history': history,
    }
    logger.info(json.dumps(doc))
    doc['history'] = json.dumps(doc['history'])
    data.log_chat(doc)

def render_tokens():
    if tokens:
        output_container.markdown(''.join(tokens))
    else:
        output_container.markdown(bot['intro'])

# st.sidebar.code(bot['template'])
# st.sidebar.code(st.session_state)
if 'css' in bot:
    st.markdown(bot['css'], unsafe_allow_html=True)

# Render previous messages
output_container = st.empty()
render_tokens()

# Divider and text input
st.divider()
col1, col2 = st.columns((14, 2))
with col1:
    st.text_area(key='human',
                  label='How can I help you?',
                  label_visibility='collapsed',
                  height=3,
                  placeholder='How can I help you?')
with col2:
    st.button('Send', on_click=submit_text, use_container_width=True)

