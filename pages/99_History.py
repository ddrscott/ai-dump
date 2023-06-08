import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

st.set_page_config(
    layout="wide",
    page_title="Chat History :: Dumpster Fire",
    page_icon="📖🗑️🔥",
)

import pandas as pd

def main():
    df = pd.read_json(open('results.jsonl'), lines=True)

    col1, col2 = st.columns((1, 2))

    # col1.data_editor(data=df, key='results', hide_index=True, use_container_width=True)

    with col1:
        selection = aggrid_interactive_table(df)

    if selection['selected_rows']:
        row = selection['selected_rows'][0]

        tab1, tab2 = col2.tabs(["Chat", "Json"])

        tab1.markdown("""<style>
              .css-12syucy {
                background-color: #474F5F;
                color: #CACFD8;
              }
          </style>""", unsafe_allow_html=True)
        tab1.markdown(f"\n > {row['question']}\n")
        tab1.markdown(row['answer'])
        tab2.json(selection['selected_rows'][0])

    else:
        col2.text('No row selected')


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
    )

    return selection


if __name__ == "__main__":
    main()
