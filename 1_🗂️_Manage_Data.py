
import streamlit as st
import pandas as pd
from utils import load_history, load_purchases

st.set_page_config(page_title="Manage Data", page_icon="🗂️")

st.markdown("## 🗂️ Manage Data")
st.caption("Upload/Download your CSVs and edit rows inline. Files live in the `data/` folder.")

tab1, tab2 = st.tabs(["History (Monthly Actuals)", "Purchases (This Month Spend)"])

with tab1:
    st.subheader("History")
    df = load_history()
    st.dataframe(df, use_container_width=True)
    uploaded = st.file_uploader("Upload history.csv", type=["csv"])
    if uploaded:
        with open("data/history.csv","wb") as f:
            f.write(uploaded.read())
        st.success("history.csv replaced. Refresh the page.")
    if st.button("Download current history.csv"):
        st.download_button("Click to download", data=open("data/history.csv","rb").read(), file_name="history.csv")
with tab2:
    st.subheader("Purchases")
    df2 = load_purchases()
    st.dataframe(df2, use_container_width=True)
    uploaded2 = st.file_uploader("Upload purchases.csv", type=["csv"])
    if uploaded2:
        with open("data/purchases.csv","wb") as f:
            f.write(uploaded2.read())
        st.success("purchases.csv replaced. Refresh the page.")
    if st.button("Download current purchases.csv"):
        st.download_button("Click to download", data=open("data/purchases.csv","rb").read(), file_name="purchases.csv")
