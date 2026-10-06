import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# ---------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


# ---------------------------------------------------
# PROJECT IMPORTS
# ---------------------------------------------------

from predictor import (
    predict_waiting_time,
    get_congestion_level,
    get_recommendation
)

from database import create_database

from queue_manager import (
    add_customer,
    get_waiting_queue,
    get_all_customers,
    call_next_customer,
    complete_service,
    get_customer_by_token,
    get_customer_position,
    get_waiting_count
)

from analytics import (
    load_queue_data,
    get_basic_statistics,
    get_service_type_analysis,
    get_day_analysis,
    get_hourly_analysis,
    get_peak_hour,
    get_congestion_distribution
)


# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="Smart Queue Predictor",
    page_icon="🎟️",
    layout="wide"
)


# ---------------------------------------------------
# CREATE DATABASE
# ---------------------------------------------------

create_database()


# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 0px;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}

.metric-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f5f7fa;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown(
    '<div class="main-title">🎟️ Smart Queue & Waiting Time Predictor</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Predict waiting time, manage digital queues, and make smarter counter decisions.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------

st.sidebar.title("📋 Smart Queue")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "👨‍💼 Staff Dashboard",
        "👤 Customer View",
        "🤖 Waiting Time Predictor",
        "📊 Analytics"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "Smart Queue Management System\n\n"
    "Digital Tokens + ML Prediction + "
    "Queue Management + Analytics"
)


# ===================================================
# HOME
# ===================================================

if page == "🏠 Home":

    st.header("🏠 Smart Queue Management System")

    st.write(
        "A smart system that combines digital queue management "
        "with machine learning to predict customer waiting time."
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Customers Waiting",
            get_waiting_count()
        )

    with col2:
        customers = get_all_customers()
        st.metric(
            "Total Customers",
            len(customers)
        )

    with col3:
        st.metric(
            "System",
            "Online"
        )

    with col4:
        st.metric(
            "ML Model",
            "XGBoost"
        )

    st.divider()

    st.subheader("🔄 How the System Works")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("### 🎟️ 1")
        st.write("Customer joins the queue and receives a digital token.")

    with step2:
        st.markdown("### 👨‍💼 2")
        st.write("Staff manages the queue and calls the next customer.")

    with step3:
        st.markdown("### 🤖 3")
        st.write("Machine learning predicts the expected waiting time.")

    with step4:
        st.markdown("### 📱 4")
        st.write("Customer checks token position and estimated waiting time.")

    st.divider()

    st.subheader("✨ Main Features")

    feature1, feature2 = st.columns(2)

    with feature1:
        st.markdown("""
        **👨‍💼 Staff Dashboard**

        - Add customers
        - Generate digital tokens
        - View waiting queue
        - Call next customer
        - Complete service
        """)

    with feature2:
        st.markdown("""
        **👤 Customer View**

        - Enter token number
        - Check queue position
        - View current status
        - See estimated waiting time
        - Track queue progress
        """)


# ===================================================
# STAFF DASHBOARD
# ===================================================

