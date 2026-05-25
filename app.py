import json
import os
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from rag.vector_store import create_vector_store
from main import run_download_pipeline
from processing.read_data import load_and_clean_data
 
# =========================================
# PAGE SETTINGS
# =========================================
 
st.set_page_config(
    page_title="MMPL AI Engineering Assistant",
    page_icon="⚙️",
    layout="wide"
)
 
# =========================================
# SESSION STATE INIT
# =========================================
 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vector_data" not in st.session_state:
    st.session_state.vector_data = None

# =========================================
# AUTO LOAD LAST REPORT ON STARTUP
# =========================================

CONFIG_FILE = "last_report.json"

if "latest_report" not in st.session_state:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                performance_path = config.get("performance_path")
                mttr_path = config.get("mttr_path")
                if performance_path and os.path.exists(performance_path):
                    st.session_state.latest_report = performance_path
                    st.session_state.mttr_report = mttr_path
        except:
            pass
 
# =========================================
# CUSTOM UI STYLING
# =========================================

st.markdown(
    """
    <style>

    /* ── BACKGROUND WITH MMPL LOGO ── */
    .stApp {
        background-color: #0a0f1e;
        background-image: url("app/static/MMPL_LOGO.png");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 55%;
        background-attachment: fixed;
        color: white;
    }

    /* BLUR OVERLAY OVER LOGO */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(10, 15, 30, 0.82);
        backdrop-filter: blur(3px);
        z-index: 0;
    }

    /* KEEP CONTENT ABOVE OVERLAY */
    .stApp > * {
        position: relative;
        z-index: 1;
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.90);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(220, 30, 30, 0.25);
    }

    /* ── BUTTONS ── */
    .stButton button {
        background: linear-gradient(135deg, #c0110a, #8b0000);
        color: white;
        border-radius: 14px;
        border: none;
        font-weight: 600;
        height: 48px;
        transition: 0.3s;
        letter-spacing: 0.5px;
    }

    .stButton button:hover {
        transform: scale(1.02);
        background: linear-gradient(135deg, #e01010, #a00000);
        box-shadow: 0 4px 20px rgba(200, 0, 0, 0.4);
    }

    /* ── INPUT BOX ── */
    .stTextInput input {
        background-color: rgba(255,255,255,0.06);
        color: white;
        border-radius: 14px;
        border: 1px solid rgba(220, 30, 30, 0.30);
        padding: 12px;
    }

    /* ── METRIC CARDS ── */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(220, 30, 30, 0.20);
        border-radius: 14px;
        padding: 16px;
        backdrop-filter: blur(8px);
    }

    /* ── RECORD CARDS ── */
    .record-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(220, 30, 30, 0.20);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(6px);
    }

    /* ── EXPANDER ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(220, 30, 30, 0.20) !important;
    }

    /* ── HEADINGS COLOR ── */
    h1, h2, h3 {
        color: white !important;
    }

    /* ── DIVIDER COLOR ── */
    hr {
        border-color: rgba(220, 30, 30, 0.25) !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# LOGO IN HEADER
# =========================================

col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("assets/MMPL_LOGO.png", width=80)

with col_title:
    st.title("⚙️ MMPL AI Engineering Assistant")
    st.caption("Maheshwari Mining Pvt Ltd — AI-powered industrial maintenance and operations assistant")
 
# =========================================
# FETCH BUTTON
# =========================================
 
if st.button("📥 Fetch Latest TappetBox Report"):
    with st.spinner("Connecting to TappetBox and downloading latest reports..."):
        performance_file, mttr_file = run_download_pipeline()
    if performance_file:
        st.success("Latest reports downloaded successfully!")
        st.session_state.latest_report = performance_file
        st.session_state.mttr_report = mttr_file
        st.session_state.vector_data = None

        # Save to config file
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "performance_path": performance_file,
                "mttr_path": mttr_file
            }, f)

        st.rerun()
    else:
        st.error("Failed to download reports. Please try again.")
 
st.markdown("Upload reports and ask AI questions about your data.")
st.markdown("---")
 
# =========================================
# SIDEBAR
# =========================================
 
with st.sidebar:
    st.header("📂 Report Source")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
 
    if uploaded_file:
        with open("temp_report.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.latest_report = "temp_report.csv"
        st.session_state.mttr_report = "downloads/mttr_mtbf_report.xlsx"
        st.session_state.vector_data = None
        st.success("File uploaded successfully!")

        # Save to config
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "performance_path": "temp_report.csv",
                "mttr_path": "downloads/mttr_mtbf_report.xlsx"
            }, f)

    if "latest_report" in st.session_state:
        st.success("✅ Latest TappetBox report loaded")
        st.caption(st.session_state.latest_report)
        st.markdown("")

        # Clear report button
        if st.button("🗑️ Clear Report"):
            st.session_state.pop("latest_report", None)
            st.session_state.pop("mttr_report", None)
            st.session_state.vector_data = None
            st.session_state.chat_history = []

            # Delete config file
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)

            st.success("Report cleared!")
            st.rerun()
 
# =========================================
# DASHBOARD
# =========================================
 
if "latest_report" in st.session_state:
 
    try:
        df = load_and_clean_data(st.session_state.latest_report)
 
        st.subheader("📊 Industrial Operations Dashboard")
 
        # =========================================
        # KPI METRICS
        # =========================================
 
        col1, col2, col3, col4 = st.columns(4)
 
        with col1:
            st.metric("Total Machines", len(df))
 
        with col2:
            active_count = len(df[df["Current Status"] == "Active"]) if "Current Status" in df.columns else 0
            st.metric("Active Machines", active_count)
 
        with col3:
            breakdown_count = len(df[df["Current Status"] == "Breakdown"]) if "Current Status" in df.columns else 0
            st.metric("Breakdown", breakdown_count)
 
        with col4:
            idle_count = len(df[df["Current Status"] == "Idle"]) if "Current Status" in df.columns else 0
            st.metric("Idle / Unhealthy", idle_count)
 
        st.markdown("### 📈 Operational Analytics")
 
        chart_col1, chart_col2 = st.columns(2)
 
        # =========================================
        # CHART 1 — MACHINE STATUS DISTRIBUTION
        # =========================================
 
        with chart_col1:
            if "Current Status" in df.columns:
                status_counts = df["Current Status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
 
                color_map = {
                    "Active": "#22c55e",
                    "Breakdown": "#ef4444",
                    "Idle": "#f59e0b",
                    "Unhealthy": "#f97316"
                }
 
                fig_status = px.pie(
                    status_counts,
                    names="Status",
                    values="Count",
                    title="Machine Status Distribution",
                    color="Status",
                    color_discrete_map=color_map,
                    template="plotly_dark"
                )
                fig_status.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_status, use_container_width=True)
 
        # =========================================
        # CHART 2 — MACHINES BY ASSET TYPE
        # =========================================
 
        with chart_col2:
            if "Asset Type" in df.columns:
                type_counts = df["Asset Type"].value_counts().reset_index()
                type_counts.columns = ["Asset Type", "Count"]
 
                fig_type = px.bar(
                    type_counts,
                    x="Asset Type",
                    y="Count",
                    title="Machines by Asset Type",
                    template="plotly_dark",
                    color="Count",
                    color_continuous_scale="Blues"
                )
                fig_type.update_layout(xaxis_tickangle=-30)
                st.plotly_chart(fig_type, use_container_width=True)
 
        chart_col3, chart_col4 = st.columns(2)
 
        # =========================================
        # CHART 3 — TOP 10 MACHINES BY WORKING HOURS
        # =========================================
 
        with chart_col3:
            if "Working hours" in df.columns and "Asset Name" in df.columns:
                df_hours = df[df["Working hours"] > 0][["Asset Name", "Working hours"]].copy()
                df_hours = df_hours.sort_values("Working hours", ascending=False).head(10)
 
                fig_hours = px.bar(
                    df_hours,
                    x="Working hours",
                    y="Asset Name",
                    orientation="h",
                    title="Top 10 Machines by Working Hours",
                    template="plotly_dark",
                    color="Working hours",
                    color_continuous_scale="Greens"
                )
                fig_hours.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_hours, use_container_width=True)
 
        # =========================================
        # CHART 4 — TOP 10 MACHINES BY TOTAL DOWNTIME
        # =========================================
 
        with chart_col4:
            if "Maintenance Downtime" in df.columns and "Asset Name" in df.columns:
                df_down = df[df["Maintenance Downtime"] != ""][["Asset Name", "Maintenance Downtime"]].copy()
                df_down = df_down[df_down["Maintenance Downtime"] != 0]
 
                if not df_down.empty:
                    fig_down = px.bar(
                        df_down.head(10),
                        x="Maintenance Downtime",
                        y="Asset Name",
                        orientation="h",
                        title="Top 10 Machines by Maintenance Downtime",
                        template="plotly_dark",
                        color="Maintenance Downtime",
                        color_continuous_scale="Reds"
                    )
                    fig_down.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig_down, use_container_width=True)
 
        # =========================================
        # CHART 5 — AVAILABILITY % BY ASSET TYPE
        # =========================================
 
        if "Availabilty" in df.columns and "Asset Type" in df.columns:
            st.markdown("### 🔧 Availability & Utilization")
 
            avail_col1, avail_col2 = st.columns(2)
 
            with avail_col1:
                df_avail = df[df["Availabilty"] > 0].copy()
                avail_by_type = df_avail.groupby("Asset Type")["Availabilty"].mean().reset_index()
                avail_by_type.columns = ["Asset Type", "Avg Availability %"]
 
                fig_avail = px.bar(
                    avail_by_type,
                    x="Asset Type",
                    y="Avg Availability %",
                    title="Average Availability % by Asset Type",
                    template="plotly_dark",
                    color="Avg Availability %",
                    color_continuous_scale="Teal"
                )
                fig_avail.update_layout(xaxis_tickangle=-30)
                st.plotly_chart(fig_avail, use_container_width=True)
 
            with avail_col2:
                if "Fuel Consumed" in df.columns:
                    df_fuel = df[df["Fuel Consumed"] > 0][["Asset Name", "Fuel Consumed"]].copy()
                    df_fuel = df_fuel.sort_values("Fuel Consumed", ascending=False).head(10)
 
                    fig_fuel = px.bar(
                        df_fuel,
                        x="Fuel Consumed",
                        y="Asset Name",
                        orientation="h",
                        title="Top 10 Machines by Fuel Consumed",
                        template="plotly_dark",
                        color="Fuel Consumed",
                        color_continuous_scale="Oranges"
                    )
                    fig_fuel.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig_fuel, use_container_width=True)
 
        # =========================================
        # COMPARATIVE CHARTS SECTION
        # =========================================
 
        st.markdown("---")
        st.markdown("### ⚖️ Comparative Analysis")
 
        # =========================================
        # CHART 6 — TOP 15 MACHINES: FUEL vs WORKING HOURS GROUPED BAR
        # =========================================
 
        if "Fuel Consumed" in df.columns and "Working hours" in df.columns:
            df_top = df[
                (df["Fuel Consumed"] > 0) & (df["Working hours"] > 0)
            ].copy()
            df_top = df_top.sort_values(
                "Working hours", ascending=False
            ).head(15)
 
            if not df_top.empty:
                fig_fw = go.Figure()
 
                fig_fw.add_trace(go.Bar(
                    name="Working Hours",
                    x=df_top["Asset Name"],
                    y=df_top["Working hours"],
                    marker_color="#3b82f6",
                    text=df_top["Working hours"].round(1),
                    textposition="outside"
                ))
 
                fig_fw.add_trace(go.Bar(
                    name="Fuel Consumed (Litres)",
                    x=df_top["Asset Name"],
                    y=df_top["Fuel Consumed"],
                    marker_color="#f97316",
                    text=df_top["Fuel Consumed"].round(0),
                    textposition="outside"
                ))
 
                fig_fw.update_layout(
                    barmode="group",
                    title="⚡ Top 15 Machines — Working Hours vs Fuel Consumed",
                    template="plotly_dark",
                    xaxis_tickangle=-35,
                    legend=dict(orientation="h", y=1.1),
                    xaxis_title="Machine Name",
                    yaxis_title="Value"
                )
                st.plotly_chart(fig_fw, use_container_width=True)
 
        # =========================================
        # CHART 7 — SITE-WISE: TOTAL WORKING HOURS vs TOTAL FUEL
        # =========================================
 
        if "Site Name" in df.columns and "Fuel Consumed" in df.columns and "Working hours" in df.columns:
            site_compare = df.groupby("Site Name").agg(
                Total_Working_Hours=("Working hours", "sum"),
                Total_Fuel_Consumed=("Fuel Consumed", "sum"),
                Machine_Count=("Asset Name", "count")
            ).reset_index()
 
            site_compare = site_compare[
                site_compare["Total_Working_Hours"] > 0
            ].sort_values("Total_Working_Hours", ascending=False).head(15)
 
            comp_col1, comp_col2 = st.columns(2)
 
            with comp_col1:
                fig_site_hours = px.bar(
                    site_compare,
                    x="Total_Working_Hours",
                    y="Site Name",
                    orientation="h",
                    title="🏗️ Top 15 Sites by Total Working Hours",
                    template="plotly_dark",
                    color="Total_Working_Hours",
                    color_continuous_scale="Blues"
                )
                fig_site_hours.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_site_hours, use_container_width=True)
 
            with comp_col2:
                site_fuel = site_compare[site_compare["Total_Fuel_Consumed"] > 0]
                fig_site_fuel = px.bar(
                    site_fuel,
                    x="Total_Fuel_Consumed",
                    y="Site Name",
                    orientation="h",
                    title="⛽ Top 15 Sites by Total Fuel Consumed",
                    template="plotly_dark",
                    color="Total_Fuel_Consumed",
                    color_continuous_scale="Oranges"
                )
                fig_site_fuel.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_site_fuel, use_container_width=True)
 
        # =========================================
        # CHART 8 — FUEL EFFICIENCY: FUEL PER WORKING HOUR BY SITE
        # =========================================
 
        if "Site Name" in df.columns and "Fuel Consumed" in df.columns and "Working hours" in df.columns:
            df_eff = df[
                (df["Fuel Consumed"] > 0) & (df["Working hours"] > 0)
            ].copy()
            df_eff["Fuel per Hour"] = df_eff["Fuel Consumed"] / df_eff["Working hours"]
 
            site_eff = df_eff.groupby("Site Name")["Fuel per Hour"].mean().reset_index()
            site_eff = site_eff.sort_values("Fuel per Hour", ascending=False).head(15)
 
            fig_eff = px.bar(
                site_eff,
                x="Site Name",
                y="Fuel per Hour",
                title="🔥 Fuel Efficiency by Site (Litres per Working Hour) — Higher = Less Efficient",
                template="plotly_dark",
                color="Fuel per Hour",
                color_continuous_scale="RdYlGn_r"
            )
            fig_eff.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig_eff, use_container_width=True)
 
        # =========================================
        # CHART 9 — SITE: WORKING HOURS (BAR) + AVAILABILITY % (LINE)
        # =========================================
 
        if "Working hours" in df.columns and "Availabilty" in df.columns and "Site Name" in df.columns:
            df_dual = df[df["Working hours"] > 0].copy()
 
            site_dual = df_dual.groupby("Site Name").agg(
                Total_Working_Hours=("Working hours", "sum"),
                Avg_Availability=("Availabilty", "mean")
            ).reset_index()
 
            site_dual = site_dual.sort_values(
                "Total_Working_Hours", ascending=False
            ).head(12)
 
            if not site_dual.empty:
                fig_dual = go.Figure()
 
                fig_dual.add_trace(go.Bar(
                    name="Total Working Hours",
                    x=site_dual["Site Name"],
                    y=site_dual["Total_Working_Hours"],
                    marker_color="#3b82f6",
                    yaxis="y1"
                ))
 
                fig_dual.add_trace(go.Scatter(
                    name="Avg Availability %",
                    x=site_dual["Site Name"],
                    y=site_dual["Avg_Availability"],
                    mode="lines+markers+text",
                    text=site_dual["Avg_Availability"].round(1).astype(str) + "%",
                    textposition="top center",
                    marker=dict(color="#22c55e", size=8),
                    line=dict(color="#22c55e", width=2),
                    yaxis="y2"
                ))
 
                fig_dual.update_layout(
                    title="📈 Site-wise Working Hours (Bar) vs Availability % (Line)",
                    template="plotly_dark",
                    xaxis_tickangle=-35,
                    xaxis_title="Site Name",
                    yaxis=dict(
                        title=dict(
                            text="Total Working Hours",
                            font=dict(color="#3b82f6")
                        )
                    ),
                    yaxis2=dict(
                        title=dict(
                            text="Avg Availability %",
                            font=dict(color="#22c55e")
                        ),
                        overlaying="y",
                        side="right",
                        range=[85, 102]
                    ),
                    legend=dict(orientation="h", y=1.1)
                )
                st.plotly_chart(fig_dual, use_container_width=True)
 
        # =========================================
        # CHART 10 — ASSET TYPE: AVG FUEL vs AVG WORKING HOURS GROUPED BAR
        # =========================================
 
        if "Asset Type" in df.columns and "Fuel Consumed" in df.columns and "Working hours" in df.columns:
            type_avg = df.groupby("Asset Type").agg(
                Avg_Working_Hours=("Working hours", "mean"),
                Avg_Fuel_Consumed=("Fuel Consumed", "mean")
            ).reset_index()
 
            fig_grouped = go.Figure()
 
            fig_grouped.add_trace(go.Bar(
                name="Avg Working Hours",
                x=type_avg["Asset Type"],
                y=type_avg["Avg_Working_Hours"],
                marker_color="#3b82f6"
            ))
 
            fig_grouped.add_trace(go.Bar(
                name="Avg Fuel Consumed",
                x=type_avg["Asset Type"],
                y=type_avg["Avg_Fuel_Consumed"],
                marker_color="#f97316"
            ))
 
            fig_grouped.update_layout(
                barmode="group",
                title="📊 Avg Working Hours vs Avg Fuel Consumed by Asset Type",
                template="plotly_dark",
                xaxis_tickangle=-20,
                legend=dict(orientation="h", y=1.1)
            )
 
            st.plotly_chart(fig_grouped, use_container_width=True)
 
        # =========================================
        # CHART 11 — DOWNTIME vs WORKING HOURS BY SITE
        # =========================================
 
        if "Site Name" in df.columns and "Working hours" in df.columns:
            df_dt = df[df["Working hours"] > 0].copy()
 
            site_dt = df_dt.groupby("Site Name").agg(
                Total_Working_Hours=("Working hours", "sum"),
                Machine_Count=("Asset Name", "count")
            ).reset_index()
 
            site_dt = site_dt.sort_values(
                "Total_Working_Hours", ascending=False
            ).head(12)
 
            fig_site_dt = px.bar(
                site_dt,
                x="Site Name",
                y="Total_Working_Hours",
                color="Machine_Count",
                title="🏭 Total Working Hours per Site (Color = No. of Machines)",
                template="plotly_dark",
                color_continuous_scale="Viridis",
                text="Machine_Count"
            )
            fig_site_dt.update_traces(textposition="outside")
            fig_site_dt.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig_site_dt, use_container_width=True)
 
        # =========================================
        # RAW DATA TABLE
        # =========================================
 
        with st.expander("📋 View Raw Data Table"):
            st.dataframe(
                df.astype(str),
                use_container_width=True
            )
 
    except Exception as e:
        st.warning(f"Dashboard error: {e}")
 
# =========================================
# ASK QUESTIONS SECTION
# =========================================
 
st.markdown("---")
st.subheader("💬 Ask Questions")
 
question = st.text_input(
    "Ask engineering questions about rigs, downtime, MTTR, failures, maintenance etc.",
    placeholder="Example: What was the MTTR of CSD 1300L|R-210?"
)
 
if st.button("Submit"):
 
    if "latest_report" not in st.session_state:
        st.warning("Please upload or fetch a CSV report first.")
 
    elif not question:
        st.warning("Please enter a question.")
 
    else:
 
        report_path = st.session_state.latest_report
 
        # =========================================
        # BUILD VECTOR STORE ONCE
        # =========================================
 
        if st.session_state.vector_data is None:
            with st.spinner("🔄 Building AI search index from reports..."):
                mttr_path = st.session_state.get(
                    "mttr_report",
                "downloads/mttr_mtbf_report.xlsx"
                )
                index, chunks, model = create_vector_store(
                    report_path,
                    mttr_path
                )
                st.session_state.vector_data = {
                    "index": index,
                    "chunks": chunks,
                    "model": model
                }
 
        index = st.session_state.vector_data["index"]
        chunks = st.session_state.vector_data["chunks"]
        model = st.session_state.vector_data["model"]
 
        # =========================================
        # RAG SEARCH
        # =========================================
 
        with st.spinner("🔍 Searching report data..."):

            # Clean question for better RAG search
            # Replace special characters so machine names are found correctly
            cleaned_question = (
                question
                .replace("|", " ")
                .replace("-", " ")
                .replace("/", " ")
            )

            question_embedding = np.array(
                model.encode([cleaned_question])
            )

            # Always search all chunks for maximum accuracy
            total_chunks = len(chunks)
            distances, indices = index.search(
                question_embedding, k=total_chunks
            )
 
            # =========================================
            # TRY GPT IF API KEY EXISTS
            # =========================================
 
            try:
                from gpt_engine import generate_ai_answer
 
                relevant_text = "Relevant Industrial Maintenance Report Data:\n\n"
                for count, i in enumerate(indices[0], start=1):
                    relevant_text += f"\n===== RECORD {count} =====\n{chunks[i]}\n\n"

                # Add context info for GPT
                relevant_text += f"\n\nUser Original Question: {question}\n"
                relevant_text += f"Total Records in Fleet: {total_chunks}\n"
 
                answer = generate_ai_answer(question, relevant_text)
                answer_mode = "gpt"
 
            except Exception as e:
                answer_mode = "rag"
                answer = None
                print(f"GPT Error: {e}")
 
        # =========================================
        # DISPLAY ANSWER
        # =========================================
 
        st.success("✅ Analysis completed")
 
        st.markdown("## 🤖 AI Engineering Analysis")
        st.markdown("---")
 
        if answer_mode == "gpt" and answer:
            st.markdown(answer)
 
        else:
            # Show retrieved data records directly
            st.info(
                "💡 GPT API not connected yet — showing raw matched data from report. "
                "Connect your OpenAI API key to get full AI-generated analysis."
            )
 
            st.markdown(f"### 🔍 Top matches for: *\"{question}\"*")
            st.markdown("")
 
            for count, i in enumerate(indices[0], 1):
                chunk = chunks[i]
 
                with st.container():
                    st.markdown(
                        f"""
                        <div class="record-card">
                            <strong>📌 Record {count}</strong><br><br>
                            {chunk.replace(" | ", "<br>")}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
 
        st.markdown("---")
 
        # =========================================
        # SAVE TO HISTORY
        # =========================================
 
        st.session_state.chat_history.append({
            "question": question,
            "answer": answer if answer_mode == "gpt" and answer else f"[RAG Result] Top {len(indices[0])} matching records shown.",
            "mode": answer_mode
        })
 
# =========================================
# CONVERSATION HISTORY
# =========================================
 
if st.session_state.chat_history:
    st.markdown("## 📘 Engineering Conversation History")
 
    for chat in reversed(st.session_state.chat_history):
 
        with st.container():
            mode_badge = "🤖 GPT Answer" if chat.get("mode") == "gpt" else "🔍 RAG Search"
            st.markdown(f"### 🛠 Question  `{mode_badge}`")
            st.write(chat["question"])
            st.markdown("### 📊 Analysis")
            st.write(chat["answer"])
            st.markdown("---")
 


