
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

def parse_month(s):
    # Accept "YYYY-MM" or timestamp-like; return first day of month
    try:
        if isinstance(s, str) and len(s) == 7 and s[4] == "-":
            return pd.to_datetime(s + "-01")
        return pd.to_datetime(s).to_period("M").to_timestamp()
    except Exception:
        return pd.NaT

def load_history(path="data/history.csv"):
    df = pd.read_csv(path)
    df["Month"] = df["Month"].apply(parse_month)
    df = df.sort_values("Month")
    # Derived
    df["Net_Profit"] = df["Revenue"] - df["COGS_Sold"] - df["PPC"] - df["Amazon_Fees"] - df["Other_Variable"] - df["Fixed_Costs"]
    core_profit = df["Revenue"] - df["COGS_Sold"] - df["PPC"] - df["Amazon_Fees"] - df["Other_Variable"]
    df["ROI_on_Spend"] = np.where(df["COGS_Sold"] > 0, core_profit / df["COGS_Sold"], np.nan)
    df["Margin_on_Revenue"] = np.where(df["Revenue"] > 0, core_profit / df["Revenue"], np.nan)
    df["Rev_to_Spend"] = np.where(df["COGS_Sold"] > 0, df["Revenue"] / df["COGS_Sold"], np.nan)
    return df

def load_purchases(path="data/purchases.csv"):
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date")

def rolling_avgs(df, n=3):
    if df.empty:
        return np.nan, np.nan, np.nan
    tail = df.tail(n)
    return tail["ROI_on_Spend"].mean(), tail["Margin_on_Revenue"].mean(), tail["Rev_to_Spend"].mean()

def compute_required_spend(target_profit, fixed_costs, avg_roi, avg_margin, avg_rev_to_spend, realization, buffer):
    # Two methods + harmonic blend
    spend_roi = (target_profit + fixed_costs) / max(avg_roi * realization, 1e-9) * (1 + buffer)
    spend_margin = (target_profit + fixed_costs) / max(avg_margin * avg_rev_to_spend * realization, 1e-9) * (1 + buffer)
    # blended as geometric mean for robustness
    blended = np.sqrt(spend_roi * spend_margin)
    return spend_roi, spend_margin, blended

def month_start(dt=None):
    dt = pd.Timestamp.utcnow() if dt is None else pd.to_datetime(dt)
    return dt.to_period("M").to_timestamp()
