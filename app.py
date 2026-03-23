import streamlit as st
import requests
import random
import pandas as pd
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Enterprise Fraud System", page_icon="💳", layout="wide")

API_URL = "https://o32jgbufsl.execute-api.eu-north-1.amazonaws.com/prod/predict"

# ================= SESSION =================
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "history" not in st.session_state:
    st.session_state.history = []

if "bulk_result" not in st.session_state:
    st.session_state.bulk_result = None

if "report_data" not in st.session_state:
    st.session_state.report_data = []   # ✅ GLOBAL REPORT

# ================= UI =================
st.markdown("""
<style>
.stApp {background:#f4f7fe;}
.stButton>button {
    background: linear-gradient(45deg,#0066ff,#00c6ff);
    color:white;border-radius:10px;font-weight:bold;
}
.card {background:white;padding:20px;border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.1);}
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

# ================= SINGLE =================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Single Transaction")

    amount = st.number_input("Amount", value=500.0)
    time = st.number_input("Time", value=10000.0)
    txn_type = st.selectbox("Type", ["Online", "POS", "ATM", "International"])
    auto = st.checkbox("Auto features", True)

    if st.button("Analyze", use_container_width=True):

        features = [random.uniform(-3,3) for _ in range(28)] if auto else [0]*28
        data = [time] + features + [amount]

        try:
            res = requests.post(API_URL, json={"data": data})
            out = res.json()
            if "body" in out: out = out["body"]

            risk = min((amount/10000)*50 + (20 if txn_type=="International" else 10),100)

            if "Fraud" in str(out) or risk > 60:
                result = "Fraud"
                st.error("🚨 Fraud")
            else:
                result = "Normal"
                st.success("✅ Normal")

            st.progress(risk/100)
            st.write(f"Risk: {risk:.2f}%")

            record = {
                "Timestamp": datetime.now(),
                "Mode": "Single",
                "Amount": amount,
                "Type": txn_type,
                "Risk": risk,
                "Result": result
            }

            st.session_state.history.append(record)
            st.session_state.report_data.append(record)

        except Exception as e:
            st.error(e)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Analytics")

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.bar_chart(df["Result"].value_counts())
        st.line_chart(df["Risk"])
    else:
        st.info("No data yet")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= BULK =================
st.markdown("---")
st.subheader("Bulk Prediction")

file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.dataframe(df.head())

    if st.button("Run Bulk"):
        results = []

        for _, row in df.iterrows():
            data = row.tolist()
            if len(data)==31:
                data = data[:-1]

            try:
                res = requests.post(API_URL, json={"data":data})
                out = res.json()
                if "body" in out: out = out["body"]
                results.append(out)
            except:
                results.append("Error")

        df["Prediction"] = results
        st.session_state.bulk_result = df

        # Save bulk to report
        for _, row in df.iterrows():
            st.session_state.report_data.append({
                "Timestamp": datetime.now(),
                "Mode": "Bulk",
                "Amount": row.get("Amount", 0),
                "Type": "Bulk",
                "Risk": "N/A",
                "Result": row["Prediction"]
            })

# ================= SHOW BULK =================
if st.session_state.bulk_result is not None:
    st.success("Bulk Completed ✅")
    st.dataframe(st.session_state.bulk_result)

# ================= GLOBAL REPORT =================
st.markdown("---")
st.subheader("📥 Download Full Report")

if st.session_state.report_data:

    report_df = pd.DataFrame(st.session_state.report_data)
    st.dataframe(report_df)

    csv = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download All Transactions Report",
        data=csv,
        file_name="full_fraud_report.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("No report data yet")

# ================= FOOTER =================
st.markdown("---")
st.markdown("🚀 Production Ready Fraud Detection System")