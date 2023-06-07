import logging
from glob import glob
import os

import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import SystemMessage

import yaml

HISTORY_CONTEXT_LENGTH = 10

st.set_page_config(
    layout="wide",
    page_title="Dumpster Fire",
    page_icon="🗑️🔥",
)

bot_path = "bots"
bots = [
    {
        'path': path,
        'title': os.path.basename(path).split(".")[0].replace("-", " ").title(),
        'base': os.path.basename(path).split(".")[0]
    }
    for path in sorted(glob(f"{bot_path}/*.yaml"))
]

if 'bot' not in st.session_state:
    st.session_state.bot = bots[0]

with st.sidebar:
    selection = st.sidebar.radio("Who do you wanna talk to?", (t for bot in bots for t in [bot['title']]))
    st.session_state.bot = filter(lambda b: b['title'] == selection, bots).__next__()

headers = _get_websocket_headers() or {}

st.subheader(st.session_state.bot['title'])

bot_config = yaml.safe_load(open(st.session_state.bot['path']))

if 'tokens' not in st.session_state:
    st.session_state.tokens = {bot['title']: [] for bot in bots}

if 'history' not in st.session_state:
    st.session_state.history = {bot['title']: [] for bot in bots}

class MyCallbackHandler(StreamingStdOutCallbackHandler):

    def __init__(self, on_new_token):
        self.on_new_token = on_new_token

    def on_llm_new_token(self, token: str, **_) -> None:
        self.on_new_token(token)

bot = st.session_state.bot
tokens = st.session_state.tokens[bot['title']]
history = st.session_state.history[bot['title']]


def on_new_token(token):
    tokens.append(token)
    render_tokens()

def submit_text():
    chat = ChatOpenAI(client=None,
                      openai_api_key=os.environ['OPENAI_API_KEY'],
                      streaming=True,
                      callbacks=[MyCallbackHandler(on_new_token=on_new_token)],
                      temperature=bot_config.get('temperature', 0.7),
                      verbose=True)

    tokens.append(f" \n> {st.session_state.human} \n\n")
    render_tokens()

    system_history = bot_config['template'].format(human=st.session_state.human, history='\n'.join(history))

    resp = chat([SystemMessage(content=system_history)])
    history.append(f'Human: {st.session_state.human}\nYou:{resp.content}')
    log_chat(system_history, st.session_state.human, resp.content)
    # only keep the last X history items
    st.session_state.history[bot['title']] = history[-HISTORY_CONTEXT_LENGTH:]
    st.session_state.human = ''

def log_chat(context, question, answer):
    import json
    from datetime import datetime
    logger = logging.getLogger('json')
    logger.info(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'bot': bot['base'],
        'question': question,
        'answer': answer,
        'context': context,
    }))

def render_tokens():
    if tokens:
        output_container.markdown(''.join(tokens))
    else:
        output_container.markdown(bot_config['intro'])

# st.sidebar.code(bot_config['template'])
# st.sidebar.code(st.session_state)
if 'css' in bot_config:
    st.markdown(bot_config['css'], unsafe_allow_html=True)

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