elif page == "👨‍💼 Staff Dashboard":

    st.header("👨‍💼 Staff Dashboard")

    waiting_count = get_waiting_count()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "👥 Waiting",
            waiting_count
        )

    with col2:
        serving_customers = [
            c for c in get_all_customers()
            if c.status == "Serving"
        ]

        st.metric(
            "🔄 Currently Serving",
            len(serving_customers)
        )

    with col3:
        completed_customers = [
            c for c in get_all_customers()
            if c.status == "Completed"
        ]

        st.metric(
            "✅ Completed",
            len(completed_customers)
        )

    st.divider()

    # ------------------------------------------------
    # ADD CUSTOMER
    # ------------------------------------------------

    st.subheader("➕ Add Customer")

    add_col1, add_col2, add_col3 = st.columns(3)

    with add_col1:

        customer_name = st.text_input(
            "Customer Name"
        )

    with add_col2:

        service_type = st.selectbox(
            "Service Type",
            [
                "Bank",
                "Hospital",
                "Restaurant",
                "Government Office",
                "College Office",
                "Customer Service"
            ],
            key="staff_service_type"
        )

    with add_col3:

        add_button = st.button(
            "🎟️ Generate Token",
            use_container_width=True
        )

    if add_button:

        if customer_name.strip() == "":
            st.warning(
                "Please enter the customer name."
            )

        else:

            token = add_customer(
                customer_name.strip(),
                service_type
            )

            st.success(
                f"Customer added successfully! "
                f"Token Number: **{token}**"
            )

            st.rerun()

    st.divider()

    # ------------------------------------------------
    # CURRENT QUEUE
    # ------------------------------------------------

    st.subheader("📋 Current Waiting Queue")

    queue = get_waiting_queue()

    if queue:

        queue_data = []

        for index, customer in enumerate(
            queue,
            start=1
        ):

            queue_data.append({
                "Position": index,
                "Token": customer.token_number,
                "Customer": customer.customer_name,
                "Service": customer.service_type,
                "Status": customer.status,
                "Joined": customer.joined_at.strftime(
                    "%H:%M:%S"
                )
            })

        queue_df = pd.DataFrame(queue_data)

        st.dataframe(
            queue_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "There are currently no customers waiting."
        )

    st.divider()

    # ------------------------------------------------
    # CALL NEXT CUSTOMER
    # ------------------------------------------------

    st.subheader("📢 Call Next Customer")

    counter_col1, counter_col2 = st.columns(2)

    with counter_col1:

        counter_number = st.number_input(
            "Counter Number",
            min_value=1,
            max_value=20,
            value=1,
            step=1
        )

    with counter_col2:

        call_button = st.button(
            "📢 Call Next Customer",
            use_container_width=True
        )

    if call_button:

        customer = call_next_customer(
            counter_number
        )

        if customer:

            st.success(
                f"Token **{customer.token_number}** "
                f"({customer.customer_name}) "
                f"has been called to Counter "
                f"**{counter_number}**."
            )

        else:

            st.warning(
                "No customers are currently waiting."
            )

    st.divider()

    # ------------------------------------------------
    # COMPLETE SERVICE
    # ------------------------------------------------

    st.subheader("✅ Complete Customer Service")

    complete_col1, complete_col2 = st.columns(2)

    with complete_col1:

        token_to_complete = st.number_input(
            "Token Number",
            min_value=1,
            step=1,
            value=1,
            key="complete_token"
        )

    with complete_col2:

        complete_button = st.button(
            "✅ Complete Service",
            use_container_width=True
        )

    if complete_button:

        result = complete_service(
            token_to_complete
        )

        if result:

            st.success(
                f"Service completed for "
                f"Token **{token_to_complete}**."
            )

        else:

            st.error(
                "Customer with this token was not found."
            )

    st.divider()

    # ------------------------------------------------
    # ALL CUSTOMERS
    # ------------------------------------------------

    st.subheader("📊 Customer History")

    all_customers = get_all_customers()

    if all_customers:

        history_data = []

        for customer in all_customers:

            history_data.append({
                "Token": customer.token_number,
                "Customer": customer.customer_name,
                "Service": customer.service_type,
                "Status": customer.status,
                "Counter": customer.counter_number
                if customer.counter_number
                else "-",
                "Joined": customer.joined_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
            })

        history_df = pd.DataFrame(
            history_data
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )


# ===================================================
# CUSTOMER VIEW
# ===================================================

