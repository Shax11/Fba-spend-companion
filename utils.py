import os, io
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

DATA_DIR = "data"
HIST_PATH = f"{DATA_DIR}/history.csv"
PURCH_PATH = f"{DATA_DIR}/purchases.csv"

def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_history(path=HIST_PATH):
    _ensure_dir()
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        sample = """Month,Revenue,COGS_Sold,PPC,Amazon_Fees,Other_Variable,Fixed_Costs,Orders
2025-02,12000,8000,900,2700,200,600,350
2025-03,9500,6000,650,2200,180,600,290
2025-04,10500,7200,700,2400,150,600,310
2025-05,13200,8500,1000,3000,220,600,410
2025-06,15000,9300,1100,3400,250,600,460
2025-07,11700,7700,800,2600,190,600,330
"""
        df = pd.read_csv(io.StringIO(sample))
    # coerce types
    df["Month"] = pd.to_datetime(df["Month"].astype(str) + "-01")
    num_cols = ["Revenue","COGS_Sold","PPC","Amazon_Fees","Other_Variable","Fixed_Costs","Orders"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df = df.sort_values("Month").reset_index(drop=True)

    core_profit = df["Revenue"] - df["COGS_Sold"] - df["PPC"] - df["Amazon_Fees"] - df["Other_Variable"]
    df["Net_Profit"] = core_profit - df["Fixed_Costs"]
    df["ROI_on_Spend"] = np.where(df["COGS_Sold"]>0, core_profit/df["COGS_Sold"], np.nan)
    df["Margin_on_Revenue"] = np.where(df["Revenue"]>0, core_profit/df["Revenue"], np.nan)
    df["Rev_to_Spend"] = np.where(df["COGS_Sold"]>0, df["Revenue"]/df["COGS_Sold"], np.nan)
    return df

def save_history(df: pd.DataFrame, path=HIST_PATH):
    _ensure_dir()
    out = df.copy()
    # store Month as YYYY-MM
    out["Month"] = pd.to_datetime(out["Month"]).dt.strftime("%Y-%m")
    cols = ["Month","Revenue","COGS_Sold","PPC","Amazon_Fees","Other_Variable","Fixed_Costs","Orders"]
    out[cols].to_csv(path, index=False)

def load_purchases(path=PURCH_PATH):
    _ensure_dir()
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        df = pd.DataFrame([
            {"Date":"2025-08-01","Supplier":"Acme Ltd","Category":"COGS","AmountGBP":1500,"Notes":"Widgets"},
            {"Date":"2025-08-05","Supplier":"Meta Ads","Category":"PPC","AmountGBP":200,"Notes":"Top of funnel"},
        ])
    df["Date"] = pd.to_datetime(df["Date"])
    df["AmountGBP"] = pd.to_numeric(df["AmountGBP"], errors="coerce").fillna(0.0)
    return df.sort_values("Date").reset_index(drop=True)

def save_purchases(df: pd.DataFrame, path=PURCH_PATH):
    _ensure_dir()
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"]).dt.strftime("%Y-%m-%d")
    cols = ["Date","Supplier","Category","AmountGBP","Notes"]
    out[cols].to_csv(path, index=False)
