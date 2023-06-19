import logging
import os

import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import SystemMessage, HumanMessage, AIMessage

import json

from dataturd.dump import data, bots

HISTORY_CONTEXT_LENGTH = 2048

ROLE_TO_CLASS = {
    'system': SystemMessage,
    'human': HumanMessage,
    'ai': AIMessage
}

st.set_page_config(
    layout="wide",
    page_title="App Builder",
    page_icon="🗑️🔥",
)

app_builder_bot = filter(lambda b: b['base'] == 'literate-markdown', bots.all_bots()).__next__()

if 'bot' not in st.session_state or st.session_state.bot['base'] != app_builder_bot['base']:
    st.session_state.bot = {**app_builder_bot}

headers = _get_websocket_headers() or {}

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
        raw_container.code(''.join(tokens), language='markdown')
    else:
        output_container.markdown(bot['intro'])
        raw_container.code(bot['intro'], language='markdown')

def save_markdown():
    if tokens:
        content = ''.join(tokens)
        save_path = os.path.join('prompts', st.session_state.save_as)
        if save_path:
            with open(save_path, 'w') as f:
                f.write(content)
            st.success(f'Saved to {save_path}')

def on_reset():
    st.session_state.bot = {**app_builder_bot}
    st.session_state.human = ''
    st.session_state.save_as = ''


if 'css' in bot:
    st.markdown(bot['css'], unsafe_allow_html=True)

# Render previous messages
tab1, tab2 = st.tabs(["Chat", "Markdown"])
output_container = tab1.empty()

col1, col2 = tab2.columns((4, 2))
with col1:
    st.markdown('### Fences')

with col2:
    st.text_input(key='save_as',
                  label='',
                  label_visibility='collapsed',
                  placeholder='Save Markdown as...')
    st.button('Save', on_click=save_markdown, use_container_width=True)

raw_container = tab2.empty()
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

