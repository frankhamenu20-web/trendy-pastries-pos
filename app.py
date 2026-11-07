import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
import os
from PIL import Image
from supabase import create_client, Client
import bcrypt
from fpdf import FPDF

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

# --- CONNECT TO SUPABASE CLOUD DATABASE ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_supabase()

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

# --- LOAD PRODUCTS FROM SUPABASE ---
if 'products' not in st.session_state:
    if supabase:
        try:
            res = supabase.table("products").select("*").execute()
            st.session_state.products = res.data if res.data else []
        except Exception as e:
            st.warning(f"Database connection warning: {e}. Using local fallback cache.")
            st.session_state.products = []
    else:
        st.session_state.products = []

# --- LOAD SALES HISTORY FROM SUPABASE ---
if 'sales_history' not in st.session_state:
    if supabase:
        try:
            res = supabase.table("sales_history").select("*").order("id", desc=True).execute()
            st.session_state.sales_history = res.data if res.data else []
        except:
            st.session_state.sales_history = []
    else:
        st.session_state.sales_history = []

if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- SECURE BCRYPT HASH FOR CEO PIN (Forces default "1234" safely) ---
if 'ceo_pin_hash' not in st.session_state:
    st.session_state.ceo_pin_hash = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())

if 'paystack_secret' not in st.session_state:
    st.session_state.paystack_secret = ""

if 'dashboard_authenticated' not in st.session_state:
    st.session_state.dashboard_authenticated = False

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "pos"

