import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PhonePe GST Feasibility Dashboard", layout="wide")

# --- Title & Intro ---
st.title("📊 PhonePe GST & Finance Simplification Product Feasibility Dashboard")
st.markdown("This dashboard presents key insights, projections, and strategic recommendations for launching the GST & finance simplification product for small merchants, fully aligned with PhonePe's mission.")

# --- Vision Alignment ---
st.header("1️⃣ Vision Alignment")
st.markdown("**Mission:** Offer every Indian equal opportunity to accelerate progress by unlocking money flow & digital access.\n**Goal:** Empower small businesses with digital billing, GST compliance & finance tools.\n**Impact:** Boost merchant efficiency, expand digital payments, increase financial inclusion.")

# # --- Regulatory & GST Compliance ---
# st.header("2️⃣ Regulatory & GST Compliance")
# compliance_points = {
#     "Regulation": ["e-Invoicing mandatory ≥ ₹10L turnover (Apr 2025)", "GST registration threshold ₹40L/year"],
#     "Solution Features": ["Auto GST invoice (IRN compliant)", "e-Way bill creation", "Input Tax Credit tracking", "GST return filing"]
# }
# st.table(pd.DataFrame(compliance_points))

# --- Regulatory & GST Compliance ---
st.header("2️⃣ Regulatory & GST Compliance")
compliance_points = [
    {"Category": "Regulation", "Detail": "e-Invoicing mandatory ≥ ₹10L turnover (Apr 2025)"},
    {"Category": "Regulation", "Detail": "GST registration threshold ₹40L/year"},
    {"Category": "Solution Feature", "Detail": "Auto GST invoice (IRN compliant)"},
    {"Category": "Solution Feature", "Detail": "e-Way bill creation"},
    {"Category": "Solution Feature", "Detail": "Input Tax Credit tracking"},
    {"Category": "Solution Feature", "Detail": "GST return filing"}
]
st.table(pd.DataFrame(compliance_points))


# --- Technical Implementation ---
st.header("3️⃣ Technical Implementation")
technical_points = [
    "Build on PhonePe’s multi-tenant architecture & India-hosted infra",
    "Integrate GST APIs for e-invoicing",
    "SoftPOS for low-cost acceptance",
    "QR invoicing for simplicity",
    "Cloud backend for scalability"
]
st.write("\n".join([f"- {p}" for p in technical_points]))

# --- Strategic Partnerships ---
st.header("4️⃣ Strategic Partnerships")
partners = ["Zoho Books", "Vyapar", "Khatabook"]
st.markdown("**Target Partners:** " + ", ".join(partners))
st.markdown("**Benefits:** Faster time-to-market, access to merchant base, shared dev & marketing costs")

# --- Merchant Behavior & Adoption ---
st.header("5️⃣ Merchant Behavior & Adoption")
barriers = ["Fear of taxes", "Low demand perception", "Complexity"]
enablers = ["Education", "Incentives", "Simplified KYC", "Local language support"]
col1, col2 = st.columns(2)
col1.subheader("Barriers")
col1.write("\n".join([f"- {b}" for b in barriers]))
col2.subheader("Enablers")
col2.write("\n".join([f"- {e}" for e in enablers]))

# --- Monetization Model ---
st.header("6️⃣ Monetization Model")
monetization_df = pd.DataFrame({
    "Model": ["Subscription tiers", "Embedded lending", "Value-added services", "Transactional commissions"],
    "Details": [
        "Basic Free, Premium ₹199/mo, Pro ₹499/mo",
        "Loans from transaction data underwriting",
        "Ads, promotions, insurance",
        "Applicable gateway/MDR fees"
    ]
})
st.table(monetization_df)

# --- Cost-effective Execution ---
st.header("7️⃣ Cost-effective Execution")
st.write("- Reuse existing tech & merchant base\n- Leverage SoftPOS\n- Partner integration to reduce dev time\n- Agile MVP approach")

# --- Fast Time-to-Market ---
st.header("8️⃣ Fast Time-to-Market")
st.write("- Extend merchant app\n- Agile sprints\n- Pilot in select regions\n- Co-launch with partners")

# --- Merchant UX Simplicity ---
st.header("9️⃣ Merchant UX Simplicity")
ux_points = [
    "Minimal setup with instant QR & invoicing",
    "Auto payment reconciliation",
    "Simple dashboards & GST alerts",
    "Multi-language & voice support",
    "Hide complexity behind simple prompts"
]
st.write("\n".join([f"- {p}" for p in ux_points]))

# --- Financial Potential Visualization ---
st.header("🔟 Financial Potential (Year 3)")
financial_df = pd.DataFrame({
    "Source": ["Subscription", "Extra TPV Profit", "Lending Profit"],
    "Revenue (₹ Cr)": [1080, 270, 400]
})
fig = px.bar(financial_df, x="Source", y="Revenue (₹ Cr)", title="Year 3 Potential Revenue Breakdown", text="Revenue (₹ Cr)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Total Potential Annual Revenue: ₹1,750 Cr")

# --- Conclusion ---
st.header("1️⃣1️⃣ Conclusion")
st.write("- Aligned with PhonePe’s vision & roadmap\n- Supports small merchant compliance\n- Creates multiple revenue streams\n- Fast, low-cost execution with partnerships")

# --- Next Steps ---
st.header("1️⃣2️⃣ Next Steps")
next_steps = ["Internal feasibility with tech & compliance teams", "Negotiate with partners", "Build MVP & pilot", "Scale nationwide"]
st.write("\n".join([f"- {n}" for n in next_steps]))
