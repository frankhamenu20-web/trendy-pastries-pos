import streamlit as st
import pandas as pd
from datetime import datetime
import json
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trendy Pastries & Bakery - POS Hub",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DARK MODE & CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .metric-card { background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE DATA ---
if 'products' not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "Meat Pie (Beef)", "cost": 7.00, "price": 15.00, "category": "Pastries", "stock": 25},
        {"id": 2, "name": "Chicken Pie", "cost": 9.00, "price": 18.00, "category": "Pastries", "stock": 20},
        {"id": 3, "name": "Red Velvet Slice", "cost": 15.00, "price": 35.00, "category": "Cakes", "stock": 10},
        {"id": 4, "name": "Ghana Sugar Bread", "cost": 10.00, "price": 20.00, "category": "Breads", "stock": 15},
        {"id": 5, "name": "Fresh Sobolo", "cost": 4.00, "price": 10.00, "category": "Drinks", "stock": 40}
    ]

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []

if 'ceo_pin' not in st.session_state:
    st.session_state.ceo_pin = "1234"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- HEADER LOGO & TITLE ---
col1, col2 = st.columns([1, 6])
with col1:
    try:
        st.image("logo.jpg", width=70)
    except:
        st.markdown("🥐")
with col2:
    st.markdown("### Trendy Pastries and Bakery")
    st.caption("Executive POS & Financial Control Hub")

st.divider()

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("## Navigation")
app_mode = st.sidebar.radio("Choose Mode", ["POS Terminal", "CEO Financial Dashboard", "CEO Admin & Settings"])

# ==========================================
# 1. POS TERMINAL VIEW
# ==========================================
if app_mode == "POS Terminal":
    col_catalog, col_cart = st.columns([3, 2])

    with col_catalog:
        st.markdown("#### 🛍️ Product Catalog")
        
        # Category Filter & Search
        cat_filter = st.selectbox("Filter Category", ["All", "Pastries", "Cakes", "Breads", "Drinks"])
        search_query = st.text_input("🔍 Search products...", "").lower()

        # Filter products
        filtered_products = st.session_state.products
        if cat_filter != "All":
            filtered_products = [p for p in filtered_products if p["category"] == cat_filter]
        if search_query:
            filtered_products = [p for p in filtered_products if search_query in p["name"].lower()]

        # Display Grid
        cols = st.columns(2)
        for idx, prod in enumerate(filtered_products):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"**{prod['name']}**")
                    st.write(f"Price: **GH₵ {prod['price']:.2f}** | Stock: {prod['stock']}")
                    if st.button(f"Add to Cart", key=f"add_{prod['id']}"):
                        if prod['stock'] > 0:
                            # Add to cart logic
                            exist = next((item for item in st.session_state.cart if item["id"] == prod["id"]), None)
                            if exist:
                                if exist["qty"] < prod["stock"]:
                                    exist["qty"] += 1
                                else:
                                    st.warning("Max stock reached!")
                            else:
                                st.session_state.cart.append({**prod, "qty": 1})
                            st.rerun()
                        else:
                            st.error("Out of stock!")

    with col_cart:
        st.markdown("#### 🛒 Current Order")
        
        if not st.session_state.cart:
            st.info("No items in the order yet.")
        else:
            subtotal = 0.0
            for item in st.session_state.cart:
                item_total = item['price'] * item['qty']
                subtotal += item_total
                
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"**{item['name']}**")
                c2.write(f"{item['qty']} x GH₵{item['price']:.2f}")
                if c3.button("❌", key=f"del_{item['id']}"):
                    st.session_state.cart = [i for i in st.session_state.cart if i["id"] != item["id"]]
                    st.rerun()

            st.divider()
            
            # Discounts & Taxes
            discount_pct = st.number_input("Discount (%)", min_value=0, max_value=100, value=0)
            discounted_subtotal = subtotal * (1 - discount_pct / 100)
            tax = discounted_subtotal * 0.08
            total = discounted_subtotal + tax

            st.write(f"Subtotal: GH₵ {subtotal:.2f}")
            if discount_pct > 0:
                st.write(f"Discount ({discount_pct}%): -GH₵ {(subtotal - discounted_subtotal):.2f}")
            st.write(f"Tax (8%): GH₵ {tax:.2f}")
            st.markdown(f"### Total: GH₵ {total:.2f}")

            if st.button("Clear Cart", type="secondary"):
                st.session_state.cart = []
                st.rerun()

            st.divider()
            st.markdown("#### Select Payment Source")
            payment_method = st.radio("Payment Method", ["MTN MoMo", "Telecel MoMo", "Paystack API", "Cash"])

            cash_tendered = 0.0
            if payment_method == "Cash":
                cash_tendered = st.number_input("Cash Tendered (GH₵)", min_value=0.0, value=total)
                change = cash_tendered - total
                st.write(f"**Change Due: GH₵ {max(0, change):.2f}**")

            if st.button("🚀 Complete Payment & Checkout", type="primary"):
                if payment_method == "Cash" and cash_tendered < total:
                    st.error("Cash tendered is less than total amount due!")
                else:
                    # Deduct stock
                    for cart_item in st.session_state.cart:
                        for p in st.session_state.products:
                            if p["id"] == cart_item["id"]:
                                p["stock"] = max(0, p["stock"] - cart_item["qty"])

                    # Save Order
                    order = {
                        "id": f"TPB-{1000 + len(st.session_state.sales_history) + 1}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "items": list(st.session_state.cart),
                        "subtotal": subtotal,
                        "total": total,
                        "method": payment_method
                    }
                    st.session_state.sales_history.insert(0, order)
                    st.session_state.cart = []
                    st.success(f"Order {order['id']} processed successfully via {payment_method}!")
                    st.balloons()