# --- TOP HEADER BAR (Branding + Analytics + Admin) ---
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
    if st.button("📈 Analytics", key="head_analytics"):
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
    
    search_query = st.text_input("🔍 Search pastries, cakes, breads...", "", key="search_prod")
    
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

    if not filtered:
        st.info("No products found. Go to **Admin** settings to add your first product!")
    else:
        grid_cols = st.columns(2)
        for idx, prod in enumerate(filtered):
            with grid_cols[idx % 2]:
                with st.container(border=True):
                    try:
                        st.image(prod['image'], use_container_width=True)
                    except:
                        st.write("🥐")
                    st.markdown(f"**{prod['name']}**")
                    st.markdown(f"<span style='color: #f59e0b; font-weight: 800; font-size: 16px;'>GH₵ {float(prod['price']):.2f}</span>", unsafe_allow_html=True)
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
            item_total = float(item['price']) * item['qty']
            subtotal += item_total
            
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            cc1.markdown(f"**{item['name']}**")
            cc2.write(f"{item['qty']}x GH₵{float(item['price']):.2f}")
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
            ["Cash 💵", "MTN MoMo", "Telecel Cash", "AT Money", "Bank Card"]
        )

        customer_email = st.text_input("Customer Email for Receipt", value="customer@trendypastries.com")

        # CASH PAYMENT FLOW
        if payment_method == "Cash 💵":
            cash_received = st.number_input("Cash Received (GH₵)", min_value=float(total), value=float(total), step=1.0)
            change_due = cash_received - total
            st.markdown(f"**Change Due:** GH₵ {change_due:.2f}")
            
            if st.button("Complete Cash Sale 💵", key="complete_cash_btn"):
                for cart_item in st.session_state.cart:
                    new_stock = max(0, cart_item["stock"] - cart_item["qty"])
                    for p in st.session_state.products:
                        if p["id"] == cart_item["id"]:
                            p["stock"] = new_stock
                    if supabase:
                        supabase.table("products").update({"stock": new_stock}).eq("id", cart_item["id"]).execute()

                order_id_str = f"TPB-{1000 + len(st.session_state.sales_history) + 1}"
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                order_record = {
                    "order_id": order_id_str,
                    "total_amount": float(total),
                    "payment_method": "Cash",
                    "items": str(st.session_state.cart),
                    "created_at": timestamp_str
                }
                
                if supabase:
                    res = supabase.table("sales_history").insert(order_record).execute()
                    if res.data:
                        st.session_state.sales_history.insert(0, res.data[0])
                else:
                    st.session_state.sales_history.insert(0, order_record)

                st.session_state.cart = []
                st.success("Cash transaction completed successfully!")
                st.rerun()

        # PAYSTACK ONLINE PAYMENT FLOW
        else:
            if not st.session_state.paystack_secret:
                st.warning("⚠️ Please save your Paystack Secret Key in the **Admin** settings to process digital payments.")
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
                                new_stock = max(0, cart_item["stock"] - cart_item["qty"])
                                for p in st.session_state.products:
                                    if p["id"] == cart_item["id"]:
                                        p["stock"] = new_stock
                                if supabase:
                                    supabase.table("products").update({"stock": new_stock}).eq("id", cart_item["id"]).execute()

                            order_id_str = f"TPB-{1000 + len(st.session_state.sales_history) + 1}"
                            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            order_record = {
                                "order_id": order_id_str,
                                "total_amount": float(total),
                                "payment_method": payment_method,
                                "items": str(st.session_state.cart),
                                "created_at": timestamp_str
                            }
                            
                            if supabase:
                                res = supabase.table("sales_history").insert(order_record).execute()
                                if res.data:
                                    st.session_state.sales_history.insert(0, res.data[0])
                            else:
                                st.session_state.sales_history.insert(0, order_record)
                        else:
                            st.error(f"Paystack Error: {res_data.get('message', 'Initialization failed')}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

# ==========================================
# VIEW 2: CEO FINANCIAL ANALYTICS DASHBOARD
# ==========================================
elif st.session_state.active_tab == "dashboard":
    st.markdown("## 📈 CEO Analytics Dashboard")

    if not st.session_state.dashboard_authenticated:
        st.warning("🔒 Secure Area. Please enter your CEO PIN to unlock analytics.")
        pin_entered = st.text_input("Enter CEO PIN (Default: 1234)", type="password", key="dash_pin_box")
        if st.button("Unlock Dashboard", key="unlock_dash_btn"):
            if bcrypt.checkpw(pin_entered.encode('utf-8'), st.session_state.ceo_pin_hash):
                st.session_state.dashboard_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
    else:
        if st.button("Lock Dashboard", key="lock_dash_btn"):
            st.session_state.dashboard_authenticated = False
            st.rerun()

        sales = st.session_state.sales_history
        
        # Payment Method Sorting / Filtering
        st.markdown("#### Filter Transactions by Payment Method")
        payment_filter = st.selectbox(
            "Select Payment Method", 
            ["All Methods", "Cash", "MTN MoMo", "Telecel Cash", "AT Money", "Bank Card"]
        )
        
        filtered_sales = sales
        if payment_filter != "All Methods":
            filtered_sales = [o for o in sales if o.get("payment_method") == payment_filter]

        total_rev = sum(float(o.get("total_amount", 0)) for o in filtered_sales)
        total_orders = len(filtered_sales)
        avg_order = total_rev / total_orders if total_orders > 0 else 0

        k1, k2, k3 = st.columns(3)
        k1.metric("Revenue", f"GH₵ {total_rev:.2f}")
        k2.metric("Orders", total_orders)
        k3.metric("Avg", f"GH₵ {avg_order:.2f}")

        st.divider()
        st.markdown(f"#### Transaction Audit Trail ({payment_filter})")
        
        if filtered_sales:
            df_sales = pd.DataFrame([{
                "ID": o.get("order_id"),
                "Date & Time": o.get("created_at"),
                "Method": o.get("payment_method"),
                "Total (GH₵)": f"{float(o.get('total_amount', 0)):.2f}"
            } for o in filtered_sales])
            st.dataframe(df_sales, use_container_width=True)

            # --- GENERATE PDF REPORT FUNCTION ---
            def create_pdf(data_list, filter_name):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="Trendy Pastries and Bakery", ln=True, align="center")
                pdf.set_font("Arial", 'I', 12)
                pdf.cell(200, 10, txt=f"Financial History Report ({filter_name})", ln=True, align="center")
                pdf.ln(10)
                
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(30, 10, "Order ID", 1)
                pdf.cell(65, 10, "Date & Time", 1)
                pdf.cell(45, 10, "Method", 1)
                pdf.cell(50, 10, "Total (GHS)", 1)
                pdf.ln()
                
                pdf.set_font("Arial", '', 10)
                for item in data_list:
                    pdf.cell(30, 10, str(item.get("order_id")), 1)
                    pdf.cell(65, 10, str(item.get("created_at")), 1)
                    pdf.cell(45, 10, str(item.get("payment_method")), 1)
                    pdf.cell(50, 10, f"GHS {float(item.get('total_amount', 0)):.2f}", 1)
                    pdf.ln()
                
                return pdf.output()

            # Only render download button if there is data to prevent empty-byte errors
            pdf_data = create_pdf(filtered_sales, payment_filter)
            st.download_button(
                label="📥 Print / Download PDF Report",
                data=pdf_data,
                file_name=f"Trendy_Pastries_Financial_Report_{payment_filter.replace(' ', '_')}.pdf",
                mime="application/pdf",
                key="download_pdf_btn"
            )
        else:
            st.info(f"No transactions found for {payment_filter}.")

