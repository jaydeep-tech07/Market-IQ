"""
prediction.py
--------------
Yeh file AI/ML ka kaam karti hai: purani sales dekh kar future demand predict karna.

Beginner ke liye simple explanation:
- Hum har din ki total quantity nikaalte hain (kitna becha gaya)
- Phir ek simple "Linear Regression" model use karte hain jo dekhta hai
  ki time ke saath sales badh rahi hai ya ghat rahi hai (trend)
- Us trend ke basis par agle kuch dino ki demand predict karte hain

IMPORTANT: Agar data bahut kam hai (jaise sirf 1-2 din ka), to hum
prediction nahi dikhate — kyunki wo galat/misleading hoga.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Kam se kam itne alag dino ka sales data chahiye tabhi prediction karenge
MIN_DAYS_REQUIRED = 5


def prepare_daily_sales(sales_rows):
    """
    Raw sales rows (date, quantity) ko daily-total mein convert karta hai.
    Return: pandas DataFrame with columns ['date', 'quantity']
    """
    if not sales_rows:
        return pd.DataFrame(columns=["date", "quantity"])

    df = pd.DataFrame(sales_rows, columns=["sale_date", "quantity"])
    # sale_date mein time bhi hai, isliye sirf date nikaalte hain
    df["date"] = pd.to_datetime(df["sale_date"]).dt.date
    daily = df.groupby("date")["quantity"].sum().reset_index()
    daily = daily.sort_values("date")
    return daily


def predict_demand(sales_rows, days_ahead=7):
    """
    Product ki sales history lekar future demand predict karta hai.

    Return: dictionary with keys:
        - "enough_data": bool
        - "message": str (agar data kam hai to explanation)
        - "predicted_total": float (agle 'days_ahead' dinon ki total predicted demand)
        - "trend": "increasing" / "decreasing" / "stable"
        - "daily_data": DataFrame (chart banane ke liye)
    """
    daily = prepare_daily_sales(sales_rows)

    if len(daily) < MIN_DAYS_REQUIRED:
        return {
            "enough_data": False,
            "message": f"Prediction ke liye kam se kam {MIN_DAYS_REQUIRED} alag dinon ka sales "
                       f"data chahiye. Abhi sirf {len(daily)} din ka data available hai. "
                       f"Jaise-jaise sales record hongi, prediction accurate hoti jayegi.",
            "predicted_total": None,
            "trend": None,
            "daily_data": daily,
        }

    # X = day number (0, 1, 2, ...), y = us din ki total quantity
    daily = daily.reset_index(drop=True)
    X = np.arange(len(daily)).reshape(-1, 1)
    y = daily["quantity"].values

    model = LinearRegression()
    model.fit(X, y)

    # Agle 'days_ahead' dinon ke liye prediction
    future_X = np.arange(len(daily), len(daily) + days_ahead).reshape(-1, 1)
    future_predictions = model.predict(future_X)

    # Negative predictions ko 0 kar dete hain (demand negative nahi ho sakti)
    future_predictions = np.clip(future_predictions, 0, None)
    predicted_total = float(np.sum(future_predictions))

    # Trend decide karte hain slope (model.coef_) ke basis par
    slope = model.coef_[0]
    if slope > 0.05:
        trend = "increasing"
    elif slope < -0.05:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "enough_data": True,
        "message": "",
        "predicted_total": round(predicted_total, 1),
        "trend": trend,
        "daily_data": daily,
    }


def recommend_reorder(current_stock, min_stock, predicted_total, enough_data):
    """
    Reorder quantity recommend karta hai.

    Logic (simple aur samajhne layak):
    - Agar prediction available nahi hai -> sirf min_stock ke basis par recommend karo
    - Agar prediction available hai -> (predicted demand + min_stock buffer) - current stock
    """
    if not enough_data or predicted_total is None:
        # Fallback: sirf minimum stock rule use karo
        if current_stock <= min_stock:
            reorder_qty = max(min_stock * 2 - current_stock, 0)
            reason = "Historical data kam hai, isliye minimum stock level ke basis par recommend kiya gaya."
        else:
            reorder_qty = 0
            reason = "Stock abhi theek hai, reorder ki zaroorat nahi."
        return reorder_qty, reason

    required_stock = predicted_total + min_stock
    reorder_qty = max(round(required_stock - current_stock), 0)

    if reorder_qty == 0:
        reason = "Current stock predicted demand ke liye kaafi hai."
    elif current_stock == 0:
        reason = "Product out of stock hai — turant reorder karein (URGENT)."
    elif current_stock <= min_stock:
        reason = "Stock minimum level se neeche/barabar hai aur demand bhi predicted hai."
    else:
        reason = "Predicted demand current stock se zyada hai."

    return reorder_qty, reason
