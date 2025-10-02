import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests
import json
import plotly.express as px
import numpy as np
import sqlite3

conn = sqlite3.connect("PhonePe.db")
cursor = conn.cursor()


st.set_page_config(page_title="PhonePe Dashboard", layout="wide")
st.title("PhonePe Data Analysis")

# Sidebar with option menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Data Information", "Analysed Information", "Report"],
        icons=["house", "bar-chart", "graph-up","file-earmark-text"],
        default_index=0,
        orientation="vertical"
    )

# Display based on selection
if selected == "Home":
    st.subheader("Home")
    st.write("""
    Welcome to the PhonePe Data Analysis Dashboard.  
    This project uses transaction and usage data sourced from the official PhonePe Pulse GitHub repository.  
    The data is organized in JSON format and includes detailed insights across all Indian states and union territories.

    In this dashboard, you'll find:
    - Tabular views of raw data for exploration
    - Visualizations to understand usage patterns
    - Analytical summaries to compare performance across regions

    *Navigate through the sidebar to find different sections of the dashboard.
    """)

    # Here we are loading all 3 CSV files from Aggregated folder
    df_txn = pd.read_csv("E:/PhonePe/Aggregate_Transaction.csv")
    df_user = pd.read_csv("E:/PhonePe/Aggregate_User.csv")
    df_insurance = pd.read_csv("E:/PhonePe/Aggregate_Insurance.csv")

    # Standardize state names

    for df in [df_txn, df_user, df_insurance]:
        df["State"] = df["State"].str.title().str.strip()

    st.markdown("### Filter Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.selectbox("Select Year", sorted(set(df_txn["Year"]).union(df_user["Year"]).union(df_insurance["Year"])))
    with col2:
        quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])
    with col3:
        data_type = st.selectbox("Select Data Type", ["Transaction", "User", "Insurance"])
    
    # Filter and aggregate based on selection
    if data_type == "Transaction":
        filtered = df_txn[(df_txn["Year"] == year) & (df_txn["Quater"] == quarter)]
        agg = filtered.groupby("State")[["Transaction_Amount", "Transaction_Count"]].sum().reset_index()
        value_col = "Transaction_Amount"
    elif data_type == "User":
        filtered = df_user[(df_user["Year"] == year) & (df_user["Quater"] == quarter)]
        agg = filtered.groupby("State")[["User_Count"]].sum().reset_index()
        value_col = "User_Count"
    elif data_type == "Insurance":
        filtered = df_insurance[(df_insurance["Year"] == year) & (df_insurance["Quater"] == quarter)]
        agg = filtered.groupby("State")[["Insurance_Amount", "Insurance_Count"]].sum().reset_index()
        value_col = "Insurance_Amount"
# Load India GeoJSON
    url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    india_geo = json.loads(requests.get(url).content)

    # Layout split: Map on left, details on right
    left, right = st.columns([2, 1])
    if agg.empty:
        st.warning(" No data available for the selected Year and Quarter.")
    else:
        with left:
            fig_map = px.choropleth(
                agg,
                geojson=india_geo,
                featureidkey="properties.ST_NM",
                locations="State",
                color=value_col,
                hover_name="State",
                hover_data={col: True for col in agg.columns if col != "State"},
                color_continuous_scale="YlGnBu",
                title=f"{data_type} Data — Q{quarter} {year}"
            )
            fig_map.update_geos(
                visible=False,
                projection=dict(type='mercator'),
                lonaxis=dict(range=[68, 98]),
                lataxis=dict(range=[6, 38])
                    )

            fig_map.update_layout(
            title=dict(text="PhonePe Transaction Amount by State", x=0.5),
            margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
            height=700,
            width=1000
                )
            fig_map.update_traces(
                hovertemplate="<b>%{location}</b><br><span style='color:#28a745'><b>Value:</b></span> %{z:,}<extra></extra>"
                    )

            st.plotly_chart(fig_map, use_container_width=True)

        with right:
        
            st.markdown("###  Top 10 States by Value")
            top10 = agg.sort_values(by=value_col, ascending=False).head(10)
            top10.index = range(1, 11)  # Set index from 1 to 10
            st.dataframe(
                top10.style
                .background_gradient(cmap="Greens")
                .format({value_col: "{:,.0f}"})
            )

            st.markdown("###  Least 10 States by Value")
            bottom10 = agg.sort_values(by=value_col, ascending=True).head(10)
            bottom10.index = range(1, 11)  # Set index from 1 to 10
            st.dataframe(
                bottom10.style
                .background_gradient(cmap="Reds")
                .format({value_col: "{:,.0f}"})
            )
 
