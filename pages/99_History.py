import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

st.set_page_config(
    layout="wide",
    page_title="Chat History :: Dumpster Fire",
    page_icon="📖🗑️🔥",
)

from dataturd.dump import data
import pandas as pd

def main():
    recent = data.recent_chats(limit=100)
    chats = [d['_source'] for d in recent]
    # df = pd.read_json(open('results.jsonl'), lines=True)
    df = pd.DataFrame(chats)

    with st.sidebar:
        selection = aggrid_interactive_table(df)

    if selection['selected_rows']:
        row = selection['selected_rows'][0]

        tab1, tab2, tab3 = st.tabs(["Chat", "Context", "Json"])

        tab1.markdown("""<style>
              .css-12syucy {
                background-color: #474F5F;
                color: #CACFD8;
              }
          </style>""", unsafe_allow_html=True)
        tab1.markdown(f"\n > {row['question']}\n")
        tab1.markdown(row['answer'])
        tab2.markdown(row['context'])
        tab3.json(selection['selected_rows'][0])

    else:
        st.text('No row selected')


def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="streamlit",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        height=400,
    )

    return selection


if __name__ == "__main__":
    main()