# ==========================================
# VIEW 3: CEO ADMIN & SETTINGS (BCRYPT PROTECTED)
# ==========================================
elif st.session_state.active_tab == "admin":
    st.markdown("## ⚙️ CEO Management Settings")

    if not st.session_state.admin_authenticated:
        st.warning("🔒 Secure Area. Please enter your CEO PIN to unlock admin settings.")
        admin_pin_entered = st.text_input("Enter CEO PIN (Default: 1234)", type="password", key="admin_pin_box")
        if st.button("Unlock Admin Settings", key="unlock_admin_btn"):
            if bcrypt.checkpw(admin_pin_entered.encode('utf-8'), st.session_state.ceo_pin_hash):
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
                p_price = st.number_input("Selling Price (GH₵)", min_value=0.0, value=15.0)
                p_stock = st.number_input("Stock Quantity", min_value=1, value=20)
                
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
                        "name": p_name,
                        "category": p_cat,
                        "price": float(p_price),
                        "stock": int(p_stock),
                        "image": image_data_url
                    }
                    
                    if supabase:
                        res = supabase.table("products").insert(new_item).execute()
                        if res.data:
                            st.session_state.products.append(res.data[0])
                    else:
                        st.session_state.products.append(new_item)
                        
                    st.success(f"Added {p_name} to cloud database!")
                    st.rerun()

            st.divider()
            st.markdown("### Existing Products (Delete)")
            if not st.session_state.products:
                st.info("No products in inventory yet.")
            else:
                for p in list(st.session_state.products):
                    d_col1, d_col2, d_col3 = st.columns([3, 2, 1])
                    d_col1.markdown(f"**{p['name']}**")
                    d_col2.write(f"GH₵ {float(p['price']):.2f}")
                    if d_col3.button("Delete 🗑️", key=f"del_prod_{p['id']}"):
                        if supabase:
                            supabase.table("products").delete().eq("id", p["id"]).execute()
                        st.session_state.products = [prod for prod in st.session_state.products if prod["id"] != p["id"]]
                        st.rerun()

        with admin_tab3:
            st.markdown("### Change CEO PIN")
            old_pin = st.text_input("Current PIN", type="password", key="old_pin_box")
            new_pin = st.text_input("New PIN (Min 4 digits)", type="password", key="new_pin_box")
            
            if st.button("Update PIN", key="save_pin_btn"):
                if bcrypt.checkpw(old_pin.encode('utf-8'), st.session_state.ceo_pin_hash):
                    if len(new_pin) >= 4:
                        salt = bcrypt.gensalt()
                        st.session_state.ceo_pin_hash = bcrypt.hashpw(new_pin.encode('utf-8'), salt)
                        st.success("CEO PIN updated and securely hashed successfully!")
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
    if st.button("📈 Analytics", key="nav_bot_dash"):
        st.session_state.active_tab = "dashboard"
        st.rerun()
