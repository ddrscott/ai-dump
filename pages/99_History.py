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
import json

def main():
    recent = data.recent_chats(limit=100)
    chats = [d['_source'] for d in recent]
    # df = pd.read_json(open('results.jsonl'), lines=True)
    df = pd.DataFrame(chats)
    df = df.reindex(columns=['question', 'answer', 'timestamp', 'history'])
    with st.sidebar:
        selection = aggrid_interactive_table(df)

    row = None
    if selection['selected_rows']:
        row = selection['selected_rows'][0]

    elif not df.empty:
        row = df.iloc[0].to_dict()

    if row:
        tab1, tab2, tab3 = st.tabs(["Chat", "Markdown", "Json"])

        tab1.markdown("""<style>
              .css-12syucy {
                background-color: #474F5F;
                color: #CACFD8;
              }
          </style>""", unsafe_allow_html=True)

        content = data.row_to_markdown(row)

        tab1.markdown(''.join(content))
        tab2.code(''.join(content), language='markdown')

        tab3.json(row)
    else:
        st.text('No history, yet')


def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, pre_selected_rows=[1], enableRowGroup=False, enableValue=False, enablePivot=False
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