elif page == "👤 Customer View":

    st.header("👤 Customer Queue Status")

    st.write(
        "Enter your token number to check your current "
        "queue position and estimated waiting time."
    )

    token_number = st.number_input(
        "Enter Token Number",
        min_value=1,
        step=1,
        value=1
    )

    check_button = st.button(
        "🔍 Check My Queue",
        use_container_width=True
    )

    if check_button:

        customer = get_customer_by_token(
            token_number
        )

        if customer is None:

            st.error(
                "Token number not found."
            )

        else:

            st.success(
                f"Token **{customer.token_number}** "
                f"belongs to **{customer.customer_name}**."
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Token Number",
                    customer.token_number
                )

            with col2:
                st.metric(
                    "Service",
                    customer.service_type
                )

            with col3:
                st.metric(
                    "Status",
                    customer.status
                )

            st.divider()

            # ----------------------------------------
            # COMPLETED
            # ----------------------------------------

            if customer.status == "Completed":

                st.success(
                    "✅ Your service has been completed."
                )

            # ----------------------------------------
            # SERVING
            # ----------------------------------------

            elif customer.status == "Serving":

                st.warning(
                    f"🔔 Your token is currently being "
                    f"served at Counter "
                    f"**{customer.counter_number}**."
                )

            # ----------------------------------------
            # WAITING
            # ----------------------------------------

            else:

                position = get_customer_position(
                    token_number
                )

                st.subheader("📍 Queue Position")

                position_col1, position_col2 = st.columns(2)

                with position_col1:

                    st.metric(
                        "Your Position",
                        position
                    )

                with position_col2:

                    people_before = max(
                        position - 1,
                        0
                    )

                    st.metric(
                        "People Before You",
                        people_before
                    )

                # ------------------------------------
                # ESTIMATED WAIT
                # ------------------------------------

                try:

                    now = datetime.now()

                    waiting_time = predict_waiting_time(
                        service_type=customer.service_type,
                        day_of_week=now.strftime("%A"),
                        hour=now.hour,
                        people_waiting=get_waiting_count(),
                        active_counters=2,
                        avg_service_time=5.0,
                        priority_customers=0,
                        arrival_rate=30
                    )

                    level, icon = get_congestion_level(
                        waiting_time
                    )

                    st.metric(
                        "🤖 Estimated Waiting Time",
                        f"{waiting_time} minutes"
                    )

                    st.info(
                        f"Queue Status: {icon} **{level}**"
                    )

                except FileNotFoundError:

                    st.warning(
                        "ML model has not been trained yet. "
                        "Run `python src/train_model.py` first."
                    )

                st.divider()

                st.info(
                    "💡 Please stay near the service area "
                    "and monitor your token status."
                )


# ===================================================
# WAITING TIME PREDICTOR
# ===================================================

elif page == "🤖 Waiting Time Predictor":

    st.header("🤖 Waiting Time Predictor")

    st.write(
        "Use the trained machine learning model to predict "
        "customer waiting time."
    )

    st.divider()

    # ------------------------------------------------
    # INPUTS
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        service_type = st.selectbox(
            "Service Type",
            [
                "Bank",
                "Hospital",
                "Restaurant",
                "Government Office",
                "College Office",
                "Customer Service"
            ],
            key="predict_service"
        )

        people_waiting = st.number_input(
            "People Currently Waiting",
            min_value=0,
            max_value=500,
            value=20,
            step=1
        )

        active_counters = st.number_input(
            "Active Counters",
            min_value=1,
            max_value=20,
            value=2,
            step=1
        )

        avg_service_time = st.number_input(
            "Average Service Time (minutes)",
            min_value=1.0,
            max_value=60.0,
            value=5.0,
            step=0.5
        )

    with col2:

        priority_customers = st.number_input(
            "Priority Customers",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

        arrival_rate = st.slider(
            "Customer Arrival Rate (per hour)",
            min_value=1,
            max_value=200,
            value=30
        )

        day_of_week = st.selectbox(
            "Day of Week",
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ]
        )

        hour = st.slider(
            "Current Hour",
            min_value=0,
            max_value=23,
            value=datetime.now().hour
        )

    predict_button = st.button(
        "🔮 Predict Waiting Time",
        use_container_width=True
    )

    # ------------------------------------------------
    # PREDICTION
    # ------------------------------------------------

    if predict_button:

        try:

            waiting_time = predict_waiting_time(
                service_type=service_type,
                day_of_week=day_of_week,
                hour=hour,
                people_waiting=people_waiting,
                active_counters=active_counters,
                avg_service_time=avg_service_time,
                priority_customers=priority_customers,
                arrival_rate=arrival_rate
            )

            level, icon = get_congestion_level(
                waiting_time
            )

            recommendation = get_recommendation(
                waiting_time,
                active_counters
            )

            st.divider()

            st.subheader("🔮 Prediction Result")

            result_col1, result_col2 = st.columns(2)

            with result_col1:

                st.metric(
                    "Estimated Waiting Time",
                    f"{waiting_time} minutes"
                )

            with result_col2:

                st.metric(
                    "Queue Status",
                    f"{icon} {level}"
                )

            st.divider()

            st.subheader("💡 Smart Recommendation")

            if level == "LOW":
                st.success(
                    recommendation
                )

            elif level == "MODERATE":
                st.warning(
                    recommendation
                )

            else:
                st.error(
                    recommendation
                )

            # ----------------------------------------
            # WHAT-IF SIMULATION
            # ----------------------------------------

            st.subheader("🔄 What-If Simulator")

            st.write(
                "See how waiting time changes when "
                "additional counters are opened."
            )

            simulation_data = []

            for extra_counter in range(0, 4):

                new_counters = (
                    active_counters
                    + extra_counter
                )

                new_waiting_time = predict_waiting_time(
                    service_type=service_type,
                    day_of_week=day_of_week,
                    hour=hour,
                    people_waiting=people_waiting,
                    active_counters=new_counters,
                    avg_service_time=avg_service_time,
                    priority_customers=priority_customers,
                    arrival_rate=arrival_rate
                )

                simulation_data.append({

                    "Additional Counters":
                        extra_counter,

                    "Total Counters":
                        new_counters,

                    "Estimated Waiting Time (min)":
                        new_waiting_time
                })

            simulation_df = pd.DataFrame(
                simulation_data
            )

            st.dataframe(
                simulation_df,
                use_container_width=True,
                hide_index=True
            )

            # ----------------------------------------
            # INSIGHTS
            # ----------------------------------------

            st.subheader("📌 Queue Insights")

            insight1, insight2, insight3 = st.columns(3)

            with insight1:

                st.info(
                    f"👥 **{people_waiting}** people "
                    "are currently waiting."
                )

            with insight2:

                st.info(
                    f"🏢 **{active_counters}** counters "
                    "are currently active."
                )

            with insight3:

                st.info(
                    f"🚶 **{arrival_rate}** customers "
                    "are arriving per hour."
                )

        except FileNotFoundError:

            st.error(
                "❌ Trained ML model not found."
            )

            st.info(
                "Run this command in the terminal:\n\n"
                "`python src/train_model.py`"
            )


