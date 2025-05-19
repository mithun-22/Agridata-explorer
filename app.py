import streamlit as st # type: ignore
import pandas as pd
import sqlite3
import altair as alt # type: ignore

st.set_page_config(layout="wide")
st.title("ICRISAT District-Level Agricultural Analysis")

# Load data
df = pd.read_csv("ICRISAT-District Level Data - ICRISAT-District Level Data.csv")

# Create SQLite in-memory DB
conn = sqlite3.connect(":memory:")
df.to_sql("agri_data", conn, index=False, if_exists="replace")

# Query execution helper
def run_query(query):
    return pd.read_sql_query(query, conn)

# Question 1
st.subheader("1. Year-wise Trend of Rice Production Across Top 3 States")
q1 = """
SELECT Year, "State Name", SUM("RICE PRODUCTION (1000 tons)") AS total_production
FROM agri_data
GROUP BY Year, "State Name"
HAVING "State Name" IN (
    SELECT "State Name"
    FROM agri_data
    GROUP BY "State Name"
    ORDER BY SUM("RICE PRODUCTION (1000 tons)") DESC
    LIMIT 3
)
ORDER BY Year;
"""
df1 = run_query(q1)
st.altair_chart(
    alt.Chart(df1).mark_line().encode(
        x='Year:O', y='total_production:Q', color='State Name:N'
    ).properties(width=700),
    use_container_width=True
)

# Question 2
st.subheader("2. Top 5 Districts by Wheat Yield Increase Over the Last 5 Years")
q2 = """
WITH yearly_yield AS (
    SELECT "Dist Name", Year, AVG("WHEAT YIELD (Kg per ha)") AS avg_yield
    FROM agri_data
    GROUP BY "Dist Name", Year
),
diffs AS (
    SELECT a."Dist Name", 
           MAX(a.avg_yield) - MIN(a.avg_yield) AS yield_increase
    FROM yearly_yield a
    WHERE Year >= (SELECT MAX(Year) FROM agri_data) - 4
    GROUP BY a."Dist Name"
)
SELECT * FROM diffs
ORDER BY yield_increase DESC
LIMIT 5;
"""
st.dataframe(run_query(q2))

# Question 3
st.subheader("3. States with Highest Growth in Oilseed Production (5-Year Growth Rate)")
q3 = """
WITH prod_years AS (
    SELECT "State Name", Year, SUM("OILSEEDS PRODUCTION (1000 tons)") AS total_prod
    FROM agri_data
    GROUP BY "State Name", Year
),
growth_calc AS (
    SELECT "State Name",
           MAX(total_prod) - MIN(total_prod) AS growth
    FROM prod_years
    WHERE Year >= (SELECT MAX(Year) FROM agri_data) - 4
    GROUP BY "State Name"
)
SELECT * FROM growth_calc
ORDER BY growth DESC
LIMIT 5;
"""
st.dataframe(run_query(q3))

# Question 4
st.subheader("4. Correlation Between Area and Production (Rice, Wheat, Maize)")
df_corr = df[["RICE AREA (1000 ha)", "RICE PRODUCTION (1000 tons)",
              "WHEAT AREA (1000 ha)", "WHEAT PRODUCTION (1000 tons)",
              "MAIZE AREA (1000 ha)", "MAIZE PRODUCTION (1000 tons)"]].corr()
st.dataframe(df_corr)

# Question 5
st.subheader("5. Yearly Production Growth of Cotton in Top 5 Producing States")
q5 = """
SELECT Year, "State Name", SUM("COTTON PRODUCTION (1000 tons)") AS total_production
FROM agri_data
WHERE "State Name" IN (
    SELECT "State Name"
    FROM agri_data
    GROUP BY "State Name"
    ORDER BY SUM("COTTON PRODUCTION (1000 tons)") DESC
    LIMIT 5
)
GROUP BY Year, "State Name"
ORDER BY Year;
"""
df5 = run_query(q5)
st.altair_chart(
    alt.Chart(df5).mark_line().encode(
        x='Year:O', y='total_production:Q', color='State Name:N'
    ).properties(width=700),
    use_container_width=True
)

# Question 6
st.subheader("6. Districts with Highest Groundnut Production in 2020")
q6 = """
SELECT "Dist Name", "State Name", "GROUNDNUT PRODUCTION (1000 tons)"
FROM agri_data
WHERE Year = 2020
ORDER BY "GROUNDNUT PRODUCTION (1000 tons)" DESC
LIMIT 5;
"""
st.dataframe(run_query(q6))

# Question 7
st.subheader("7. Annual Average Maize Yield Across All States")
q7 = """
SELECT Year, AVG("MAIZE YIELD (Kg per ha)") AS avg_yield
FROM agri_data
GROUP BY Year
ORDER BY Year;
"""
df7 = run_query(q7)
st.altair_chart(
    alt.Chart(df7).mark_line().encode(
        x='Year:O', y='avg_yield:Q'
    ).properties(width=700),
    use_container_width=True
)

# Question 8
st.subheader("8. Total Area Cultivated for Oilseeds in Each State")
q8 = """
SELECT "State Name", SUM("OILSEEDS AREA (1000 ha)") AS total_area
FROM agri_data
GROUP BY "State Name"
ORDER BY total_area DESC;
"""
st.dataframe(run_query(q8))

# Question 9
st.subheader("9. Districts with Highest Rice Yield")
q9 = """
SELECT "Dist Name", "State Name", MAX("RICE YIELD (Kg per ha)") AS max_yield
FROM agri_data
GROUP BY "Dist Name", "State Name"
ORDER BY max_yield DESC
LIMIT 5;
"""
st.dataframe(run_query(q9))

# Question 10
st.subheader("10. Compare Wheat and Rice Production for Top 5 States Over 10 Years")
q10 = """
SELECT Year, "State Name",
       SUM("RICE PRODUCTION (1000 tons)") AS rice_production,
       SUM("WHEAT PRODUCTION (1000 tons)") AS wheat_production
FROM agri_data
WHERE "State Name" IN (
    SELECT "State Name"
    FROM agri_data
    GROUP BY "State Name"
    ORDER BY SUM("RICE PRODUCTION (1000 tons)" + "WHEAT PRODUCTION (1000 tons)") DESC
    LIMIT 5
)
GROUP BY Year, "State Name"
ORDER BY Year;
"""
st.dataframe(run_query(q10))
st.line_chart(df10.set_index("Year"), use_container_width=True)


conn.close()
