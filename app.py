import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Trendy Pastries and Bakery - Executive POS",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM MOBILE-FRIENDLY DARK STYLING ---
st.markdown("""
    <style>
    /* Global Background & Mobile Touch Fix */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Hide default Streamlit headers & footers for clean native app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Touch Friendly Buttons for Smartphones */
    .stButton>button {
        background-color: #f59e0b;
        color: #0f172a;
        font-weight: 800;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1rem;
        width: 100%;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    .stButton>button:hover, .stButton>button:active {
        background-color: #fbbf24;
        color: #0f172a;
    }

    /* Container Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
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

# --- TOP NAVIGATION HEADER ---
header_col1, header_col2 = st.columns([2, 5])
with header_col1:
    st.markdown("### 🥐 <span style='color: #f59e0b;'>Trendy Pastries</span>", unsafe_allow_html=True)
with header_col2:
    n1, n2, n3 = st.columns(3)
    if n1.button("🛒 POS", key="nav_pos"):
        st.session_state.active_tab = "pos"
        st.rerun()
    if n2.button("📊 Analytics", key="nav_dash"):
        st.session_state.active_tab = "dashboard"
        st.rerun()
    if n3.button("⚙️ Admin", key="nav_admin"):
        st.session_state.active_tab = "admin"
        st.rerun()

st.divider()

# ==========================================
# VIEW 1: POS TERMINAL
# ==========================================
if st.session_state.active_tab == "pos":
    col_catalog, col_cart = st.columns([3, 2])

    with col_catalog:
        search_query = st.text_input("🔍 Search products...", "", key="search_prod")
        
        c1, c2, c3, c4, c5 = st.columns(5)
        if "selected_cat" not in st.session_state:
            st.session_state.selected_cat = "All"
            
        if c1.button("All", key="cat_all"): st.session_state.selected_cat = "All"; st.rerun()
        if c2.button("Pastries", key="cat_pas"): st.session_state.selected_cat = "Pastries"; st.rerun()
        if c3.button("Cakes", key="cat_cak"): st.session_state.selected_cat = "Cakes"; st.rerun()
        if c4.button("Breads", key="cat_brd"): st.session_state.selected_cat = "Breads"; st.rerun()
        if c5.button("Drinks", key="cat_drk"): st.session_state.selected_cat = "Drinks"; st.rerun()

        filtered = st.session_state.products
        if st.session_state.selected_cat != "All":
            filtered = [p for p in filtered if p["category"] == st.session_state.selected_cat]
        if search_query:
            filtered = [p for p in filtered if search_query.lower() in p["name"].lower()]

        # Native Grid Rendering (Guarantees smartphone touch responsiveness)
        grid_cols = st.columns(2)
        for idx, prod in enumerate(filtered):
            with grid_cols[idx % 2]:
                with st.container(border=True):
                    try:
                        st.image(prod['image'], use_container_width=True)
                    except:
                        st.write("🥐")
                    st.markdown(f"**{prod['name']}**")
                    st.markdown(f"**GH₵ {prod['price']:.2f}** | Stock: {prod['stock']}")
                    if st.button(f"Add 🛒", key=f"add_cart_{prod['id']}"):
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

    with col_cart:
        st.markdown("#### 🛒 Current Order")
        
        if not st.session_state.cart:
            st.info("No items in cart.")
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
            payment_method = st.radio("Payment Method", ["MTN MoMo", "Telecel MoMo", "Paystack API", "Cash"])

            cash_tendered = 0.0
            if payment_method == "Cash":
                cash_tendered = st.number_input("Cash Tendered (GH₵)", min_value=0.0, value=total)
                change = cash_tendered - total
                st.write(f"**Change Due: GH₵ {max(0, change):.2f}**")

            if st.button("Complete Order 🚀", key="checkout_btn"):
                if payment_method == "Cash" and cash_tendered < total:
                    st.error("Cash tendered is less than total!")
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
                    st.success(f"Order #{order['id']} completed!")
                    st.balloons()

# ==========================================
# VIEW 2: CEO FINANCIAL DASHBOARD
# ==========================================
elif st.session_state.active_tab == "dashboard":
    st.markdown("## 📊 Financial Dashboard")

    if "dash_auth" not in st.session_state:
        st.session_state.dash_auth = False

    if not st.session_state.dash_auth:
        st.warning("🔒 Verification Required.")
        pin_entered = st.text_input("Enter CEO PIN", type="password", key="dash_pin_box")
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

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Revenue", f"GH₵ {total_rev:.2f}")
        k2.metric("Total Orders", total_orders)
        k3.metric("Avg Order", f"GH₵ {avg_order:.2f}")

        st.divider()
        if sales:
            df_sales = pd.DataFrame([{
                "Order ID": o["id"],
                "Date": o["timestamp"],
                "Method": o["method"],
                "Items": ", ".join([f"{i['qty']}x {i['name']}" for i in o["items"]]),
                "Total (GH₵)": f"{o['total']:.2f}"
            } for o in sales])
            st.dataframe(df_sales, use_container_width=True)
        else:
            st.info("No sales recorded yet.")

# ==========================================
# VIEW 3: CEO ADMIN & SETTINGS (Manage & Delete Products)
# ==========================================
elif st.session_state.active_tab == "admin":
    st.markdown("## ⚙️ CEO Management Settings")

    admin_tab1, admin_tab2 = st.tabs(["📦 Product Inventory & Deletion", "🔑 Security PIN"])

    with admin_tab1:
        st.markdown("### ➕ Add New Product")
        with st.form("add_product_form"):
            p_name = st.text_input("Product Name")
            p_cat = st.selectbox("Category", ["Pastries", "Cakes", "Breads", "Drinks"])
            p_cost = st.number_input("Cost Price (GH₵)", min_value=0.0, value=5.0)
            p_price = st.number_input("Selling Price (GH₵)", min_value=0.0, value=15.0)
            p_stock = st.number_input("Stock Quantity", min_value=1, value=20)
            p_img = st.text_input("Image URL", value="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=300")
            
            submitted = st.form_submit_button("Save Product")
            if submitted and p_name:
                new_item = {
                    "id": len(st.session_state.products) + 100,
                    "name": p_name,
                    "cost": p_cost,
                    "price": p_price,
                    "category": p_cat,
                    "stock": p_stock,
                    "image": p_img
                }
                st.session_state.products.append(new_item)
                st.success(f"Added {p_name} to menu!")
                st.rerun()

        st.divider()
        st.markdown("### 🗑️ Existing Products (Delete or Remove)")
        
        for p in list(st.session_state.products):
            d_col1, d_col2, d_col3 = st.columns([3, 2, 1])
            d_col1.markdown(f"**{p['name']}** ({p['category']})")
            d_col2.write(f"GH₵ {p['price']:.2f} | Stock: {p['stock']}")
            if d_col3.button("Delete 🗑️", key=f"del_prod_{p['id']}"):
                st.session_state.products = [prod for prod in st.session_state.products if prod["id"] != p["id"]]
                st.success(f"Removed {p['name']} from POS menu!")
                st.rerun()

    with admin_tab2:
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
