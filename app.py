import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trendy Pastries and Bakery - Executive POS",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NETLIFY-INSPIRED DARK THEME STYLING ---
st.markdown("""
    <style>
    /* Global Slate Dark Background & Text Styling */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Hide default Streamlit headers & footers for clean app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom Card Containers */
    .pos-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    .pos-card:hover {
        border-color: #f59e0b;
        box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.15);
    }

    /* Primary Buttons / Amber Accents */
    .stButton>button {
        background-color: #f59e0b;
        color: #0f172a;
        font-weight: 800;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #fbbf24;
        color: #0f172a;
    }

    /* Secondary / Utility Buttons */
    button[kind="secondary"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #334155 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE DATA ---
if 'products' not in st.session_state:
    st.session_state.products = [
        {"id": 1, "name": "Meat Pie (Beef)", "cost": 7.00, "price": 15.00, "category": "Pastries", "stock": 25, "image": "https://images.unsplash.com/photo-1621996346565-e3d5d6281273?w=300&auto=format&fit=crop&q=80"},
        {"id": 2, "name": "Chicken Pie", "cost": 9.00, "price": 18.00, "category": "Pastries", "stock": 20, "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=300&auto=format&fit=crop&q=80"},
        {"id": 3, "name": "Red Velvet Slice", "cost": 15.00, "price": 35.00, "category": "Cakes", "stock": 10, "image": "https://images.unsplash.com/photo-1586788680434-30d324b2d46f?w=300&auto=format&fit=crop&q=80"},
        {"id": 4, "name": "Ghana Sugar Bread", "cost": 10.00, "price": 20.00, "category": "Breads", "stock": 15, "image": "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?w=300&auto=format&fit=crop&q=80"},
        {"id": 5, "name": "Fresh Sobolo", "cost": 4.00, "price": 10.00, "category": "Drinks", "stock": 40, "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=300&auto=format&fit=crop&q=80"}
    ]

if 'cart' not in st.session_state:
    st.session_state.cart = []

if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []

if 'ceo_pin' not in st.session_state:
    st.session_state.ceo_pin = "1234"

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "pos"

# --- TOP HEADER BAR (Matching Netlify Header) ---
header_col1, header_col2, header_col3 = st.columns([1, 4, 3])
with header_col1:
    try:
        st.image("logo.jpg", width=45)
    except:
        st.markdown("🥐")
with header_col2:
    st.markdown("### <span style='color: #f59e0b;'>Trendy Pastries and Bakery</span>", unsafe_allow_html=True)
    st.caption("Executive POS & Financial Control Hub")

with header_col3:
    nav_cols = st.columns(3)
    if nav_cols[0].button("POS Terminal", key="nav_pos"):
        st.session_state.active_tab = "pos"
        st.rerun()
    if nav_cols[1].button("Dashboard", key="nav_dash"):
        st.session_state.active_tab = "dashboard"
        st.rerun()
    if nav_cols[2].button("Settings", key="nav_admin"):
        st.session_state.active_tab = "admin"
        st.rerun()

st.markdown("<hr style='margin: 10px 0px; border-color: #334155;'>", unsafe_allow_html=True)

# ==========================================
# VIEW 1: POS TERMINAL
# ==========================================
if st.session_state.active_tab == "pos":
    col_catalog, col_cart = st.columns([3, 2], gap="medium")

    with col_catalog:
        # Search & Filter Row
        search_query = st.text_input("🔍 Search pastries, cakes, breads...", "", key="search_prod")
        
        # Category Tabs
        cat_col1, cat_col2, cat_col3, cat_col4, cat_col5 = st.columns(5)
        if "selected_cat" not in st.session_state:
            st.session_state.selected_cat = "All"
            
        if cat_col1.button("All Items", key="cat_all"): st.session_state.selected_cat = "All"; st.rerun()
        if cat_col2.button("Pastries", key="cat_pas"): st.session_state.selected_cat = "Pastries"; st.rerun()
        if cat_col3.button("Cakes", key="cat_cak"): st.session_state.selected_cat = "Cakes"; st.rerun()
        if cat_col4.button("Breads", key="cat_brd"): st.session_state.selected_cat = "Breads"; st.rerun()
        if cat_col5.button("Drinks", key="cat_drk"): st.session_state.selected_cat = "Drinks"; st.rerun()

        st.markdown(f"<p style='font-size: 11px; color: #94a3b8; margin-top: 5px;'>Active Filter: <b>{st.session_state.selected_cat}</b></p>", unsafe_allow_html=True)

        # Filter Logic
        filtered = st.session_state.products
        if st.session_state.selected_cat != "All":
            filtered = [p for p in filtered if p["category"] == st.session_state.selected_cat]
        if search_query:
            filtered = [p for p in filtered if search_query.lower() in p["name"].lower()]

        # Product Grid (2 columns)
        grid_cols = st.columns(2)
        for idx, prod in enumerate(filtered):
            with grid_cols[idx % 2]:
                st.markdown(f"""
                    <div class="pos-card">
                        <img src="{prod['image']}" style="width: 100%; height: 100px; object-fit: cover; border-radius: 8px; margin-bottom: 8px;">
                        <div style="font-weight: bold; font-size: 13px; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{prod['name']}</div>
                        <div style="color: #f59e0b; font-weight: 800; font-size: 15px; margin: 4px 0;">GH₵ {prod['price']:.2f}</div>
                        <div style="font-size: 10px; color: #94a3b8;">{prod['stock']} units left</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Add ➕", key=f"add_cart_{prod['id']}"):
                    if prod['stock'] > 0:
                        exist = next((item for item in st.session_state.cart if item["id"] == prod["id"]), None)
                        if exist:
                            if exist["qty"] < prod['stock']:
                                exist["qty"] += 1
                        else:
                            st.session_state.cart.append({**prod, "qty": 1})
                        st.rerun()
                    else:
                        st.error("Out of stock!")
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    with col_cart:
        st.markdown("#### 🛒 Current Order")
        
        if not st.session_state.cart:
            st.info("No items in the order yet. Select items from the menu.")
        else:
            subtotal = 0.0
            for item in st.session_state.cart:
                item_total = item['price'] * item['qty']
                subtotal += item_total
                
                cc1, cc2, cc3, cc4 = st.columns([3, 2, 2, 1])
                cc1.markdown(f"**{item['name']}**")
                cc2.text(f"GH₵{item['price']:.2f}")
                cc3.text(f"Qty: {item['qty']}")
                if cc4.button("❌", key=f"rem_{item['id']}"):
                    st.session_state.cart = [i for i in st.session_state.cart if i["id"] != item["id"]]
                    st.rerun()

            st.markdown("<hr style='border-color: #334155;'>", unsafe_allow_html=True)
            
            discount_pct = st.number_input("Discount (%)", min_value=0, max_value=100, value=0, key="disc_input")
            discounted_subtotal = subtotal * (1 - discount_pct / 100)
            tax = discounted_subtotal * 0.08
            total = discounted_subtotal + tax

            col_sub1, col_sub2 = st.columns(2)
            col_sub1.text(f"Subtotal: GH₵ {subtotal:.2f}")
            col_sub2.text(f"Tax (8%): GH₵ {tax:.2f}")
            if discount_pct > 0:
                st.text(f"Discount: -GH₵ {(subtotal - discounted_subtotal):.2f}")
            
            st.markdown(f"### <span style='color: #f59e0b;'>Total: GH₵ {total:.2f}</span>", unsafe_allow_html=True)

            if st.button("Clear All", key="clear_cart_btn"):
                st.session_state.cart = []
                st.rerun()

            st.markdown("---")
            st.markdown("#### Select Payment Source")
            payment_method = st.radio("Payment Method", ["MTN MoMo", "Telecel MoMo", "Paystack API", "Cash"], horizontal=True)

            cash_tendered = 0.0
            if payment_method == "Cash":
                cash_tendered = st.number_input("Cash Tendered (GH₵)", min_value=0.0, value=total)
                change = cash_tendered - total
                st.markdown(f"**Change Due: <span style='color: #10b981;'>GH₵ {max(0, change):.2f}</span>**", unsafe_allow_html=True)

            if st.button("Proceed to Payment 🚀", key="checkout_btn"):
                if payment_method == "Cash" and cash_tendered < total:
                    st.error("Cash tendered is less than total amount due!")
                else:
                    for cart_item in st.session_state.cart:
                        for p in st.session_state.products:
                            if p["id"] == cart_item["id"]:
                                p["stock"] = max(0, p["stock"] - cart_item["qty"])

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
                    st.success(f"Payment successful! Order #{order['id']} processed via {payment_method}.")
                    st.balloons()

# ==========================================
# VIEW 2: CEO FINANCIAL DASHBOARD
# ==========================================
elif st.session_state.active_tab == "dashboard":
    st.markdown("## 📊 CEO Financial Dashboard & Analytics")
    st.caption("Audit sales sorted by Mobile Money, Paystack API, Card, and Cash.")

    if "dash_auth" not in st.session_state:
        st.session_state.dash_auth = False

    if not st.session_state.dash_auth:
        st.warning("🔒 CEO Verification Required. Enter your PIN to view financial records.")
        pin_entered = st.text_input("Enter CEO PIN (Default: 1234)", type="password", key="dash_pin_box")
        if st.button("Unlock Dashboard", key="unlock_dash_btn"):
            if pin_entered == st.session_state.ceo_pin:
                st.session_state.dash_auth = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    else:
        if st.button("Lock Dashboard", key="lock_dash_btn"):
            st.session_state.dash_auth = False
            st.rerun()

        sales = st.session_state.sales_history
        total_rev = sum(o["total"] for o in sales)
        total_orders = len(sales)
        avg_order = total_rev / total_orders if total_orders > 0 else 0
        est_profit = total_rev * 0.45 # estimated margin

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Revenue", f"GH₵ {total_rev:.2f}")
        k2.metric("Est. Net Profit", f"GH₵ {est_profit:.2f}")
        k3.metric("Total Orders", total_orders)
        k4.metric("Avg Order", f"GH₵ {avg_order:.2f}")

        st.markdown("---")
        st.markdown("#### Detailed Transaction Audit Trail")
        if sales:
            df_sales = pd.DataFrame([{
                "Order ID": o["id"],
                "Date & Time": o["timestamp"],
                "Source": o["method"],
                "Items": ", ".join([f"{i['qty']}x {i['name']}" for i in o["items"]]),
                "Total Paid (GH₵)": f"{o['total']:.2f}"
            } for o in sales])
            st.dataframe(df_sales, use_container_width=True)
        else:
            st.info("No recorded transactions yet.")

# ==========================================
# VIEW 3: CEO ADMIN & SETTINGS (Password Change)
# ==========================================
elif st.session_state.active_tab == "admin":
    st.markdown("## ⚙️ CEO Management Settings")

    admin_tab1, admin_tab2 = st.tabs(["🔑 Change CEO Password / PIN", "📦 Product Inventory"])

    with admin_tab1:
        st.markdown("### Change CEO Security PIN")
        st.caption("Set a custom secret PIN to restrict access to financial statements.")
        
        old_pin = st.text_input("Current CEO PIN", type="password", key="old_pin_input")
        new_pin = st.text_input("New Secret PIN (At least 4 digits)", type="password", key="new_pin_input")
        
        if st.button("Update Security PIN", key="save_pin_btn"):
            if old_pin == st.session_state.ceo_pin:
                if len(new_pin) >= 4:
                    st.session_state.ceo_pin = new_pin
                    st.success("CEO Security PIN updated successfully!")
                else:
                    st.error("New PIN must be at least 4 digits.")
            else:
                st.error("Current PIN is incorrect.")

    with admin_tab2:
        st.markdown("### Add New Product")
        with st.form("add_product_form"):
            p_name = st.text_input("Product Name")
            p_cat = st.selectbox("Category", ["Pastries", "Cakes", "Breads", "Drinks"])
            p_cost = st.number_input("Cost Price (GH₵)", min_value=0.0, value=5.0)
            p_price = st.number_input("Selling Price (GH₵)", min_value=0.0, value=15.0)
            p_stock = st.number_input("Initial Stock Quantity", min_value=1, value=20)
            p_img = st.text_input("Image URL (Unsplash)", value="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=300")
            
            submitted = st.form_submit_button("Save Product to Menu")
            if submitted and p_name:
                new_item = {
                    "id": len(st.session_state.products) + 1,
                    "name": p_name,
                    "cost": p_cost,
                    "price": p_price,
                    "category": p_cat,
                    "stock": p_stock,
                    "image": p_img
                }
                st.session_state.products.append(new_item)
                st.success(f"Added {p_name} successfully!")
                st.rerun()
