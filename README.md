# 📍 PhonePe Transaction Insights Dashboard

[![Streamlit App](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen?logo=streamlit)](https://janarthanan-369-phonepe-dashboard.streamlit.app/)

An interactive data analytics dashboard built with **Streamlit** to visualize and explore PhonePe transaction insights across India.  
It provides rich map-based visualizations, scenario-driven analysis, and filtering options for deep financial data exploration.

---

## 🚀 Live Demo
🔗 **[Open the Dashboard](https://janarthanan-369-phonepe-dashboard.streamlit.app/)**

---

## 📊 Features
- **🗺️ India Transaction Heatmap** — Visualizes district and state-level transaction patterns.
- **📈 Custom Analysis** — User-driven SQL queries and charts for personalized insights.
- **📊 Scenario-based Insights** — Predefined business scenarios showcasing UPI payment trends.
- **🔎 Filter Controls** — Multi-select filters by **State**, **Year**, and **Quarter**.
- **💾 Database Integration** — Powered by PostgreSQL with **Neon Cloud** hosting and local fallback.
- **⚡ Cloud-Optimized** — Fully deployed on Streamlit Cloud for instant access.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit, PyDeck, Plotly
- **Backend**: Python, Pandas
- **Database**: PostgreSQL (Neon Cloud + Local Fallback)
- **Other Tools**: SQLAlchemy, psycopg2

---

## 📂 Project Structure

📁 PhonePe-Dashboard
├── main.py # Main dashboard entry point
├── pages/ # Streamlit multi-page scripts
├── utils/db_connection.py # Database connection & query helpers
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## ⚙️ Setup & Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Janarthanan-369/PhonePe-Dashboard.git
   cd PhonePe-Dashboard

2. **Create a Virtual Environment**  

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. **Install Dependencies**

pip install -r requirements.txt

4. **Run the App**

streamlit run main.py

📬 Contact
Email: janarthanan3609@gmail.com
LinkedIn: linkedin.com/in/janarthanan-t-4b239523b


