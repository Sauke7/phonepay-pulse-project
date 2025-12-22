# phonepay-pulse-project
# 📊 PhonePe Pulse – Business Analytics Dashboard

## 📌 Project Overview
PhonePe Pulse Analytics is a data-driven dashboard built using Python and Streamlit
to analyze digital payment trends across India. The project provides insights into
transactions, user engagement, device dominance, insurance growth, and market expansion
using PhonePe Pulse data.

---

## 🎯 Objectives
- Analyze transaction behavior across states and time periods
- Identify device usage trends and underutilized devices
- Study insurance penetration and growth potential
- Understand user engagement patterns using app opens
- Visualize insights using interactive charts and maps

---

## 🛠️ Technologies Used
- **Python**
- **Streamlit** – Dashboard framework
- **MySQL** – Database
- **SQLAlchemy** – Database connectivity
- **Pandas** – Data processing
- **Plotly** – Interactive visualizations

---

## 📂 Project Structure
phonepayproject/

│

├── app.py # Main Streamlit application

├── aggre_trans.py # Aggregated transaction ETL

├── aggre_user.py # Aggregated user & device ETL

├── aggre_insure.py # Insurance data ETL

├──  map_trans.py # District-level transaction data

├── map_insure.py  # District-level insurance penetration data

├── map_user.py  # District-level user engagement (app opens, users)

├── top_user.py # Top users analysis

├── top_trans.py # Top transactions analysis

├── top_insure.py # Top insurance-performing states/districts
