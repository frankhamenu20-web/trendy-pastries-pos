import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
import os
from PIL import Image

# --- LOAD CUSTOM LOGO FOR BROWSER TAB (FAVICON) ---
try:
    favicon = Image.open("logo.jpg")
except:
    favicon = "🥐"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trendy Pastries and Bakery",
    page_icon=favicon,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LOAD LOCAL LOGO AS BASE64 FOR HEADER RENDERING ---
def get_logo_base64():
    if os.path.exists("logo.jpg"):
        with open("logo.jpg", "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_logo_base64()

# --- NETLIFY-INSPIRED DARK MOBILE UI STYLING ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        max-width: 100vw !important;
        overflow-x: hidden !important;
        background-color: #0f172a !important;
        color: #f8fafc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        padding-top: 0.8rem !important;
        max-width: 600px !important;
    }

    /* Card Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* Custom Button Styling */
    .stButton>button {
        background-color: #1e293b;
        color: #f8fafc;
        font-weight: 700;
        border-radius: 10px;
        border: 1px solid #334155;
        padding: 0.4rem 0.5rem;
        font-size: 12px;
        width: 100%;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #f59e0b !important;
        color: #0f172a !important;
        border-color: #f59e0b !important;
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

if 'paystack_secret' not in st.session_state:
    st.session_state.paystack_secret = ""

if 'dashboard_authenticated' not in st.session_state:
    st.session_state.dashboard_authenticated = False

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "pos"

# --- TOP HEADER BAR (Branding + Password + Admin) ---
head_c1, head_c2, head_c3 = st.columns([2, 1, 1])

with head_c1:
    if logo_b64:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 4px;">
                <img src="data:image/jpeg;base64,{logo_b64}" style="width: 32px; height: 32px; border-radius: 8px; object-fit: cover; border: 1px solid #f59e0b;">
                <span style="font-weight: 700; font-size: 14px; color: #f8fafc;">Trendy Pastries</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("🥐 **Trendy Pastries**", unsafe_allow_html=True)

with head_c2:
    if st.button("🔑 Password", key="head_pass"):
        st.session_state.active_tab = "dashboard"
        st.rerun()

with head_c3:
    if st.button("⚙️ Admin", key="head_admin"):
        st.session_state.active_tab = "admin"
        st.rerun()

st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

# ==========================================
# VIEW 1: POS TERMINAL
# ==========================================
if st.session_state.active_tab == "pos":
    
    # Search Bar
    search_query = st.text_input("🔍 Search pastries, cakes, breads...", "", key="search_prod")
    
    # Category Filter Pills
    cat_c1, cat_c2, cat_c3, cat_c4, cat_c5 = st.columns(5)
    if "selected_cat" not in st.session_state:
        st.session_state.selected_cat = "All Items"
        
    if cat_c1.button("All Items", key="cat_all"): st.session_state.selected_cat = "All Items"; st.rerun()
    if cat_c2.button("Pastries", key="cat_pas"): st.session_state.selected_cat = "Pastries"; st.rerun()
    if cat_c3.button("Cakes", key="cat_cak"): st.session_state.selected_cat = "Cakes"; st.rerun()
    if cat_c4.button("Breads", key="cat_brd"): st.session_state.selected_cat = "Breads"; st.rerun()
    if cat_c5.button("Drinks", key="cat_drk"): st.session_state.selected_cat = "Drinks"; st.rerun()

    st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

    filtered = st.session_state.products
    if st.session_state.selected_cat != "All Items":
        filtered = [p for p in filtered if p["category"] == st.session_state.selected_cat]
    if search_query:
        filtered = [p for p in filtered if search_query.lower() in p["name"].lower()]

    # Product Catalog Grid (2 columns)
    grid_cols = st.columns(2)
    for idx, prod in enumerate(filtered):
        with grid_cols[idx % 2]:
            with st.container(border=True):
                try:
                    st.image(prod['image'], use_container_width=True)
                except:
                    st.write("🥐")
                st.markdown(f"**{prod['name']}**")
                st.markdown(f"<span style='color: #f59e0b; font-weight: 800; font-size: 16px;'>GH₵ {prod['price']:.2f}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: #94a3b8; font-size: 11px;'>{prod['stock']} units left</span>", unsafe_allow_html=True)
                
                if st.button("Add 🛒", key=f"add_cart_{prod['id']}"):
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

    st.divider()

    # Floating/Bottom Cart Summary & Checkout
    total_cart_items = sum(item['qty'] for item in st.session_state.cart)
    if total_cart_items > 0:
        st.markdown(f"""
            <div style="background-color: #f59e0b; color: #0f172a; padding: 10px 16px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; font-weight: 800; margin-bottom: 15px;">
                <span>🛒 Cart ({total_cart_items} items)</span>
                <span>Active Order</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🛒 Current Order")
    
    if not st.session_state.cart:
        st.info("No items in cart")
    else:
        subtotal = 0.0
        for item in st.session_state.cart:
            item_total = item['price'] * item['qty']
            subtotal += item_total
            
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            cc1.markdown(f"**{item['name']}**")
            cc2.write(f"{item['qty']}x GH₵{item['price']:.2f}")
            if cc3.button("❌", key=f"rem_{item['id']}"):
                st.session_state.cart = [i for i in st.session_state.cart if i["id"] != item["id"]]
                st.rerun()

        st.divider()
        discount_pct = st.number_input("Discount (%)", min_value=0, max_value=100, value=0, key="disc_input")
        discounted_subtotal = subtotal * (1 - discount_pct / 100)
        tax = discounted_subtotal * 0.08
        total = discounted_subtotal + tax

        st.write(f"Subtotal: GH₵ {subtotal:.2f}")
        st.write(f"Tax (8%): GH₵ {tax:.2f}")
        st.markdown(f"### Total: GH₵ {total:.2f}")

        if st.button("Clear Cart", key="clear_cart_btn"):
            st.session_state.cart = []
            st.rerun()

        st.divider()
        st.markdown("#### Select Payment Channel")
        payment_method = st.radio(
            "Payment Method", 
            ["MTN MoMo", "Telecel Cash", "AT Money", "Bank Card"]
        )

        customer_email = st.text_input("Customer Email for Receipt", value="customer@trendypastries.com")

        if not st.session_state.paystack_secret:
            st.warning("⚠️ Please save your Paystack Secret Key in the **Admin** settings to process payments.")
        else:
            if st.button(f"Initiate {payment_method} Payment via Paystack 💳", key="paystack_init_btn"):
                channel_map = {
                    "MTN MoMo": ["mobile_money"],
                    "Telecel Cash": ["mobile_money"],
                    "AT Money": ["mobile_money"],
                    "Bank Card": ["card"]
                }
                
                url = "https://api.paystack.co/transaction/initialize"
                headers = {
                    "Authorization": f"Bearer {st.session_state.paystack_secret}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "email": customer_email,
                    "amount": int(total * 100),
                    "currency": "GHS",
                    "channels": channel_map.get(payment_method, ["card", "mobile_money"])
                }
                
                try:
                    response = requests.post(url, json=payload, headers=headers)
                    res_data = response.json()
                    if res_data.get("status"):
                        checkout_url = res_data["data"]["authorization_url"]
                        st.success(f"Paystack request generated successfully for {payment_method}!")
                        st.markdown(f"👉 **[Click Here to Pay GH₵ {total:.2f} via {payment_method}]({checkout_url})**", unsafe_allow_html=True)
                        
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
                    else:
                        st.error(f"Paystack Error: {res_data.get('message', 'Initialization failed')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# ==========================================
# VIEW 2: CEO FINANCIAL DASHBOARD & ANALYTICS (PIN PROTECTED)
# ==========================================
elif st.session_state.active_tab == "dashboard":
    st.markdown("## 📊 CEO Financial Dashboard")

    if not st.session_state.dashboard_authenticated:
        st.warning("🔒 Secure Area. Please enter your CEO PIN to unlock analytics.")
        pin_entered = st.text_input("Enter CEO PIN (Default: 1234)", type="password", key="dash_pin_box")
        if st.button("Unlock Dashboard", key="unlock_dash_btn"):
            if pin_entered == st.session_state.ceo_pin:
                st.session_state.dashboard_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    else:
        if st.button("Lock Dashboard", key="lock_dash_btn"):
            st.session_state.dashboard_authenticated = False
            st.rerun()

        sales = st.session_state.sales_history
        total_rev = sum(o["total"] for o in sales)
        total_orders = len(sales)
        avg_order = total_rev / total_orders if total_orders > 0 else 0

        k1, k2, k3 = st.columns(3)
        k1.metric("Revenue", f"GH₵ {total_rev:.2f}")
        k2.metric("Orders", total_orders)
        k3.metric("Avg", f"GH₵ {avg_order:.2f}")

        st.divider()
        st.markdown("#### Transaction Audit Trail")
        if sales:
            df_sales = pd.DataFrame([{
                "ID": o["id"],
                "Date": o["timestamp"],
                "Method": o["method"],
                "Total (GH₵)": f"{o['total']:.2f}"
            } for o in sales])
            st.dataframe(df_sales, use_container_width=True)
        else:
            st.info("No sales recorded yet.")

# ==========================================
# VIEW 3: CEO ADMIN & SETTINGS (PIN PROTECTED)
# ==========================================
elif st.session_state.active_tab == "admin":
    st.markdown("## ⚙️ CEO Management Settings")

    if not st.session_state.admin_authenticated:
        st.warning("🔒 Secure Area. Please enter your CEO PIN to unlock admin settings.")
        admin_pin_entered = st.text_input("Enter CEO PIN (Default: 1234)", type="password", key="admin_pin_box")
        if st.button("Unlock Admin Settings", key="unlock_admin_btn"):
            if admin_pin_entered == st.session_state.ceo_pin:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    else:
        if st.button("Lock Admin Settings", key="lock_admin_btn"):
            st.session_state.admin_authenticated = False
            st.rerun()

        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["💳 Paystack", "📦 Inventory", "🔑 PIN"])

        with admin_tab1:
            st.markdown("### Paystack Configuration")
            paystack_input = st.text_input("Paystack Secret Key", value=st.session_state.paystack_secret, type="password", key="pay_secret_box")
            if st.button("Save Paystack Key", key="save_paystack_key"):
                st.session_state.paystack_secret = paystack_input
                st.success("Paystack Secret Key saved successfully!")

        with admin_tab2:
            st.markdown("### Add New Product")
            with st.form("add_product_form"):
                p_name = st.text_input("Product Name")
                p_cat = st.selectbox("Category", ["Pastries", "Cakes", "Breads", "Drinks"])
                p_cost = st.number_input("Cost Price (GH₵)", min_value=0.0, value=5.0)
                p_price = st.number_input("Selling Price (GH₵)", min_value=0.0, value=15.0)
                p_stock = st.number_input("Stock Quantity", min_value=1, value=20)
                
                # DIRECT IMAGE FILE UPLOAD FROM PHONE
                uploaded_file = st.file_uploader("Upload Product Image from Phone 📸", type=["jpg", "jpeg", "png", "webp"])
                
                submitted = st.form_submit_button("Save Product")
                if submitted and p_name:
                    image_data_url = "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=300"
                    
                    if uploaded_file is not None:
                        bytes_data = uploaded_file.getvalue()
                        b64_img = base64.b64encode(bytes_data).decode()
                        mime_type = uploaded_file.type
                        image_data_url = f"data:{mime_type};base64,{b64_img}"
                        
                    new_item = {
                        "id": len(st.session_state.products) + 100,
                        "name": p_name,
                        "cost": p_cost,
                        "price": p_price,
                        "category": p_cat,
                        "stock": p_stock,
                        "image": image_data_url
                    }
                    st.session_state.products.append(new_item)
                    st.success(f"Added {p_name}!")
                    st.rerun()

            st.divider()
            st.markdown("### Existing Products (Delete)")
            for p in list(st.session_state.products):
                d_col1, d_col2, d_col3 = st.columns([3, 2, 1])
                d_col1.markdown(f"**{p['name']}**")
                d_col2.write(f"GH₵ {p['price']:.2f}")
                if d_col3.button("Delete 🗑️", key=f"del_prod_{p['id']}"):
                    st.session_state.products = [prod for prod in st.session_state.products if prod["id"] != p["id"]]
                    st.rerun()

        with admin_tab3:
            st.markdown("### Change CEO PIN")
            old_pin = st.text_input("Current PIN", type="password", key="old_pin_box")
            new_pin = st.text_input("New PIN (Min 4 digits)", type="password", key="new_pin_box")
            
            if st.button("Update PIN", key="save_pin_btn"):
                if old_pin == st.session_state.ceo_pin:
                    if len(new_pin) >= 4:
                        st.session_state.ceo_pin = new_pin
                        st.success("CEO PIN updated successfully!")
                    else:
                        st.error("PIN must be at least 4 digits.")
                else:
                    st.error("Current PIN is incorrect.")

st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# --- BOTTOM NAVIGATION BAR ---
bot_c1, bot_c2 = st.columns(2)
with bot_c1:
    if st.button("🛒 POS", key="nav_bot_pos"):
        st.session_state.active_tab = "pos"
        st.rerun()
with bot_c2:
    if st.button("📊 Dashboard", key="nav_bot_dash"):
        st.session_state.active_tab = "dashboard"
        st.rerun()
