# FBA Spend-to-Profit Companion (Streamlit)

A minimalist, phone-friendly dashboard that calculates how much you need to **spend** this month to hit a target **net profit**, using your historical ROI/margins, with live progress vs target.

## Features
- KPI cards for revenue, profit, ROI, margin, revenue-to-spend
- **Required spend** via ROI method, Margin×Turn method, and a **blended** target
- **Gauge** showing current month COGS purchases vs spend target
- Trend charts and **sensitivity** analysis
- Data manager to upload/download CSVs
- Dark, elegant theme optimized for iPhone Safari

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open the URL on your iPhone (same Wi‑Fi) or deploy.

## Deploy (Streamlit Community Cloud)
1. Push this folder to a GitHub repo.
2. Create a new Streamlit app at share.streamlit.io, point to `app.py`.
3. Add the `data/` folder in the repo — you can update CSVs anytime in **Manage Data** page.

## iOS App-like Experience
- Open the deployed URL in Safari on iPhone → Share → **Add to Home Screen**. 
- It behaves like a fullscreen app with your brand.

## Data
- Replace `data/history.csv` with your monthly actuals (export from SellerToolkit/bookkeeping).
- Log this month's **COGS purchases** in `data/purchases.csv` for live target tracking.

## Model Notes
Required spend uses:
1) ROI method: `(Target + Fixed) / (Avg ROI × Realization) × (1 + Buffer)`
2) Margin×Turn: `(Target + Fixed) / (Avg Margin × Avg (Revenue/Spend) × Realization) × (1 + Buffer)`
3) Blended = geometric mean of (1) and (2) for robustness.

Tune **Rolling months**, **Realization**, and **Buffer** in the sidebar.

---

> Optional next steps:
> - Hook to SellerToolkit exports automatically (cron to refresh history.csv).
> - Persist data in a cloud DB (Supabase) and add auth.
> - Add alerts (Discord/Email) when spend lags target or TACOS drifts.
