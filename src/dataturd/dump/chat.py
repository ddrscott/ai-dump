import logging
from glob import glob
import os

import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import SystemMessage

import yaml

from dataturd.dump import data

HISTORY_CONTEXT_LENGTH = 2048


def parse_bots():
    bot_path = "bots"
    return [
        {
            'path': path,
            'title': os.path.basename(path).split(".")[0].replace("-", " ").title(),
            'base': os.path.basename(path).split(".")[0]
        }
        for path in sorted(glob(f"{bot_path}/*.yaml"))
    ]

class MyCallbackHandler(StreamingStdOutCallbackHandler):

    def __init__(self, on_new_token):
        self.on_new_token = on_new_token

    def on_llm_new_token(self, token: str, **_) -> None:
        self.on_new_token(token)


def render(container, name, template, intro='How can I help you?', temperature=0.7, css=None, history_length=HISTORY_CONTEXT_LENGTH, **_):

    if 'tokens' not in st.session_state:
        st.session_state.tokens = [intro]

    if 'history' not in st.session_state:
        st.session_state.history = []

    tokens = st.session_state.tokens
    history = st.session_state.history

    def on_new_token(token):
        tokens.append(token)
        render_tokens()


    def submit_text():
        chat = ChatOpenAI(client=None,
                          streaming=True,
                          callbacks=[MyCallbackHandler(on_new_token=on_new_token)],
                          temperature=temperature,
                          verbose=True)

        tokens.append(f" \n> {st.session_state.human} \n\n")
        render_tokens()

        system_history = template.format(human=st.session_state.human, history='\n'.join(history))

        resp = chat([SystemMessage(content=system_history)])
        history.append(f'Human: {st.session_state.human}\nYou:{resp.content}')
        log_chat(system_history, st.session_state.human, resp.content)
        # only keep the last X history items
        st.session_state.history = history[-history_length:]
        st.session_state.human = ''

    def log_chat(context, question, answer):
        import json
        from datetime import datetime
        logger = logging.getLogger('json')
        doc = {
            'timestamp': datetime.now().isoformat(),
            'bot': name,
            'question': question,
            'answer': answer,
            'context': context,
        }
        logger.info(json.dumps(doc))
        data.log_chat(doc)

    def render_tokens():
        if tokens:
            output_container.markdown(''.join(tokens))
        else:
            output_container.markdown(intro)

    if css:
        st.markdown(css, unsafe_allow_html=True)

    # Render previous messages
    output_container = container.empty()
    render_tokens()

    # Divider and text input
    container.divider()
    col1, col2 = container.columns((14, 2))
    with col1:
        container.text_area(key='human',
                      label='How can I help you?',
                      label_visibility='collapsed',
                      height=3,
                      placeholder='How can I help you?')
    with col2:
        container.button('Send', on_click=submit_text, use_container_width=True)