elif selected == "Data Information":
    st.subheader("Data Information")
    st.write("""
    This section presents the raw data extracted from PhonePe Pulse in a structured format.  
    The data includes metrics such as transaction counts, payment types, user registrations, and more.
             
    - Interactive tables for browsing state-wise data
    - CSV views for download or inspection
    - Visual charts to see trends and distributions

    Use this section to get more info with the  dataset before knowing into deeper analysis.
    """)
    st.markdown("### View Raw Data and Visualisation")
    with st.expander("choose one"):
  
        menu_choice = st.radio("Choose Mode", ["Raw Data", "Visualizations"], horizontal=True)
    if menu_choice == "Raw Data":
        # Load all CSVs
        df_txn = pd.read_csv("E:/PhonePe/Aggregate_Transaction.csv")
        df_user = pd.read_csv("E:/PhonePe/Aggregate_User.csv")
        df_ins = pd.read_csv("E:/PhonePe/Aggregate_Insurance.csv")
        df_map_txn = pd.read_csv("E:/PhonePe/Map_Transaction.csv")
        df_map_user = pd.read_csv("E:/PhonePe/Map_User.csv")
        df_map_ins = pd.read_csv("E:/PhonePe/Map_Insurance.csv")
        df_top_txn = pd.read_csv("E:/PhonePe/Top_Transaction.csv")
        df_top_user = pd.read_csv("E:/PhonePe/Top_User.csv")
        df_top_ins = pd.read_csv("E:/PhonePe/Top_Insurance.csv")

        csv_options = {
            "Transaction Aggregated": df_txn,
            "User Aggregated": df_user,
            "Insurance Aggregated": df_ins,
            "Transaction Map": df_map_txn,
            "User Map": df_map_user,
            "Insurance Map": df_map_ins,
            "Transaction Top": df_top_txn,
            "User Top": df_top_user,
            "Insurance Top": df_top_ins
            }

        selected_csv = st.selectbox("Select a dataset to view", list(csv_options.keys()))
        st.dataframe(csv_options[selected_csv]) 
    elif menu_choice == "Visualizations":
        #if menu_choice == "Visualizations":
                # Load all CSVs
        df_txn = pd.read_csv("E:/PhonePe/Aggregate_Transaction.csv")
        df_user = pd.read_csv("E:/PhonePe/Aggregate_User.csv")
        df_ins = pd.read_csv("E:/PhonePe/Aggregate_Insurance.csv")
        df_map_txn = pd.read_csv("E:/PhonePe/Map_Transaction.csv")
        df_map_user = pd.read_csv("E:/PhonePe/Map_User.csv")
        df_map_ins = pd.read_csv("E:/PhonePe/Map_Insurance.csv")
        df_top_txn = pd.read_csv("E:/PhonePe/Top_Transaction.csv")
        df_top_user = pd.read_csv("E:/PhonePe/Top_User.csv")
        df_top_ins = pd.read_csv("E:/PhonePe/Top_Insurance.csv")    

        st.markdown("### Filter Options")

        col1, col2, col3 = st.columns(3)
        with col1:
            selected_year = st.selectbox("Select Year", sorted(df_txn["Year"].unique()))
        with col2:
            selected_quarter = st.selectbox("Select Quarter", sorted(df_txn["Quater"].unique()))
        with col3:
            selected_state = st.selectbox("Select State", sorted(df_txn["State"].unique()))

        
        filtered_txn = df_txn[
            (df_txn["Year"] == selected_year) &
            (df_txn["Quater"] == selected_quarter) &
            (df_txn["State"] == selected_state)
                ]
        df_ins_filtered = df_ins[
            (df_ins["State"] == selected_state) &
            (df_ins["Year"] == selected_year) &
            (df_ins["Quater"] == selected_quarter)
                        ]
        df_district_filtered = df_map_txn[
            (df_map_txn["State"] == selected_state) &
            (df_map_txn["Year"] == selected_year) &
            (df_map_txn["Quater"] == selected_quarter)
                ]

        fig_district_bar = px.bar(
            df_district_filtered,
            x="District",
            y="Transaction_Count",
            color="District",
            title=f"District-wise Transactions in {selected_state} - Q{selected_quarter}, {selected_year}"
            )
        st.plotly_chart(fig_district_bar)

        fig_insurance_curve = px.bar(
            df_ins_filtered,
            x="Transaction_Name",
            y="Insurance_Count",
            color="Transaction_Name",
            title=f"Insurance Transactions in {selected_state} - Q{selected_quarter}, {selected_year}"
                )
        st.plotly_chart(fig_insurance_curve)

        fig_txn_trend = px.bar(
            filtered_txn,
            x="Transaction_Name",
            y="Transaction_Count",
            color="Transaction_Name",
            title=f" Transactions in {selected_state} - Q{selected_quarter}, {selected_year}"
                )
        st.plotly_chart(fig_txn_trend)

        fig_txn_amount = px.pie(
                filtered_txn,
                names="Transaction_Name",
                values="Transaction_Amount",
                title=f"Transaction Amount Distribution in {selected_state} - Q{selected_quarter}, {selected_year}"
                    )
        st.plotly_chart(fig_txn_amount)

        df_pincode_filtered = df_top_txn[
            (df_top_txn["State"] == selected_state) &
            (df_top_txn["Year"] == selected_year) &
            (df_top_txn["Quater"] == selected_quarter)
                ]

        filtered_pincode_sorted = df_pincode_filtered.sort_values(by="Transaction_Count", ascending=False).head(15)

        fig_pincode_horizontal = px.bar(
            filtered_pincode_sorted,
            x="Transaction_Count",
            y="Pincode",
            
            color="Transaction_Count",
            title=f"Top 15 Pincode Transactions in {selected_state} - Q{selected_quarter}, {selected_year}",
            log_x=True  # Optional: makes small values more visible
                )
        st.plotly_chart(fig_pincode_horizontal)


        df_yearly = df_txn[df_txn["State"] == selected_state]

        fig_yearly_trend = px.bar(
            df_yearly,
            x="Year",
            y="Transaction_Count",
            color="Quater",
            barmode="group",
            title=f"Yearly Transaction Trends in {selected_state}"
                )
        st.plotly_chart(fig_yearly_trend)


