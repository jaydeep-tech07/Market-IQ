"""
app.py
------
Yeh main Streamlit application file hai.
Isse run karne ke liye terminal mein likhein:

    streamlit run app.py

Beginner ke liye: Streamlit ek Python library hai jisse hum simple
Python code likh kar hi website jaisa interface bana sakte hain —
HTML/CSS/JS seekhne ki zaroorat nahi.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

import database as db
import prediction as pred

# ------------------------------------------------------------------
# PAGE CONFIG (sabse pehle call hona chahiye)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Shop AI Management",
    page_icon="🛒",
    layout="wide",
)

# Database tables create karo (agar pehle se nahi hain to)
db.init_db()

# ------------------------------------------------------------------
# SIMPLE CUSTOM STYLING
# ------------------------------------------------------------------
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        border-left: 5px solid #4CAF50;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fb;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------
st.sidebar.title("🛒 Smart Shop AI")
st.sidebar.caption("AI-Based Inventory & Sales Management")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📦 Inventory",
        "💰 Sales",
        "🤖 AI Sales Prediction",
        "🔁 Reorder Recommendation",
        "📑 Reports",
        "ℹ️ About Project",
    ],
)

# Helper: products ko DataFrame mein convert karna (baar baar use hoga)
PRODUCT_COLUMNS = [
    "Product ID", "Name", "Category", "Purchase Price", "Selling Price",
    "Current Stock", "Min Stock", "Supplier", "Date Added",
]


def products_to_df(rows):
    if not rows:
        return pd.DataFrame(columns=PRODUCT_COLUMNS)
    return pd.DataFrame(rows, columns=PRODUCT_COLUMNS)


# ====================================================================
# PAGE 1: DASHBOARD
# ====================================================================
if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    products = db.get_all_products()
    df_products = products_to_df(products)
    low_stock = db.get_low_stock_products()
    out_of_stock = db.get_out_of_stock_products()
    today_sales = db.get_today_sales_total()
    total_sales = db.get_total_sales_amount()

    total_products = len(df_products)
    total_stock = int(df_products["Current Stock"].sum()) if not df_products.empty else 0

    # ---- Metric cards row 1 ----
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Products", total_products)
    c2.metric("Total Stock (units)", total_stock)
    c3.metric("Today's Sales (₹)", f"{today_sales:,.2f}")
    c4.metric("Total Sales (₹)", f"{total_sales:,.2f}")

    # ---- Metric cards row 2 ----
    c5, c6 = st.columns(2)
    c5.metric("Low Stock Products", len(low_stock))
    c6.metric("Out-of-Stock Products", len(out_of_stock))

    st.markdown("---")

    if df_products.empty:
        st.info("Abhi koi product add nahi kiya gaya hai. 'Inventory' page se product add karein.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Current Stock Levels")
            fig = px.bar(df_products, x="Name", y="Current Stock", color="Category")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Low Stock Products")
            if low_stock:
                df_low = products_to_df(low_stock)
                fig2 = px.bar(df_low, x="Name", y="Current Stock", color="Current Stock",
                              color_continuous_scale="Reds")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.success("Koi bhi product low-stock mein nahi hai! 🎉")

        # Sales trend
        sales = db.get_all_sales()
        if sales:
            df_sales = pd.DataFrame(
                sales, columns=["Sale ID", "Product", "Quantity", "Price", "Total", "Date"]
            )
            df_sales["Date"] = pd.to_datetime(df_sales["Date"]).dt.date
            daily_trend = df_sales.groupby("Date")["Total"].sum().reset_index()

            st.subheader("Sales Trend Over Time")
            fig3 = px.line(daily_trend, x="Date", y="Total", markers=True)
            st.plotly_chart(fig3, use_container_width=True)

            st.subheader("Top-Selling Products")
            top_products = df_sales.groupby("Product")["Quantity"].sum().reset_index()
            top_products = top_products.sort_values("Quantity", ascending=False).head(10)
            fig4 = px.bar(top_products, x="Product", y="Quantity")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Abhi tak koi sale record nahi hui hai — sales trend dikhane ke liye 'Sales' page se sale add karein.")


# ====================================================================
# PAGE 2: INVENTORY
# ====================================================================
elif page == "📦 Inventory":
    st.title("📦 Inventory Management")

    tab1, tab2, tab3 = st.tabs(["➕ Add Product", "📋 View / Edit / Delete", "🔍 Search"])

    # ---------------- ADD PRODUCT ----------------
    with tab1:
        st.subheader("Add New Product")
        with st.form("add_product_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name *")
                category = st.text_input("Category")
                purchase_price = st.number_input("Purchase Price (₹) *", min_value=0.0, step=1.0)
                selling_price = st.number_input("Selling Price (₹) *", min_value=0.0, step=1.0)
            with col2:
                current_stock = st.number_input("Current Stock *", min_value=0, step=1)
                min_stock = st.number_input("Minimum Stock Level *", min_value=0, step=1)
                supplier = st.text_input("Supplier")

            submitted = st.form_submit_button("Add Product")

            if submitted:
                if not name.strip():
                    st.error("Product Name zaroori hai.")
                elif selling_price < purchase_price:
                    st.warning("⚠️ Selling price purchase price se kam hai — check kar lein (product phir bhi add ho jayega).")
                    db.add_product(name, category, purchase_price, selling_price,
                                    current_stock, min_stock, supplier)
                    st.success(f"Product '{name}' successfully add ho gaya!")
                else:
                    db.add_product(name, category, purchase_price, selling_price,
                                    current_stock, min_stock, supplier)
                    st.success(f"Product '{name}' successfully add ho gaya!")

    # ---------------- VIEW / EDIT / DELETE ----------------
    with tab2:
        st.subheader("All Products")
        products = db.get_all_products()

        if not products:
            st.info("Koi product nahi mila. Pehle 'Add Product' tab se product add karein.")
        else:
            df = products_to_df(products)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Edit / Update Stock / Delete")

            product_names = {f"{row[1]} (ID: {row[0]})": row[0] for row in products}
            selected_label = st.selectbox("Product select karein", list(product_names.keys()))
            selected_id = product_names[selected_label]
            product = db.get_product_by_id(selected_id)

            if product:
                with st.form("edit_product_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        e_name = st.text_input("Name", value=product[1])
                        e_category = st.text_input("Category", value=product[2] or "")
                        e_purchase = st.number_input("Purchase Price (₹)", min_value=0.0, value=float(product[3]))
                        e_selling = st.number_input("Selling Price (₹)", min_value=0.0, value=float(product[4]))
                    with col2:
                        e_stock = st.number_input("Current Stock (direct update)", min_value=0, value=int(product[5]))
                        e_min_stock = st.number_input("Minimum Stock Level", min_value=0, value=int(product[6]))
                        e_supplier = st.text_input("Supplier", value=product[7] or "")

                    col_a, col_b = st.columns(2)
                    update_btn = col_a.form_submit_button("💾 Update Product")
                    delete_btn = col_b.form_submit_button("🗑️ Delete Product")

                    if update_btn:
                        db.update_product(selected_id, e_name, e_category, e_purchase, e_selling, e_min_stock, e_supplier)
                        db.update_stock(selected_id, e_stock)
                        st.success("Product update ho gaya!")
                        st.rerun()

                    if delete_btn:
                        db.delete_product(selected_id)
                        st.success("Product delete ho gaya!")
                        st.rerun()

    # ---------------- SEARCH ----------------
    with tab3:
        st.subheader("Search Products")
        keyword = st.text_input("Naam ya category se search karein")
        if keyword:
            results = db.search_products(keyword)
            if results:
                st.dataframe(products_to_df(results), use_container_width=True, hide_index=True)
            else:
                st.warning("Koi matching product nahi mila.")


# ====================================================================
# PAGE 3: SALES
# ====================================================================
elif page == "💰 Sales":
    st.title("💰 Sales Management")

    products = db.get_all_products()

    tab1, tab2 = st.tabs(["🧾 Record Sale", "📜 Sales History"])

    with tab1:
        st.subheader("Record a New Sale")
        if not products:
            st.warning("Pehle 'Inventory' page se products add karein.")
        else:
            product_map = {f"{p[1]} (Stock: {p[5]})": p for p in products}
            selected_label = st.selectbox("Product select karein", list(product_map.keys()))
            selected_product = product_map[selected_label]

            with st.form("sale_form"):
                quantity = st.number_input("Quantity Sold", min_value=1, step=1)
                selling_price = st.number_input(
                    "Selling Price (₹) per unit", min_value=0.0,
                    value=float(selected_product[4]), step=1.0
                )
                submitted = st.form_submit_button("Record Sale")

                if submitted:
                    success, message = db.record_sale(selected_product[0], quantity, selling_price)
                    if success:
                        st.success(f"✅ {message} Total Amount: ₹{quantity * selling_price:,.2f}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    with tab2:
        st.subheader("Sales History")
        sales = db.get_all_sales()
        if not sales:
            st.info("Abhi tak koi sale record nahi hui.")
        else:
            df_sales = pd.DataFrame(
                sales, columns=["Sale ID", "Product", "Quantity", "Price (₹)", "Total Amount (₹)", "Date"]
            )
            st.dataframe(df_sales, use_container_width=True, hide_index=True)
            csv = df_sales.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Sales History (CSV)", csv, "sales_history.csv", "text/csv")


# ====================================================================
# PAGE 4: AI SALES PREDICTION
# ====================================================================
elif page == "🤖 AI Sales Prediction":
    st.title("🤖 AI Sales Prediction")
    st.caption("Purani sales history dekh kar future demand predict ki jaati hai.")

    products = db.get_all_products()
    if not products:
        st.warning("Pehle products add karein.")
    else:
        product_map = {p[1]: p for p in products}
        selected_name = st.selectbox("Product select karein", list(product_map.keys()))
        selected_product = product_map[selected_name]

        days_ahead = st.slider("Kitne din aage predict karna hai?", 1, 30, 7)

        sales_rows = db.get_sales_for_prediction(selected_product[0])
        result = pred.predict_demand(sales_rows, days_ahead=days_ahead)

        if not result["enough_data"]:
            st.warning(f"⚠️ {result['message']}")
            if not result["daily_data"].empty:
                st.subheader("Available Sales Data")
                fig = px.bar(result["daily_data"], x="date", y="quantity")
                st.plotly_chart(fig, use_container_width=True)
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric(f"Predicted Demand (next {days_ahead} days)", f"{result['predicted_total']:.1f} units")
            col2.metric("Sales Trend", result["trend"].capitalize())
            col3.metric("Current Stock", selected_product[5])

            st.subheader("Historical Daily Sales")
            fig = px.line(result["daily_data"], x="date", y="quantity", markers=True,
                          title="Past Sales (used for prediction)")
            st.plotly_chart(fig, use_container_width=True)

            trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}
            st.info(f"{trend_emoji.get(result['trend'], '')} Sales trend is **{result['trend']}**.")


# ====================================================================
# PAGE 5: REORDER RECOMMENDATION
# ====================================================================
elif page == "🔁 Reorder Recommendation":
    st.title("🔁 AI Reorder Recommendation")
    st.caption("Current stock, minimum level aur predicted demand ke basis par reorder suggestion.")

    products = db.get_all_products()
    if not products:
        st.warning("Pehle products add karein.")
    else:
        rows = []
        for p in products:
            product_id, name, category, purchase_price, selling_price, current_stock, min_stock, supplier, date_added = p
            sales_rows = db.get_sales_for_prediction(product_id)
            result = pred.predict_demand(sales_rows, days_ahead=7)
            reorder_qty, reason = pred.recommend_reorder(
                current_stock, min_stock, result["predicted_total"], result["enough_data"]
            )

            urgency = "🔴 URGENT" if current_stock == 0 else ("🟠 Soon" if reorder_qty > 0 else "🟢 OK")

            rows.append({
                "Product": name,
                "Current Stock": current_stock,
                "Predicted Demand (7d)": result["predicted_total"] if result["enough_data"] else "N/A",
                "Min Stock": min_stock,
                "Recommended Order Qty": reorder_qty,
                "Urgency": urgency,
                "Reason": reason,
            })

        df_reorder = pd.DataFrame(rows)

        urgent = df_reorder[df_reorder["Urgency"] == "🔴 URGENT"]
        if not urgent.empty:
            st.error(f"⚠️ {len(urgent)} product(s) ko URGENT restocking chahiye!")

        st.dataframe(df_reorder, use_container_width=True, hide_index=True)

        csv = df_reorder.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Reorder Report (CSV)", csv, "reorder_recommendations.csv", "text/csv")


# ====================================================================
# PAGE 6: REPORTS
# ====================================================================
elif page == "📑 Reports":
    st.title("📑 Reports")

    sales = db.get_all_sales()
    products = db.get_all_products()

    if not sales:
        st.info("Reports dikhane ke liye pehle kuch sales record karein.")
    else:
        df_sales = pd.DataFrame(
            sales, columns=["Sale ID", "Product", "Quantity", "Price", "Total", "Date"]
        )
        df_sales["Date"] = pd.to_datetime(df_sales["Date"])
        df_sales["Day"] = df_sales["Date"].dt.date
        df_sales["Week"] = df_sales["Date"].dt.isocalendar().week
        df_sales["Month"] = df_sales["Date"].dt.to_period("M").astype(str)

        report_type = st.selectbox(
            "Report Type",
            ["Daily Sales", "Weekly Sales", "Monthly Sales", "Product-wise Sales", "Revenue Summary"]
        )

        if report_type == "Daily Sales":
            report = df_sales.groupby("Day")["Total"].sum().reset_index()
            st.dataframe(report, use_container_width=True, hide_index=True)
            st.plotly_chart(px.bar(report, x="Day", y="Total"), use_container_width=True)

        elif report_type == "Weekly Sales":
            report = df_sales.groupby("Week")["Total"].sum().reset_index()
            st.dataframe(report, use_container_width=True, hide_index=True)
            st.plotly_chart(px.bar(report, x="Week", y="Total"), use_container_width=True)

        elif report_type == "Monthly Sales":
            report = df_sales.groupby("Month")["Total"].sum().reset_index()
            st.dataframe(report, use_container_width=True, hide_index=True)
            st.plotly_chart(px.bar(report, x="Month", y="Total"), use_container_width=True)

        elif report_type == "Product-wise Sales":
            report = df_sales.groupby("Product").agg(
                Total_Quantity=("Quantity", "sum"), Total_Revenue=("Total", "sum")
            ).reset_index()
            st.dataframe(report, use_container_width=True, hide_index=True)
            st.plotly_chart(px.pie(report, names="Product", values="Total_Revenue"), use_container_width=True)

        elif report_type == "Revenue Summary":
            total_revenue = df_sales["Total"].sum()
            total_units = df_sales["Quantity"].sum()
            st.metric("Total Revenue (₹)", f"{total_revenue:,.2f}")
            st.metric("Total Units Sold", int(total_units))
            report = df_sales

        csv = report.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Report (CSV)", csv, f"{report_type.replace(' ', '_').lower()}.csv", "text/csv")

    st.markdown("---")
    st.subheader("Inventory Status Report")
    if products:
        df_products = products_to_df(products)
        st.dataframe(df_products, use_container_width=True, hide_index=True)
        low_stock_df = products_to_df(db.get_low_stock_products())
        if not low_stock_df.empty:
            st.warning("Low Stock Products:")
            st.dataframe(low_stock_df, use_container_width=True, hide_index=True)
    else:
        st.info("Koi product nahi mila.")


# ====================================================================
# PAGE 7: ABOUT
# ====================================================================
elif page == "ℹ️ About Project":
    st.title("ℹ️ About This Project")
    st.markdown("""
    ### Smart Shop AI Management

    **AI-Based Smart Inventory & Sales Prediction System**

    Yeh application local shopkeepers ke liye banaya gaya hai taaki wo:
    - Apna inventory manage kar sakein
    - Sales record kar sakein
    - AI ki madad se future demand predict kar sakein
    - Smart reorder recommendations paa sakein

    **Tech Stack:**
    - Python
    - Streamlit (UI)
    - Pandas & NumPy (data handling)
    - Scikit-learn (AI prediction)
    - SQLite (database)
    - Plotly (charts)

    **Note:** AI predictions tabhi dikhayi jaati hain jab kaafi historical
    sales data available ho, taaki galat/misleading predictions na dein.
    """)