# ==========================================
# 2. CEO FINANCIAL DASHBOARD VIEW
# ==========================================
elif app_mode == "CEO Financial Dashboard":
    st.markdown("## 📊 CEO Financial Dashboard & Analytics")

    if not st.session_state.authenticated:
        st.warning("🔒 Secure area. Please enter your CEO PIN to view financial history.")
        entered_pin = st.text_input("Enter CEO PIN", type="password")
        if st.button("Unlock Dashboard"):
            if entered_pin == st.session_state.ceo_pin:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    else:
        if st.button("Lock Dashboard"):
            st.session_state.authenticated = False
            st.rerun()

        sales = st.session_state.sales_history
        total_rev = sum(o["total"] for o in sales)
        total_orders = len(sales)
        avg_order = total_rev / total_orders if total_orders > 0 else 0

        # KPI Metrics
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Revenue", f"GH₵ {total_rev:.2f}")
        k2.metric("Total Orders", total_orders)
        k3.metric("Average Order Value", f"GH₵ {avg_order:.2f}")

        st.divider()
        st.markdown("#### Detailed Transaction Audit Trail")
        if sales:
            df_sales = pd.DataFrame([{
                "Order ID": o["id"],
                "Date/Time": o["timestamp"],
                "Method": o["method"],
                "Total (GH₵)": f"{o['total']:.2f}",
                "Items": ", ".join([f"{i['qty']}x {i['name']}" for i in o["items"]])
            } for o in sales])
            st.dataframe(df_sales, use_container_width=True)
        else:
            st.info("No recorded transactions yet.")

# ==========================================
# 3. CEO ADMIN & SETTINGS VIEW (Password Change)
# ==========================================
elif app_mode == "CEO Admin & Settings":
    st.markdown("## ⚙️ CEO Management Settings")

    admin_tab1, admin_tab2 = st.tabs(["🔒 Change CEO Password / PIN", "📦 Product Inventory"])

    with admin_tab1:
        st.markdown("### Update Security PIN")
        current_pin_input = st.text_input("Current CEO PIN", type="password")
        new_pin_input = st.text_input("New Secret PIN (At least 4 digits)", type="password")
        
        if st.button("Update Password / PIN"):
            if current_pin_input == st.session_state.ceo_pin:
                if len(new_pin_input) >= 4:
                    st.session_state.ceo_pin = new_pin_input
                    st.success("CEO Security PIN updated successfully!")
                else:
                    st.error("New PIN must be at least 4 characters long.")
            else:
                st.error("Current PIN is incorrect.")

    with admin_tab2:
        st.markdown("### Manage Products")
        with st.form("add_prod_form"):
            p_name = st.text_input("Product Name")
            p_cat = st.selectbox("Category", ["Pastries", "Cakes", "Breads", "Drinks"])
            p_cost = st.number_input("Cost Price (GH₵)", min_value=0.0, value=5.0)
            p_price = st.number_input("Selling Price (GH₵)", min_value=0.0, value=10.0)
            p_stock = st.number_input("Initial Stock", min_value=1, value=20)
            
            submitted = st.form_submit_button("Add Product")
            if submitted and p_name:
                new_p = {
                    "id": len(st.session_state.products) + 1,
                    "name": p_name,
                    "cost": p_cost,
                    "price": p_price,
                    "category": p_cat,
                    "stock": p_stock
                }
                st.session_state.products.append(new_p)
                st.success(f"Added {p_name} to inventory!")
                st.rerun()