elif selected == "Analysed Information":
    st.subheader("Analysed Information")
    st.write("""
    In this section, we present insights derived from the collected data.  
    Through comparative analysis, we explore how PhonePe usage varies across states and over time.

    - Decoding Transaction Dynamics on PhonePe
    - Device Dominance and User Engagement Analysis
    - Transaction Analysis for Market Expansion
    - User Engagement and Growth Strategy
    - Transaction Analysis Across States and Districts

    These insights help us understand the digital payment landscape.
    """)

    
    with st.expander("Choose one"):
        analysis_option = st.radio("Options", ["Decoding Transaction Dynamics on PhonePe",
        "Device Dominance and User Engagement Analysis",
        "User Engagement and Growth Strategy",
        "Transaction Analysis Across States and Districts",
        "Transaction Analysis for Market Expansion",
        "Insurance Transactions Analysis"])

    if analysis_option == "Decoding Transaction Dynamics on PhonePe":
        st.header(" Decoding Transaction Dynamics on PhonePe")

        
        tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs([
            "Total Transaction Amount by State",
            "Quarterly Transaction Trends",
            "Transaction Type Breakdown by State",
            "Yearly Growth by Transaction Type",
            "Top Transaction Types Overall","Final"
                    ])
        

        
        with tab1:
            st.subheader(" Total Transaction Amount by State")
            query1 = """
                SELECT State, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State
                ORDER BY Total_Transaction_Amount DESC;
            """
            df1 = pd.read_sql_query(query1, conn)
            sorted_df1 = df1.sort_values(by="Total_Transaction_Amount", ascending=False)
            #st.bar_chart(df1.set_index("State"))
            st.bar_chart(sorted_df1.set_index("State"))

            # Show table below
            st.dataframe(sorted_df1)

        with tab2:
            st.subheader(" Quarterly Transaction Trends by State")
            query2 = """
                SELECT State, Year, Quater, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State, Year, Quater
                ORDER BY State, Year, Quater;
            """
            df2 = pd.read_sql_query(query2, conn)
            
            selected_state = st.selectbox("Choose a State", df2["State"].unique())
            filtered_df2 = df2[df2["State"] == selected_state]
            filtered_df2["Year_Quarter"] = filtered_df2["Year"].astype(str) + " Q" + filtered_df2["Quater"].astype(str)

            # Set index and plot
            chart_df = filtered_df2.set_index("Year_Quarter")["Total_Transaction_Amount"]
            st.line_chart(chart_df)
            #st.line_chart(filtered_df2.pivot_table(index=["Year", "Quater"], values="Total_Transaction_Amount"))
            st.dataframe(df2)

        with tab3:
            st.subheader(" Transaction Type Breakdown by State")
            query3 = """
                SELECT State, Transaction_Name, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State, Transaction_Name
                ORDER BY State, Total_Transaction_Amount DESC;
            """
            df3 = pd.read_sql_query(query3, conn)
            
            selected_state = st.selectbox("Select State for Breakdown", df3["State"].unique())
            filtered_df3 = df3[df3["State"] == selected_state]
            st.bar_chart(filtered_df3.set_index("Transaction_Name"))

            st.dataframe(df3)

        with tab4:
            st.subheader(" Yearly Growth by Transaction Type")
            query4 = """
                SELECT Year, Transaction_Name, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY Year, Transaction_Name
                ORDER BY Year, Transaction_Name;
            """
            df4 = pd.read_sql_query(query4, conn)
            
            selected_type = st.selectbox("Choose Transaction Type", df4["Transaction_Name"].unique())
            filtered_df4 = df4[df4["Transaction_Name"] == selected_type]
            if filtered_df4["Year"].nunique() > 1:
                fig = px.line(
                filtered_df4,
                x="Year",
                y="Total_Transaction_Amount",
                markers=True,
                title=f"Yearly Growth for {selected_type}"
                )
                st.plotly_chart(fig)
            else:
                st.warning("Not enough data points across years to show a trend")

            st.dataframe(df4)

        with tab5:
            st.subheader(" Top Transaction Types Overall")
            query5 = """
                SELECT Transaction_Name, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY Transaction_Name
                ORDER BY Total_Transaction_Amount DESC;
            """
            df5 = pd.read_sql_query(query5, conn)
            
            st.bar_chart(df5.set_index("Transaction_Name"))

            st.dataframe(df5)

        with tab6:
            
            st.subheader(" Overall Transaction Trend Across India")

            query = """
                SELECT Year, Quater, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY Year, Quater
                ORDER BY Year, Quater;
            """
            df = pd.read_sql_query(query, conn)

            # Combine Year and Quarter for timeline
            df["Year_Quarter"] = df["Year"].astype(str) + " Q" + df["Quater"].astype(str)

            # Plot line chart
            st.line_chart(df.set_index("Year_Quarter")["Total_Transaction_Amount"])

    if analysis_option == "Device Dominance and User Engagement Analysis":
        st.header(" Device Dominance and User Engagement Analysis")

        tab1, tab2, tab3, tab4,tab5 = st.tabs([
            "Total Users by Device Brand",
            "Device Usage by State",
            "Yearly Trends by Brand",
            "Quarterly Growth by Brand",
            "State Vs Brand"
            ])

    #  Tab 1: Total Users by Device Brand
        with tab1:
            st.subheader(" Total Registered Users by Device Brand")
            query1 = """
                SELECT User_Brand, SUM(User_Count) AS Total_Users
                FROM Aggregate_User
                GROUP BY User_Brand
                ORDER BY Total_Users DESC;
            """
            df1 = pd.read_sql_query(query1, conn)
            
            st.bar_chart(df1.set_index("User_Brand"))

            st.dataframe(df1)

        #  Tab 2: Device Usage by State
        with tab2:
            st.subheader(" Device Brand Usage by State")
            query2 = """
                SELECT State, User_Brand, SUM(User_Count) AS Total_Users
                FROM Aggregate_User
                GROUP BY State, User_Brand
                ORDER BY State, Total_Users DESC;
            """
            df2 = pd.read_sql_query(query2, conn)
            

            selected_state = st.selectbox("Choose a State", df2["State"].unique())
            filtered_df2 = df2[df2["State"] == selected_state]
            st.bar_chart(filtered_df2.set_index("User_Brand"))

            st.dataframe(df2)

        #  Tab 3: Yearly Trends by Brand
        with tab3:
            st.subheader(" Yearly Trends by Device Brand")
            query3 = """
                SELECT User_Brand, Year, SUM(User_Count) AS Total_Users
                FROM Aggregate_User
                GROUP BY User_Brand, Year
                ORDER BY User_Brand, Year;
            """
            df3 = pd.read_sql_query(query3, conn)
           
            selected_brand = st.selectbox("Choose a Device Brand", df3["User_Brand"].unique())
            filtered_df3 = df3[df3["User_Brand"] == selected_brand]
            st.line_chart(filtered_df3.set_index("Year")["Total_Users"])

            st.dataframe(df3)


        # Tab 4: Quarterly Growth by Brand
        with tab4:
            st.subheader(" Quarterly Growth by Device Brand")
            query4 = """
                SELECT User_Brand, Year, Quater, SUM(User_Count) AS Total_Users
                FROM Aggregate_User
                GROUP BY User_Brand, Year, Quater
                ORDER BY User_Brand, Year, Quater;
            """
            df4 = pd.read_sql_query(query4, conn)
            

            selected_brand_q = st.selectbox("Select Device Brand", df4["User_Brand"].unique())
            filtered_df4 = df4[df4["User_Brand"] == selected_brand_q]
            filtered_df4["Year_Quarter"] = filtered_df4["Year"].astype(str) + " Q" + filtered_df4["Quater"].astype(str)
            st.line_chart(filtered_df4.set_index("Year_Quarter")["Total_Users"])

            st.dataframe(df4)

        
        with tab5:
            st.subheader(" State vs Device Brand Usage")

            query5 = """
                SELECT State, User_Brand, SUM(User_Count) AS Total_Users
                FROM Aggregate_User
                GROUP BY State, User_Brand
                ORDER BY State, Total_Users DESC;
            """
            df5 = pd.read_sql_query(query5, conn)
            

            # Optional filter
            selected_brand = st.selectbox("Filter by Device Brand (optional)", ["All"] + sorted(df5["User_Brand"].unique()))
            if selected_brand != "All":
                df5 = df5[df5["User_Brand"] == selected_brand]

            # Pivot for grouped bar chart
            pivot_df = df5.pivot_table(index="State", columns="User_Brand", values="Total_Users", fill_value=0)

            st.bar_chart(pivot_df)

            st.dataframe(df5)
    if analysis_option == "User Engagement and Growth Strategy":
        
        st.header(" User Engagement and Growth Strategy")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Registered Users by State",
            "App Opens by State",
            "District-Level Engagement",
            "Engagement Ratio by District",
            "Quarterly Growth in App Opens"
        ])

        #  Tab 1: Registered Users by State
        with tab1:
            st.subheader(" Total Registered Users by State")
            query1 = """
                SELECT State, SUM(Registerd_Users) AS Total_Registered
                FROM Map_User
                GROUP BY State
                ORDER BY Total_Registered DESC;
            """
            df1 = pd.read_sql_query(query1, conn)
        
          
            st.bar_chart(df1.set_index("State"))

            st.dataframe(df1)

        # Tab 2: App Opens by State
        with tab2:
            st.subheader(" Total App Opens by State")
            
            query2 = """
                SELECT State, SUM(App_Count) AS Total_App_Counts
                FROM Map_User
                GROUP BY State
                ORDER BY Total_App_Counts DESC;
            """
            df2 = pd.read_sql_query(query2, conn)

            
            st.bar_chart(df2.set_index("State"))

            st.dataframe(df2)

        #  Tab 3: District-Level Engagement
        with tab3:
            st.subheader(" District-Level Engagement")
            query3 = """
                SELECT State, District, SUM(Registerd_Users) AS Total_Registered, SUM(App_Count) AS Total_App_Counts
                FROM Map_User
                GROUP BY State, District
                ORDER BY State, Total_App_Counts DESC;
            """
            df3 = pd.read_sql_query(query3, conn)
           

            selected_state = st.selectbox("Choose a State", df3["State"].unique())
            filtered_df3 = df3[df3["State"] == selected_state]
            st.bar_chart(filtered_df3.set_index("District")[["Total_App_Counts", "Total_Registered"]])

            st.dataframe(df3)

        #  Tab 4: Engagement Ratio by District
        with tab4:
            st.subheader(" Engagement Ratio by District")
            query4 = """
                SELECT State, District, SUM(App_Count)*1.0 / SUM(Registerd_Users) AS Engagement_Rate
                FROM Map_User
                GROUP BY State, District
                ORDER BY Engagement_Rate DESC;
            """
            df4 = pd.read_sql_query(query4, conn)
            

            top_districts = df4.head(20)
            st.bar_chart(top_districts.set_index("District")["Engagement_Rate"])

            st.dataframe(df4)

        #  Tab 5: Quarterly Growth in App Opens
        with tab5:
            st.subheader(" Quarterly Growth in App Opens")
            query5 = """
                SELECT State, Year, Quater, SUM(App_Count) AS Total_App_Counts
                FROM Map_User
                GROUP BY State, Year, Quater
                ORDER BY State, Year, Quater;
            """
            df5 = pd.read_sql_query(query5, conn)
            

            selected_state_q = st.selectbox("Select State", df5["State"].unique())
            filtered_df5 = df5[df5["State"] == selected_state_q]
            filtered_df5["Year_Quarter"] = filtered_df5["Year"].astype(str) + " Q" + filtered_df5["Quater"].astype(str)
            st.line_chart(filtered_df5.set_index("Year_Quarter")["Total_App_Counts"])

            st.dataframe(df5)

    if analysis_option == "Transaction Analysis for Market Expansion":
        st.markdown("## Transaction Analysis for Market Expansion")
        st.markdown("""
        PhonePe operates in a highly competitive market, and understanding transaction dynamics at the state level is crucial for strategic decision-making. 
        This section explores transaction trends, regional growth, and high-performing pincodes to uncover opportunities for expansion and deeper market penetration.
        """)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Total Transaction by State",
            "Yearly Growth by State",
            "Quarterly Trends by Type",
            "Top Pincodes by Amount",
            "State-Wise Pincode Performance"
        ])

        # Tab 1: Total Transaction Amount by State
        with tab1:
            query1 = """
                SELECT State, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State
                ORDER BY State, Total_Transaction_Amount DESC;
            """
            df1 = pd.read_sql_query(query1, conn)
            
            st.bar_chart(df1.set_index("State"))

            st.dataframe(df1)

        # Tab 2: Yearly Growth by State
        with tab2:
            query2 = """
                SELECT State, Year, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State, Year
                ORDER BY State, Year;
            """
            df2 = pd.read_sql_query(query2, conn)
            
            st.line_chart(df2.pivot(index="Year", columns="State", values="Total_Transaction_Amount"))

            st.dataframe(df2)

        #  Tab 3: Quarterly Trends by Transaction Type
        with tab3:
            query3 = """
                SELECT State, Transaction_Name, Year, Quater, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State, Transaction_Name, Year, Quater
                ORDER BY State, Transaction_Name, Year, Quater;
            """
            df3 = pd.read_sql_query(query3, conn)
            
            st.markdown("#### Sample Trend (Choose State & Type)")
            states = df3["State"].unique()
            types = df3["Transaction_Name"].unique()
            selected_state = st.selectbox("Select State", states)
            selected_type = st.selectbox("Select Transaction Type", types)
            filtered = df3[(df3["State"] == selected_state) & (df3["Transaction_Name"] == selected_type)]
            chart_data = filtered.pivot_table(index=["Year", "Quater"], values="Total_Transaction_Amount", aggfunc="sum").reset_index()
            st.line_chart(chart_data)

            st.dataframe(df3)

        #  Tab 4: Top Pincodes by Transaction Amount
        with tab4:
            df_check = pd.read_sql_query("SELECT * FROM Top_Transaction LIMIT 5;", conn)
            st.write(df_check.columns.tolist())

            query4 = """
                SELECT Pincode, SUM(Transaction_Amount) AS Total_Amount
                FROM Top_Transaction
                GROUP BY Pincode
                ORDER BY Total_Amount DESC;
            """
            df4 = pd.read_sql_query(query4, conn)
            
            st.bar_chart(df4.set_index("Pincode").head(10))

            st.dataframe(df4)

        # Tab 5: State-Wise Pincode Performance
        with tab5:
            query5 = """
                SELECT State, Pincode, SUM(Transaction_Amount) AS Total_Amount
                FROM Top_Transaction
                GROUP BY State, Pincode
                ORDER BY State, Total_Amount DESC;
            """
            df5 = pd.read_sql_query(query5, conn)       
            st.markdown("#### Select State to View Top Pincodes")
            selected_state = st.selectbox("Choose State", df5["State"].unique())
            filtered_df = df5[df5["State"] == selected_state]
            st.bar_chart(filtered_df.set_index("Pincode").head(10))

            st.dataframe(df5)


        conn.close()

    if analysis_option == "Transaction Analysis Across States and Districts":
        st.markdown("## Transaction Analysis Across States and Districts")
        st.markdown("""
        PhonePe is analyzing transaction data to identify the top-performing states, districts, and pin codes in terms of transaction volume and value. 
        This helps uncover user engagement patterns and guide targeted marketing efforts.
        """)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Top States by Amount",
            "Top States by Volume",
            "Top Districts by Amount",
            "Top Districts by Volume",
            "Top Pincodes by Amount",
            "Top Pincodes by Volume"
        ])

        #  Tab 1: Top States by Transaction Amount
        with tab1:
            query1 = """
                SELECT State, SUM(Transaction_Amount) AS Total_Transaction_Amount
                FROM Aggregate_Transaction
                GROUP BY State
                ORDER BY Total_Transaction_Amount DESC;
            """
            df1 = pd.read_sql_query(query1, conn)
            
            st.bar_chart(df1.set_index("State").head(10))

            st.dataframe(df1)

        # Tab 2: Top States by Transaction Volume
        with tab2:
            query2 = """
                SELECT State, SUM(Transaction_Count) AS Total_Transaction_Count
                FROM Aggregate_Transaction
                GROUP BY State
                ORDER BY Total_Transaction_Count DESC;
            """
            df2 = pd.read_sql_query(query2, conn)
            
            st.bar_chart(df2.set_index("State").head(10))

            st.dataframe(df2)

        # Tab 3: Top Districts by Transaction Amount
        with tab3:
            query3 = """
                SELECT District, SUM(Transaction_Amount) AS Total_Amount
                FROM Map_Transaction
                GROUP BY District
                ORDER BY Total_Amount DESC;
            """
            df3 = pd.read_sql_query(query3, conn)
            
            st.bar_chart(df3.set_index("District").head(10))

            st.dataframe(df3)

        # Tab 4: Top Districts by Transaction Volume
        with tab4:
            query4 = """
                SELECT District, SUM(Transaction_Count) AS Total_Count
                FROM Map_Transaction
                GROUP BY District
                ORDER BY Total_Count DESC;
            """
            df4 = pd.read_sql_query(query4, conn)
          
            st.bar_chart(df4.set_index("District").head(10))

            st.dataframe(df4)

        # Tab 5: Top Pincodes by Transaction Amount
        with tab5:
            query5 = """
                SELECT Pincode, SUM(Transaction_Amount) AS Total_Amount
                FROM Top_Transaction
                GROUP BY Pincode
                ORDER BY Total_Amount DESC
                LIMIT 10;
            """
            df5 = pd.read_sql_query(query5, conn)
           
            st.bar_chart(df5.set_index("Pincode"))

            st.dataframe(df5)

        #  Tab 6: Top Pincodes by Transaction Volume
        with tab6:
            query6 = """
                SELECT Pincode, SUM(Transaction_Count) AS Total_Count
                FROM Top_Transaction
                GROUP BY Pincode
                ORDER BY Total_Count DESC
                LIMIT 10;
            """
            df6 = pd.read_sql_query(query6, conn)
            
            st.bar_chart(df6.set_index("Pincode"))

            st.dataframe(df6)
    if analysis_option == "Insurance Transactions Analysis":
        st.markdown("## Insurance Transactions Analysis")
        st.markdown("""
        PhonePe aims to analyze insurance transactions to identify the top states, districts, and pin codes where the most insurance transactions occurred during a specific year–quarter combination. 
        This helps understand user engagement in the insurance sector and informs strategic decisions.
        """)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Top States by Insurance Count",
            "Top Districts by Insurance Count",
            "Top Pincodes by Insurance Count",
            "State-Wise Insurance Trend",
            "Year-Quarter Breakdown"
        ])

        # Tab 1: Top States by Insurance Count
        with tab1:
            query1 = """
                SELECT State, SUM(Insurance_Count) AS Total_Insurance_Transactions
                FROM Aggregate_Insurance
                GROUP BY State
                ORDER BY Total_Insurance_Transactions DESC;
            """
            df1 = pd.read_sql_query(query1, conn)
            
            st.bar_chart(df1.set_index("State"))

            st.dataframe(df1)

            

        # Tab 2: Top Districts by Insurance Count
        with tab2:
            query2 = """
                SELECT District, SUM(Insurance_Count) AS Total_Insurance_Transactions
                FROM Map_Insurance
                GROUP BY District
                ORDER BY Total_Insurance_Transactions DESC;
            """
            df2 = pd.read_sql_query(query2, conn)
            
            st.bar_chart(df2.set_index("District").head(10))
            st.dataframe(df2)

        #  Tab 3: Top Pincodes by Insurance Count
        with tab3:
            query3 = """
                SELECT Pincode, SUM(Insurance_Count) AS Total_Insurance_Transactions
                FROM Top_Insurance
                GROUP BY Pincode
                ORDER BY Total_Insurance_Transactions DESC
                LIMIT 10;
            """
            df3 = pd.read_sql_query(query3, conn)
            
            st.bar_chart(df3.set_index("Pincode"))

            st.dataframe(df3)

        #  Tab 4: State-Wise Insurance Trend Over Time
        with tab4:
            query4 = """
                SELECT State, Year, Quater, SUM(Insurance_Count) AS Total_Insurance_Transactions
                FROM Aggregate_Insurance
                GROUP BY State, Year, Quater
                ORDER BY State, Year, Quater;
            """
            df4 = pd.read_sql_query(query4, conn)
            
            selected_state = st.selectbox("Choose State", df4["State"].unique())
            filtered_df = df4[df4["State"] == selected_state]
            chart_data = filtered_df.pivot_table(index=["Year", "Quater"], values="Total_Insurance_Transactions", aggfunc="sum").reset_index()
            st.line_chart(chart_data, x="Year", y="Total_Insurance_Transactions")

            st.dataframe(df4)

        # Tab 5: Year–Quarter Breakdown Across States
        with tab5:
            year = st.selectbox("Select Year", sorted(df4["Year"].unique()))
            quarter = st.selectbox("Select Quarter", sorted(df4["Quater"].unique()))
            filtered_yq = df4[(df4["Year"] == year) & (df4["Quater"] == quarter)]
            
            st.bar_chart(filtered_yq.set_index("State"))

            st.dataframe(filtered_yq.sort_values(by="Total_Insurance_Transactions", ascending=False))



