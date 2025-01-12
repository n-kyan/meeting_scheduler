import streamlit as st

def page_init():
    st.set_page_config(
        page_title="Kyan Nelson - Scholars and Honors Student add Leeds CU Boulder",
        # page_icon="💼",
        layout="wide"
    )

    col1, col2 = st.columns([2, 1])

    return col1, col2