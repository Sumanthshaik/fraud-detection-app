import streamlit as st
import pandas as pd
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Enterprise Fraud System", page_icon="💳", layout="wide")

# ================= SESSION =================
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "history" not in st.session_state:
    st.session_state.history = []

if "accounts" not in st.session_state:
    st.session_state.accounts = {}

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {background:#eef2f7;}

.card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 6px 20px rgba(0,0,0,0.1);
}

.result-box {
    padding:25px;
    border-radius:15px;
    text-align:center;
    font-size:22px;
    font-weight:bold;
}

.fraud {background:#ff4d4d;color:white;}
.safe {background:#28a745;color:white;}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
def login():
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in st.session_state.users and st.session_state.users[u] == p:
            st.session_state.logged_in = True
        else:
            st.error("Invalid ❌")

    if st.button("Sign Up"):
        st.session_state.page = "signup"

def signup():
    st.title("📝 Sign Up")
    u = st.text_input("New Username")
    p = st.text_input("New Password", type="password")

    if st.button("Create"):
        st.session_state.users[u] = p
        st.success("Created ✅")

    if st.button("Back"):
        st.session_state.page = "login"

# ================= AUTH =================
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login()
    else:
        signup()
    st.stop()

# ================= HEADER =================
st.title("💳 Enterprise Fraud Detection System")
st.button("🚪 Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

st.markdown("---")

# ================= INPUT =================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💰 Transaction Details")

    amount = st.number_input("Amount", value=500.0)
    time = st.number_input("Time (seconds)", value=10000.0)  # ✅ ADDED BACK
    txn_type = st.selectbox("Type", ["Online","POS","ATM","International"])
    account_no = st.text_input("Account Number (10-12 digits)")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🌐 Risk Factors")

    location = st.selectbox("Location", ["Local","Different City","Different Country"])
    device = st.selectbox("Device", ["Mobile","Laptop"])
    ip_risk = st.selectbox("IP Risk", ["Low","Medium","High"])

    txn_freq = st.number_input("Transactions (24 hrs)", value=2)
    failed_logins = st.number_input("Failed Logins", value=0)

    new_payee = st.checkbox("New Payee")
    previous_fraud = st.checkbox("Previous Fraud")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= RESET =================
if st.button("🔄 Reset Accounts"):
    st.session_state.accounts = {}
    st.success("Accounts Reset")

# ================= VALIDATION =================
if account_no and (not account_no.isdigit() or not (10 <= len(account_no) <= 12)):
    st.error("❌ Invalid Account Number")
    st.stop()

# ================= ANALYSIS =================
if st.button("🚀 Analyze Transaction", use_container_width=True):

    today = datetime.now()

    acc = st.session_state.accounts.get(account_no, {
        "last_used": today,
        "txn_count": 0,
        "fraud_count": 0,
        "avg_amount": amount
    })

    risk = 0
    breakdown = {}

    # ================= LOGIC =================
    if amount > 10000:
        risk += 20
        breakdown["High Amount"] = 20

    if txn_type == "International":
        risk += 20
        breakdown["International"] = 20

    if location == "Different Country":
        risk += 20
        breakdown["Location Risk"] = 20

    if ip_risk == "High":
        risk += 15
        breakdown["High IP"] = 15
    elif ip_risk == "Medium":
        risk += 8
        breakdown["Medium IP"] = 8

    if txn_freq > 5:
        risk += 10
        breakdown["High Frequency"] = 10

    if failed_logins > 3:
        risk += 15
        breakdown["Failed Logins"] = 15

    if new_payee:
        risk += 10
        breakdown["New Payee"] = 10

    if previous_fraud:
        risk += 25
        breakdown["Previous Fraud"] = 25

    # Account behavior
    if acc["fraud_count"] > 0:
        risk += 30
        breakdown["Account Fraud History"] = 30

    if acc["txn_count"] > 5:
        risk += 15
        breakdown["Too Many Transactions"] = 15

    if amount > acc["avg_amount"] * 3:
        risk += 25
        breakdown["Unusual Amount"] = 25

    # OPTIONAL: time-based risk
    if time < 1000:
        risk += 10
        breakdown["Unusual Time"] = 10

    risk = min(risk, 100)

    # ================= RESULT =================
    if risk >= 50:
        st.markdown('<div class="result-box fraud">🚨 FRAUD DETECTED</div>', unsafe_allow_html=True)
        result = "Fraud"
    else:
        st.markdown('<div class="result-box safe">✅ SAFE TRANSACTION</div>', unsafe_allow_html=True)
        result = "Not Fraud"

    # ================= RISK METER =================
    st.markdown("### 🎯 Risk Meter")
    st.progress(risk/100)
    st.write(f"Risk Score: {risk}%")

    # ================= BREAKDOWN =================
    st.markdown("### 🔍 Risk Breakdown")

    if breakdown:
        for k,v in breakdown.items():
            st.write(f"{k} → +{v}")
    else:
        st.write("No risk factors")

    # ================= CHART =================
    if breakdown:
        df = pd.DataFrame({
            "Factor": breakdown.keys(),
            "Value": breakdown.values()
        }).set_index("Factor")

        st.markdown("### 📊 Risk Contribution")
        st.bar_chart(df)

    # ================= UPDATE =================
    acc["last_used"] = today
    acc["txn_count"] += 1
    acc["avg_amount"] = (acc["avg_amount"] + amount)/2

    if result == "Fraud":
        acc["fraud_count"] += 1

    st.session_state.accounts[account_no] = acc

    # ================= SAVE =================
    st.session_state.history.append({
        "Time": today,
        "Account": account_no,
        "Amount": amount,
        "Input Time": time,
        "Risk": risk,
        "Result": result
    })

# ================= HISTORY =================
st.markdown("---")
st.subheader("📊 Transaction History")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
    st.bar_chart(df["Result"].value_counts())
else:
    st.info("No transactions yet")