elif selected == "Report":
    st.subheader(" Conclusion or Report&Recommendations")
    st.write("""
    Based on the analysis of PhonePe usage data across various states and transaction categories,  
    this report outlines key observations and strategic recommendations to support future growth.""")

    with st.expander("Final Report & Observations", expanded=True):
        st.markdown("## Final Report & Observations")
        st.markdown("""
        Based on my analysis of PhonePe's transaction and user engagement data across states, districts, and pincodes, the following observations and strategic insights have emerged:
        """)

        st.markdown("### Key Observations")
        st.markdown("""
            - From the data, it's clear that states like Andhra Pradesh, Karnataka, Maharashtra, and Telangana are leading in digital transactions. 
            - States like Bihar, Delhi, Tamil Nadu, Gujarat, Haryana, and Odisha are showing good growth in recent years.
            - On the other hand, border and northeastern states—such as Arunachal Pradesh, Chandigarh, Ladakh, Daman and Diu, Meghalaya, Mizoram, Nagaland, and Sikkim—have lower usage. This might be due to fewer facilities, security concerns, or lack of awareness.
            - The good news is that in the last few quarters of 2024, usage has started to rise in almost all regions. With a little extra effort, this growth can continue.
            - Peer-to-peer transfers, mobile recharges, and merchant payments are doing well in most places.
            - Insurance transactions are still low in border states, showing that people may not know much about them or don’t use them yet.
            - Spread Awareness: Use ads and campaigns to teach people about insurance and digital payments, especially in low-usage areas.
            - Recharge Offers: Give discounts or cashback on mobile recharges to attract more users.
            - Partner with Mobile Brands: Work with phone companies to include or recommend PhonePe as a trusted app for payments.
            - Local Language Campaigns: Use regional languages and local culture to make people feel more comfortable using the app.

        """)

        st.markdown("### Strategy Suggestion")
        st.markdown("""
            - Focus on states that are already growing well.
            - Push insurance awareness in places where it’s starting to grow.
            - Use district-level data to plan better partnerships.
            - Watch quarterly trends to adjust campaigns.

        """)

        st.markdown("### Conclusion")
        st.markdown("""
        This dashboard gives a full picture of how PhonePe is being used across India. It shows where things are working well and where there’s room to grow. These insights can help guide future plans—for payments, insurance, and reaching new regions.
        """)
    with st.expander("Personal Reflection & Project Journey", expanded=True):
        st.markdown("## Personal Reflection & Project Journey")
        st.markdown("""
        This project marks my **first experience writing code**. Coming from an **accounting background**, I never imagined myself working with Python, data structures, or building dashboards. But over the past 10 days, I committed myself fully to learning, exploring, and understanding the process behind this PhonePe data analysis.

        ###  Technical Journey
        - I collected JSON data from GitHub and used Python libraries like `os`, `pandas`, `sqlite3`, `streamlit`, `json`, and `plotly`.
        - I wrote custom Python code to extract data from individual files and store it in dictionaries with structured column lists.
        - The dataset was organized into **3 main folders**, each with **3 subfolders**, resulting in **9 key files**:
            - `Aggregate_Transaction`, `Aggregate_User`, `Aggregate_Insurance`
            - `Map_Transaction`, `Map_User`, `Map_Insurance`
            - `Top_Transaction`, `Top_User`, `Top_Insurance`
        - I converted all JSON files to CSV, then into SQL tables for structured querying and analysis.
        - I performed multiple comparisons and visualizations to understand performance variations across states, districts, and pincodes.

        ###  Business Case Studies Explored
        - *Decoding Transaction Dynamics on PhonePe*
        - *Device Dominance and User Engagement Analysis*
        - *User Engagement and Growth Strategy*
        - *Transaction Analysis Across States and Districts*
        - *Transaction Analysis for Market Expansion*
        - *Insurance Transactions Analysis*

        ###  Personal Reflection
        I spent **6 to 7 hours daily**, learning from class recordings, GitHub, Copilot, YouTube, Google, and asking questions wherever I could. My only goal was **not to copy-paste blindly**, but to understand what I was building—even if just the basics.

        I'm submitting this on the **last day**, and while I know there's more to learn, I feel  little happy and proud**. This project gave me the confidence to believe that I can try something in the software field. I’m grateful for the opportunity—it made me think, learn, and grow in ways I never expected.
        """)
conn.commit()
conn.close()

    