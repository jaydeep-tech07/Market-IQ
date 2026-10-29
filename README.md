# 🛒 Smart Shop AI Management

**AI-Based Smart Inventory & Sales Prediction System**

Ek local shopkeeper ke liye AI-powered inventory aur sales management system —
products manage karo, sales record karo, AI se demand predict karo, aur smart
reorder recommendations paao.

## 📁 Project Structure

```
smart_shop_ai/
├── app.py            # Main Streamlit app (UI + navigation)
├── database.py       # SQLite database functions (CRUD)
├── prediction.py      # AI prediction & reorder recommendation logic
├── requirements.txt   # Python dependencies
└── README.md
```

## 🚀 How to Run (Local Computer)

1. Requirements install karein:
   ```
   pip install -r requirements.txt
   ```

2. App run karein:
   ```
   streamlit run app.py
   ```

3. Browser mein automatically khul jayega (usually `http://localhost:8501`).

Database (`smart_shop.db`) pehli baar app run karne par automatically ban jaayega —
kuch manually karne ki zaroorat nahi.

## 🚀 How to Run on Replit

1. Saari files (app.py, database.py, prediction.py, requirements.txt) Replit
   project mein upload karein.
2. Replit `.replit` config file mein run command set karein:
   ```
   run = "streamlit run app.py --server.port 8080 --server.address 0.0.0.0"
   ```
3. "Run" button dabayein.

## ✨ Features

- **Dashboard** — live metrics, sales trend, top products, stock charts
- **Inventory** — add / edit / delete / search products, auto low-stock detection
- **Sales** — record sales, auto stock deduction, sales history + CSV export
- **AI Prediction** — Linear-regression based demand forecast (only shown when
  enough historical data exists — minimum 5 days of sales)
- **Reorder Recommendation** — smart reorder quantities with urgency flags
- **Reports** — daily / weekly / monthly / product-wise reports, CSV downloads

## 🧠 How the AI Prediction Works (Simple Explanation)

1. Har product ki daily sales quantity nikaali jaati hai.
2. Ek simple **Linear Regression** model dekhtaa hai ki time ke saath sales
   badh rahi hai ya ghat rahi hai.
3. Us trend ke basis par agle N dinon ki demand predict hoti hai.
4. Agar kaafi data nahi hai (5 din se kam), to system saaf keh deta hai ki
   prediction possible nahi hai — galat number nahi dikhata.

## 📝 Notes

- Database empty hone par bhi app crash nahi hoga — har jagah graceful
  empty-state messages hain.
- Negative quantities, insufficient stock, aur missing product jaisी
  situations properly handle ki gayi hain.
