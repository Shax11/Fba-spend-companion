import streamlit as st
import pandas as pd
from utils import load_history, save_history, load_purchases, save_purchases

st.set_page_config(page_title="Manage Data", page_icon="🗂️")

st.markdown("## 🗂️ Manage Data")
st.caption("Edit tables inline, add new rows with the forms, and click **Save**. You can still upload/download CSVs if you prefer.")

hist = load_history()
purch = load_purchases()

tab1, tab2 = st.tabs(["History (Monthly Actuals)", "Purchases (This Month Spend)"])

with tab1:
    st.subheader("History")
    st.caption("Format: Month = YYYY-MM. Numbers in £ except Orders (count). Derived metrics will recompute automatically.")
    # Show editable view (hide derived columns)
    editable_cols = ["Month","Revenue","COGS_Sold","PPC","Amazon_Fees","Other_Variable","Fixed_Costs","Orders"]
    hist_edit = st.data_editor(
        hist[editable_cols],
        num_rows="dynamic",
        use_container_width=True,
        key="hist_editor",
        column_config={
            "Month": st.column_config.DateColumn(format="YYYY-MM", step="month"),
            "Revenue": st.column_config.NumberColumn(format="£%,.0f"),
            "COGS_Sold": st.column_config.NumberColumn(format="£%,.0f"),
            "PPC": st.column_config.NumberColumn(format="£%,.0f"),
            "Amazon_Fees": st.column_config.NumberColumn(format="£%,.0f"),
            "Other_Variable": st.column_config.NumberColumn(format="£%,.0f"),
            "Fixed_Costs": st.column_config.NumberColumn(format="£%,.0f"),
            "Orders": st.column_config.NumberColumn(format="%,.0f"),
        },
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Save History"):
            save_history(hist_edit)
            st.success("History saved.")
    with c2:
        up = st.file_uploader("Replace via CSV upload", type=["csv"], label_visibility="collapsed")
        if up:
            df = pd.read_csv(up)
            save_history(df)
            st.success("history.csv uploaded & saved. Refresh the page.")
    with c3:
        st.download_button(
            "⬇️ Download history.csv",
            data=open("data/history.csv","rb").read(),
            file_name="history.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("Purchases")
    st.caption("Log this month’s **COGS** purchases for the spend target gauge. Use categories like COGS, PPC, Fees.")
    purch_edit = st.data_editor(
        purch,
        num_rows="dynamic",
        use_container_width=True,
        key="purch_editor",
        column_config={
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Supplier": st.column_config.TextColumn(),
            "Category": st.column_config.SelectboxColumn(options=["COGS","PPC","Fees","Other"]),
            "AmountGBP": st.column_config.NumberColumn(format="£%,.2f"),
            "Notes": st.column_config.TextColumn(),
        },
    )

    with st.expander("➕ Quick add purchase"):
        c1, c2, c3 = st.columns(3)
        with c1:
            d = st.date_input("Date")
            supplier = st.text_input("Supplier")
        with c2:
            cat = st.selectbox("Category", ["COGS","PPC","Fees","Other"], index=0)
            amt = st.number_input("Amount £", min_value=0.0, step=10.0)
        with c3:
            notes = st.text_input("Notes")
            if st.button("Add Row"):
                new = pd.DataFrame([{"Date": d, "Supplier": supplier, "Category": cat, "AmountGBP": amt, "Notes": notes}])
                purch_edit = pd.concat([purch_edit, new], ignore_index=True)
                st.session_state["purch_editor"] = purch_edit  # refresh table

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💾 Save Purchases"):
            save_purchases(purch_edit)
            st.success("Purchases saved.")
    with c2:
        up2 = st.file_uploader("Replace via CSV upload", type=["csv"], label_visibility="collapsed", key="p_up")
        if up2:
            df2 = pd.read_csv(up2)
            save_purchases(df2)
            st.success("purchases.csv uploaded & saved. Refresh the page.")
    with c3:
        st.download_button(
            "⬇️ Download purchases.csv",
            data=open("data/purchases.csv","rb").read(),
            file_name="purchases.csv",
            mime="text/csv",
        )