# ===================================================
# ANALYTICS
# ===================================================

elif page == "📊 Analytics":

    st.header("📊 Queue Analytics")

    try:

        df = load_queue_data()

        statistics = get_basic_statistics(df)

        # --------------------------------------------
        # KEY METRICS
        # --------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Records",
                statistics["total_records"]
            )

        with col2:

            st.metric(
                "Average Waiting Time",
                f'{statistics["average_waiting_time"]} min'
            )

        with col3:

            st.metric(
                "Maximum Waiting Time",
                f'{statistics["maximum_waiting_time"]} min'
            )

        with col4:

            st.metric(
                "Average Queue Length",
                statistics["average_queue_length"]
            )

        st.divider()

        # --------------------------------------------
        # SERVICE ANALYSIS
        # --------------------------------------------

        st.subheader("🏢 Service Type Analysis")

        service_analysis = get_service_type_analysis(
            df
        )

        st.dataframe(
            service_analysis,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            service_analysis.set_index(
                "service_type"
            )["average_waiting_time"]
        )

        # --------------------------------------------
        # DAY ANALYSIS
        # --------------------------------------------

        st.subheader("📅 Waiting Time by Day")

        day_analysis = get_day_analysis(df)

        st.line_chart(
            day_analysis.set_index(
                "day_of_week"
            )["average_waiting_time"]
        )

        # --------------------------------------------
        # HOURLY ANALYSIS
        # --------------------------------------------

        st.subheader("⏰ Waiting Time by Hour")

        hourly_analysis = get_hourly_analysis(df)

        st.line_chart(
            hourly_analysis.set_index(
                "hour"
            )["average_waiting_time"]
        )

        # --------------------------------------------
        # PEAK HOUR
        # --------------------------------------------

        peak_hour, peak_wait = get_peak_hour(
            df
        )

        st.warning(
            f"🔥 Peak hour: **{peak_hour}:00** "
            f"with average waiting time of "
            f"**{peak_wait} minutes**."
        )

        # --------------------------------------------
        # CONGESTION
        # --------------------------------------------

        st.subheader("🚦 Congestion Distribution")

        congestion = get_congestion_distribution(
            df
        )

        congestion.columns = [
            "Congestion Level",
            "Number of Records"
        ]

        st.dataframe(
            congestion,
            use_container_width=True,
            hide_index=True
        )

    except Exception as error:

        st.error(
            f"Unable to load analytics: {error}"
        )


# ===================================================
# FOOTER
# ===================================================

st.divider()

st.caption(
    "Smart Queue & Waiting Time Predictor | "
    "Machine Learning + Streamlit + SQLite + Analytics"
)