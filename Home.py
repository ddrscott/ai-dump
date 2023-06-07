import os
import logging
import logging.config

import streamlit as st

def main():
    st.set_page_config(
        layout="wide",
        page_title="Dumpster Fire",
        page_icon="🗑️🔥",
    )

    st.markdown(open("README.md").read())

def setup_logging():
    config_file = "logging.ini"
    if os.path.isfile(config_file):
        logging.config.fileConfig(config_file)
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    setup_logging()
    main()
