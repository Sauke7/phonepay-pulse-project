# ===================== IMPORTS =====================
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import requests
# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="PhonePe Transaction Dynamics",
    layout="wide"
)
# ===================== TITLE =====================
st.title("📈 PhonePe Pulse 📈")

# ===================== DATABASE CONNECTION =====================
@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+mysqlconnector://root:k.dybalasai@localhost/phonepay",
        pool_pre_ping=True
    )

engine = get_engine()

def load_data(query):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

# ===================== SIDEBAR NAVIGATION =====================
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Analysis"]
)

# ===================== HOME PAGE =====================
if page == "Home":
    st.markdown("🔴 India-wide Transaction & User Insights")
    st.markdown(
        "Hover over any state to view **Registered Users** and "
        "**Total Transaction Amount (₹ Crore)**."
    )

    geojson_url = (
        "https://gist.githubusercontent.com/jbrobst/"
        "56c13bbbf9d97d187fea01ca62ea5112/raw/"
        "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    )
    india_geojson = requests.get(geojson_url).json()

    query_map = """
    SELECT
        u.State,
        MAX(u.Registered_Users) AS registered_users,
        SUM(t.Transacion_amount) AS total_amount
    FROM Aggre_user u
    JOIN Aggre_Trans t
        ON u.State = t.State
       AND u.Year = t.Year
       AND u.Quater = t.Quater
    GROUP BY u.State;
    """

    df_map = load_data(query_map)
    df_map["amount_cr"] = df_map["total_amount"] / 1_00_00_000

    df_map["State"] = (
        df_map["State"]
        .str.replace("-", " ")
        .str.replace("&", "and")
        .str.title()
    )
     
    fig_map = px.choropleth(
        df_map,
        
        geojson=india_geojson,
        featureidkey="properties.ST_NM",
        locations="State",
        color="amount_cr",
        color_continuous_scale="Reds",
        hover_name="State",
        hover_data={
            "registered_users": True,
            "amount_cr": ":.2f"
        },
        labels={
            "amount_cr": "Transaction Amount (₹ Cr)",
            "registered_users": "Registered Users"
        }
    )

    fig_map.update_geos(fitbounds="locations", visible=False)
    
    fig_map.update_layout(
        title={
        "text": "State-wise Transaction Amount (₹ Cr)",
        "x": 0.5,          # center the title
        "xanchor": "center",
        "yanchor": "top"
    },
        height=950,
        margin=dict(l=0, r=0, t=30, b=0),
        title_x=0.5
        

    )

    st.plotly_chart(fig_map, use_container_width=True)


# ===================== ANALYSIS PAGE =====================
elif page == "Analysis":
    st.header("1️⃣ Decoding Transaction Dynamics on PhonePe")
    st.markdown("""
    PhonePe analyzes **state, district, and pin-code level transactions**
    to identify:
    
    - High-performing regions  
    - User engagement hotspots  
    - Areas for targeted marketing  
    
   
    """)

    # 1️⃣ STATE-WISE TRANSACTION PERFORMANCE
    st.header("🔴 State-wise Transaction Performance")

    query_state = """
    SELECT 
        State,
        SUM(Transacion_count) AS total_transactions,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_Trans
    GROUP BY State
    ORDER BY total_amount DESC;
    """

    df_state = load_data(query_state)

    fig_state = px.bar(
        df_state.head(15),
        x="State",
        y="total_amount",
        title="Top 15 States by Transaction Amount",
        labels={"total_amount": "Transaction Amount"}
    )

    st.plotly_chart(fig_state, use_container_width=True)

    # 2️⃣ QUARTERLY TRANSACTION TREND
    st.header("🔴 Quarterly Transaction Trend")

    query_quarter = """
    SELECT 
        Year,
        Quater,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_Trans
    GROUP BY Year, Quater
    ORDER BY Year, Quater;
    """

    df_quarter = load_data(query_quarter)
    df_quarter["Year-Quarter"] = df_quarter["Year"].astype(str) + " Q" + df_quarter["Quater"].astype(str)

    fig_quarter = px.line(
        df_quarter,
        x="Year-Quarter",
        y="total_amount",
        markers=True,
        title="Quarter-wise Transaction Growth"
    )

    st.plotly_chart(fig_quarter, use_container_width=True)

    # 3️⃣ TRANSACTION CATEGORY PERFORMANCE
    st.header("🔴 Transaction Category Performance")

    query_type = """
    SELECT 
        Transacion_type,
        SUM(Transacion_count) AS total_count,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_Trans
    GROUP BY Transacion_type
    ORDER BY total_amount DESC;
    """

    df_type = load_data(query_type)

    fig_type = px.pie(
        df_type,
        names="Transacion_type",
        values="total_amount",
        title="Transaction Amount Share by Category"
    )

    st.plotly_chart(fig_type, use_container_width=True)

    # 4️⃣ USER GROWTH VS TRANSACTIONS
    st.header("🔴 User Growth vs Transaction Growth")

    query_user_txn = """
    SELECT
        t.State,
        SUM(t.Transacion_amount) AS total_amount,
        MAX(u.Registered_Users) AS registered_users
    FROM Aggre_Trans t
    JOIN Aggre_user u
    ON t.State = u.State
    AND t.Year = u.Year
    AND t.Quater = u.Quater
    GROUP BY t.State
    ORDER BY total_amount DESC;
    """

    df_user_txn = load_data(query_user_txn)

    fig_user_txn = px.scatter(
        df_user_txn,
        x="registered_users",
        y="total_amount",
        size="total_amount",
        color="State",
        title="Registered Users vs Transaction Amount"
    )

    st.plotly_chart(fig_user_txn, use_container_width=True)

    # 5️⃣ DISTRICT-LEVEL ENGAGEMENT GAP
    st.header("🔴 District-level Engagement vs Transactions")

    query_district = """
    SELECT
        u.State,
        u.District,
        SUM(u.appOpens) AS total_app_opens,
        SUM(t.district_Transacion_amount) AS total_transaction_amount
    FROM map_user u
    JOIN map_trans t
    ON u.State = t.State
    AND u.District = t.district_name
    AND u.Year = t.Year
    AND u.Quater = t.Quater
    GROUP BY u.State, u.District
    ORDER BY total_app_opens DESC
    LIMIT 20;
    """

    df_district = load_data(query_district)

    fig_district = px.bar(
        df_district,
        x="District",
        y="total_app_opens",
        color="State",
        title="Top Districts by App Opens (High Growth Potential)"
    )


    # FINAL INSIGHTS
    st.header("📌 Key Insights")
    st.markdown("""
    - Few states dominate transaction value  
    - Clear quarterly growth and stagnation patterns  
    - Certain transaction categories outperform others  
    - User growth does not always mean transaction growth  
    - Districts with high app opens but low transactions are growth opportunities  
    """)

    ###
   #222
    ###
    st.header("2️⃣ Device Dominance and User Engagement Analysis")

    st.markdown("""
    - A small number of states contribute the majority of transaction value  
    - Transaction growth varies significantly across quarters  
    - Certain payment categories dominate overall volume  
    - User growth does not always translate into transaction growth  
    - Districts with high app opens but low transactions indicate conversion gaps  
    """)
    # # =====================================================
    # # 1️⃣ DEVICE BRAND DOMINANCE
    # # =====================================================
    st.header("🔴 Device Brand Dominance")

    query_brand = """
    SELECT
        Brand_Name,
        SUM(User_Count) AS total_users
    FROM Aggre_user
    GROUP BY Brand_Name
    ORDER BY total_users DESC;
    """

    df_brand = load_data(query_brand)

    fig_brand = px.bar(
        df_brand,
        x="Brand_Name",
        y="total_users",
        title="Total Registered Users by Device Brand",
        labels={"total_users": "Registered Users"}
    )

    st.plotly_chart(fig_brand, use_container_width=True)

    # =====================================================
    # 2️⃣ BRAND-WISE USER TREND OVER TIME
    # =====================================================
    st.header("🔴 Brand-wise User Trend Over Time")

    query_trend = """
    SELECT
        Year,
        Quater,
        Brand_Name,
        SUM(User_Count) AS users
    FROM Aggre_user
    GROUP BY Year, Quater, Brand_Name
    ORDER BY Year, Quater;
    """

    df_trend = load_data(query_trend)
    df_trend["Year-Quarter"] = df_trend["Year"].astype(str) + " Q" + df_trend["Quater"].astype(str)

    fig_trend = px.line(
        df_trend,
        x="Year-Quarter",
        y="users",
        color="Brand_Name",
        title="Quarter-wise Registered Users by Brand"
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    # =====================================================
    # 3️⃣ BRAND vs STATE DISTRIBUTION
    # =====================================================
    st.header("🔴 Device Brand Distribution Across States")

    query_state_brand = """
    SELECT
        State,
        Brand_Name,
        SUM(User_Count) AS users
    FROM Aggre_user
    GROUP BY State, Brand_Name
    ORDER BY users DESC;
    """

    df_state_brand = load_data(query_state_brand)

    fig_state_brand = px.bar(
        df_state_brand.head(20),
        x="State",
        y="users",
        color="Brand_Name",
        title="Top State–Brand Combinations"
    )

    st.plotly_chart(fig_state_brand, use_container_width=True)

    # =====================================================
    # 4️⃣ ENGAGEMENT GAP (CRITICAL)
    # =====================================================
    st.header("🔴 Engagement Gap: Registered Users vs App Opens")

    query_engagement = """
    SELECT
        a.Brand_Name,
        SUM(a.User_Count) AS registered_users,
        SUM(m.appOpens) AS app_opens,
        ROUND(SUM(m.appOpens) / SUM(a.User_Count), 2) AS opens_per_user
    FROM Aggre_user a
    JOIN map_user m
    ON a.State = m.State
    AND a.Year = m.Year
    AND a.Quater = m.Quater
    GROUP BY a.Brand_Name
    ORDER BY opens_per_user ASC;
    """

    df_engagement = load_data(query_engagement)

    fig_engagement = px.scatter(
        df_engagement,
        x="registered_users",
        y="app_opens",
        size="opens_per_user",
        color="Brand_Name",
        title="Engagement Gap by Device Brand",
        labels={
            "registered_users": "Registered Users",
            "app_opens": "App Opens"
        }
    )

    st.plotly_chart(fig_engagement, use_container_width=True)

    # =====================================================
    # 5️⃣ UNDERUTILIZED DEVICE BRANDS
    # =====================================================
    st.header("🔴 Underutilized Device Brands")

    fig_under = px.bar(
        df_engagement.sort_values("opens_per_user").head(10),
        x="Brand_Name",
        y="opens_per_user",
        title="Lowest Engagement per User (Priority Devices)",
        labels={"opens_per_user": "App Opens per User"}
    )

    st.plotly_chart(fig_under, use_container_width=True)
   
    # =====================================================
    # FINAL INSIGHTS
    # =====================================================
    st.header("📌 Key Insights")

    st.markdown("""
    - A few device brands dominate PhonePe registrations  
    - Several brands show **high registration but low engagement**  
    - Engagement varies significantly across regions  
    - Underutilized devices represent **optimization opportunities**  
    - Device-level insights enable **targeted UX & performance improvements**
    """)


    # ###
    # 333
    # ###
    st.header("3️⃣ Insurance Penetration & Growth Potential Analysis")

    st.markdown("""
    - A few device brands dominate PhonePe registrations  
    - Several brands show **high registration but low engagement**  
    - Engagement varies significantly across regions  
    - Underutilized devices represent **optimization opportunities**  
    - Device-level insights enable **targeted UX & performance improvements**
    """)

    # =====================================================
    # 1️⃣ STATE-WISE INSURANCE TRANSACTION PERFORMANCE
    # =====================================================
    st.header("🔴 State-wise Insurance Transaction Performance")

    query_state_ins = """
    SELECT
        State,
        SUM(Transacion_count) AS total_policies,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_insure
    GROUP BY State
    ORDER BY total_amount DESC;
    """

    df_state_ins = load_data(query_state_ins)
    df_state_ins["amount_cr"] = df_state_ins["total_amount"] / 1_00_00_000

    fig_state_ins = px.bar(
        df_state_ins,
        x="State",
        y="amount_cr",
        title="Insurance Transaction Value by State (₹ Crore)",
        labels={"amount_cr": "Insurance Amount (₹ Cr)"}
    )

    st.plotly_chart(fig_state_ins, use_container_width=True)

    # =====================================================
    # 2️⃣ INSURANCE GROWTH TREND (QUARTERLY)
    # =====================================================
    st.header("🔴 Insurance Growth Trend Over Time")

    query_growth = """
    SELECT
        Year,
        Quater,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_insure
    GROUP BY Year, Quater
    ORDER BY Year, Quater;
    """

    df_growth = load_data(query_growth)
    df_growth["Year-Quarter"] = df_growth["Year"].astype(str) + " Q" + df_growth["Quater"].astype(str)
    df_growth["amount_cr"] = df_growth["total_amount"] / 1_00_00_000

    fig_growth = px.line(
        df_growth,
        x="Year-Quarter",
        y="amount_cr",
        markers=True,
        title="Quarter-wise Insurance Growth (₹ Crore)",
        labels={"amount_cr": "Insurance Amount (₹ Cr)"}
    )

    st.plotly_chart(fig_growth, use_container_width=True)

    # =====================================================
    # 3️⃣ INSURANCE PENETRATION VS USER BASE
    # =====================================================
    st.header("🔴 Insurance Penetration vs User Base")

    query_penetration = """
    SELECT
        i.State,
        SUM(i.Transacion_count) AS insurance_policies,
        MAX(u.Registered_Users) AS registered_users,
        ROUND(SUM(i.Transacion_count) / MAX(u.Registered_Users), 4) AS penetration_ratio
    FROM Aggre_insure i
    JOIN Aggre_user u
    ON i.State = u.State
    AND i.Year = u.Year
    AND i.Quater = u.Quater
    GROUP BY i.State
    ORDER BY penetration_ratio ASC;
    """

    df_penetration = load_data(query_penetration)

    fig_penetration = px.scatter(
        df_penetration,
        x="registered_users",
        y="insurance_policies",
        size="penetration_ratio",
        color="State",
        title="Insurance Penetration vs User Base",
        labels={
            "registered_users": "Registered Users",
            "insurance_policies": "Insurance Policies"
        }
    )

    st.plotly_chart(fig_penetration, use_container_width=True)

    # =====================================================
    # 4️⃣ UNDERPENETRATED STATES (HIGH POTENTIAL)
    # =====================================================
    st.header("🔴 Underpenetrated States (Growth Opportunity)")

    fig_under = px.bar(
        df_penetration.head(10),
        x="State",
        y="penetration_ratio",
        title="Lowest Insurance Penetration States",
        labels={"penetration_ratio": "Policies per User"}
    )

    st.plotly_chart(fig_under, use_container_width=True)

    # =====================================================
    # 5️⃣ TOP STATES FOR INSURANCE REVENUE
    # =====================================================
    st.header("🔴 Top Revenue-Generating States")

    fig_top = px.bar(
        df_state_ins.head(10),
        x="State",
        y="amount_cr",
        title="Top States by Insurance Revenue (₹ Crore)",
        labels={"amount_cr": "Insurance Amount (₹ Cr)"}
    )

    st.plotly_chart(fig_top, use_container_width=True)


    # =====================================================
    # FINAL INSIGHTS
    # =====================================================
    st.header("📌 Key Insights")

    st.markdown("""
    - Insurance adoption is **uneven across states**
    - A few states dominate insurance transaction value
    - Several states have **large user bases but low insurance penetration**
    - These states present **high growth potential**
    - Insights can guide **marketing campaigns & insurer partnerships**
    """)

    # ###
    # 444
    # ###
    st.header("4️⃣ Transaction Analysis for Market Expansion")
    st.markdown("""
    PhonePe operates in a competitive digital payments market.
    This analysis focuses on:
    
    - State-wise transaction volume & value  
    - Growth trends across quarters  
    - High-performing vs underperforming states  
    - Identifying regions for **market expansion**
    
    """)
    # =====================================================
    # 1️⃣ STATE-WISE TRANSACTION PERFORMANCE
    # =====================================================
    st.header("🔴 State-wise Transaction Performance")

    query_state = """
    SELECT
        State,
        SUM(Transacion_count) AS total_transactions,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_Trans
    GROUP BY State
    ORDER BY total_amount DESC;
    """

    df_state = load_data(query_state)
    df_state["amount_cr"] = df_state["total_amount"] / 1_00_00_000

    fig_state = px.bar(
        df_state,
        x="State",
        y="amount_cr",
        title="State-wise Transaction Value (₹ Crore)",
        labels={"amount_cr": "Transaction Amount (₹ Cr)"}
    )

    st.plotly_chart(fig_state, use_container_width=True)

    # =====================================================
    # 2️⃣ QUARTERLY TRANSACTION GROWTH
    # =====================================================
    st.header("🔴 Quarterly Transaction Growth")

    query_quarter = """
    SELECT
        Year,
        Quater,
        SUM(Transacion_amount) AS total_amount
    FROM Aggre_Trans
    GROUP BY Year, Quater
    ORDER BY Year, Quater;
    """

    df_quarter = load_data(query_quarter)
    df_quarter["Year-Quarter"] = df_quarter["Year"].astype(str) + " Q" + df_quarter["Quater"].astype(str)
    df_quarter["amount_cr"] = df_quarter["total_amount"] / 1_00_00_000

    fig_quarter = px.line(
        df_quarter,
        x="Year-Quarter",
        y="amount_cr",
        markers=True,
        title="Quarter-wise Transaction Growth (₹ Crore)",
        labels={"amount_cr": "Transaction Amount (₹ Cr)"}
    )

    st.plotly_chart(fig_quarter, use_container_width=True)

    # =====================================================
    # 3️⃣ HIGH GROWTH STATES (EXPANSION LEADERS)
    # =====================================================
    st.header("🔴 High-Growth States (Expansion Leaders)")

    fig_top = px.bar(
        df_state.head(10),
        x="State",
        y="amount_cr",
        title="Top 10 States by Transaction Value (₹ Crore)"
    )

    st.plotly_chart(fig_top, use_container_width=True)

    # =====================================================
    # 4️⃣ UNDERPERFORMING STATES (EXPANSION OPPORTUNITIES)
    # =====================================================
    st.header("🔴 Underperforming States (Growth Opportunity)")

    fig_low = px.bar(
        df_state.tail(10),
        x="State",
        y="amount_cr",
        title="Lowest Transaction Value States (₹ Crore)"
    )

    st.plotly_chart(fig_low, use_container_width=True)

    # =====================================================
    # 5️⃣ TRANSACTION COUNT VS VALUE
    # =====================================================
    st.header("🔴 Transaction Count vs Value")

    fig_scatter = px.scatter(
        df_state,
        x="total_transactions",
        y="amount_cr",
        size="amount_cr",
        color="State",
        title="Transaction Volume vs Transaction Value",
        labels={
            "total_transactions": "Total Transactions",
            "amount_cr": "Transaction Amount (₹ Cr)"
        }
    )

    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # =====================================================
    # FINAL INSIGHTS
    # =====================================================
    st.header("📌 Key Insights")

    st.markdown("""
    - A small set of states dominate transaction value  
    - Several states show consistent growth quarter-over-quarter  
    - Some states have low transaction penetration but high potential  
    - Transaction count and value gaps indicate **market maturity levels**  
    - Underperforming states are prime targets for expansion strategies
    """)

    # ###
    # 555
    # ###
    st.header("5️⃣ User Engagement and Growth Strategy")
    st.markdown("""
    PhonePe aims to strengthen its market position by analyzing **user engagement**.
    
    This analysis focuses on:
    - Registered users across states  
    - App opens as a measure of engagement  
    - State and district-level engagement patterns  
    - Identifying regions with high growth potential 
    
    """)
     # =====================================================
    # 1️⃣ STATE-WISE REGISTERED USERS
    # =====================================================
    st.header("🔴 State-wise Registered Users")

    query_users_state = """
    SELECT
        State,
        MAX(Registered_Users) AS registered_users
    FROM Aggre_user
    GROUP BY State
    ORDER BY registered_users DESC;
    """

    df_users_state = load_data(query_users_state)

    fig_users_state = px.bar(
        df_users_state.head(15),
        x="State",
        y="registered_users",
        title="Top States by Registered Users",
        labels={"registered_users": "Registered Users"}
    )

    st.plotly_chart(fig_users_state, use_container_width=True)

    # =====================================================
    # 2️⃣ STATE-WISE APP OPENS (ENGAGEMENT)
    # =====================================================
    st.header("🔴 State-wise App Opens (User Engagement)")

    query_app_opens_state = """
    SELECT
        State,
        SUM(appOpens) AS total_app_opens
    FROM map_user
    GROUP BY State
    ORDER BY total_app_opens DESC;
    """

    df_app_state = load_data(query_app_opens_state)

    fig_app_state = px.bar(
        df_app_state.head(15),
        x="State",
        y="total_app_opens",
        title="Top States by App Opens",
        labels={"total_app_opens": "App Opens"}
    )

    st.plotly_chart(fig_app_state, use_container_width=True)

    # =====================================================
    # 3️⃣ ENGAGEMENT RATIO (APP OPENS PER USER)
    # =====================================================
    st.header("🔴 Engagement Ratio (App Opens per User)")

    query_engagement = """
    SELECT
        u.State,
        MAX(u.Registered_Users) AS registered_users,
        SUM(m.appOpens) AS app_opens,
        ROUND(SUM(m.appOpens) / MAX(u.Registered_Users), 2) AS opens_per_user
    FROM Aggre_user u
    JOIN map_user m
    ON u.State = m.State
    AND u.Year = m.Year
    AND u.Quater = m.Quater
    GROUP BY u.State
    ORDER BY opens_per_user DESC;
    """

    df_engagement = load_data(query_engagement)

    fig_engagement = px.scatter(
        df_engagement,
        x="registered_users",
        y="app_opens",
        size="opens_per_user",
        color="State",
        title="Registered Users vs App Opens",
        labels={
            "registered_users": "Registered Users",
            "app_opens": "App Opens"
        }
    )

    st.plotly_chart(fig_engagement, use_container_width=True)

    # =====================================================
    # 4️⃣ DISTRICT-LEVEL USER ENGAGEMENT
    # =====================================================
    st.header("🔴 District-level User Engagement")

    query_district = """
    SELECT
        State,
        District,
        SUM(appOpens) AS total_app_opens,
        SUM(district_registeredUsers) AS district_users
    FROM map_user
    GROUP BY State, District
    ORDER BY total_app_opens DESC
    LIMIT 20;
    """

    df_district = load_data(query_district)

    fig_district = px.bar(
        df_district,
        x="District",
        y="total_app_opens",
        color="State",
        title="Top Districts by App Opens",
        labels={"total_app_opens": "App Opens"}
    )

    st.plotly_chart(fig_district, use_container_width=True)

    # =====================================================
    # 5️⃣ LOW ENGAGEMENT – HIGH USER STATES (GROWTH TARGETS)
    # =====================================================
    st.header("🔴 High Users but Low Engagement (Growth Targets)")

    fig_low_engagement = px.bar(
        df_engagement.sort_values("opens_per_user").head(10),
        x="State",
        y="opens_per_user",
        title="Lowest Engagement Ratio States",
        labels={"opens_per_user": "App Opens per User"}
    )

    st.plotly_chart(fig_low_engagement, use_container_width=True)
    
    # =====================================================
    # FINAL INSIGHTS
    # =====================================================
    st.header("📌 Key Insights")

    st.markdown("""
    - A few states dominate total registered users  
    - App opens vary significantly across regions  
    - Some states show **high registrations but low engagement**  
    - District-level analysis highlights localized growth opportunities  
    - These insights support **targeted user engagement strategies**
    """)

    