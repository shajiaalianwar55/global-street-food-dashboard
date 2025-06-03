#  GLOBAL STREET-FOOD DASHBOARD
import pandas as pd          # data tables
import numpy as np           # easy numeric operations
import plotly.express as px  # interactive charts
import streamlit as st       # turns this script into a web app

#----------------------- DATA LOAD & CLEAN-------------------------#
df = pd.read_csv("global_street_food_cleaned.csv")

# Fix typo
df["Country"] = df["Country"].str.replace("Leba0n", "Lebanon")

# Remove accidental spaces in column headers
df.columns = df.columns.str.strip()

# Make price numeric
df["TypicalPrice(USD)"] =pd.to_numeric(df["TypicalPrice(USD)"], errors="coerce")

# How many ingredients does each dish list? (split on commas)
if "Ingredients" in df.columns:
    df["IngredientCount"] = df["Ingredients"].str.split(",").str.len()
else:
    # Fallback: use length of Description words if Ingredients column absent
    df["IngredientCount"] = df["Description"].str.split().str.len()

# Clean up NULLS
df.dropna(inplace=True)

#------------------------STREAMLIT PAGE--------------------#
st.set_page_config(page_title="Global Street Food Dashboard", layout="wide")
st.title("Global Street Food Pricing")
all_countries = sorted(df["Country"].unique())
selected_country = st.sidebar.selectbox("Filter by Country", ["All"] + all_countries)

# Filter logic
filtered_df = df.copy() if selected_country == "All" else df[df["Country"] == selected_country]
if filtered_df.empty:
    st.warning("No data available for the selected country.")
    st.stop()

#-------------------- CARD---------------------------------#
global_avg_price = df["TypicalPrice(USD)"].mean()
st.metric(label="🌍 Global Average Street-Food Price (USD)",
          value=f"{global_avg_price:.2f}")

#-------------------BAR: MOST EXPENSIVE CITIES-------------------#
st.subheader("Most Expensive Cities for Street Food")
avg_price_by_city = (filtered_df
                     .groupby("Region/City")["TypicalPrice(USD)"]
                     .mean()
                     .sort_values(ascending=False))

fig_city = px.bar(x=avg_price_by_city.index,
                  y=avg_price_by_city.values,
                  labels={"x": "City", "y": "Average Price (USD)"},
                  title="Top Cities by Street-Food Cost",
                  color_discrete_sequence=["#2a90b5"],
                  text=avg_price_by_city.values.round(2))
fig_city.update_traces(textposition="outside")
st.plotly_chart(fig_city, use_container_width=True)

#---------------------- TWO-COLUMN SECTION-----------------------#
left_col, right_col = st.columns(2)

# ------- LEFT: Veg vs Non-Veg price comparison ------- #
with left_col:
    st.subheader("Average Price by Dish Type")

    filtered_df["DishType"] = np.where(filtered_df["Vegetarian"].astype(int) == 1,
                                       "Vegetarian", "Non-Vegetarian")

    avg_price_by_dish = (filtered_df
                         .groupby("DishType")["TypicalPrice(USD)"]
                         .mean()
                         .reset_index(name="Average Price (USD)"))

    fig_dish = px.bar(avg_price_by_dish,
                      x="DishType", y="Average Price (USD)",
                      color="DishType",
                      color_discrete_sequence=["#005b7d", "#52b4d9"],
                      title="Average Street-Food Price: Vegetarian vs Non-Vegetarian",
                      text=avg_price_by_dish["Average Price (USD)"].round(2),
                      category_orders={"DishType": ["Vegetarian", "Non-Vegetarian"]})
    fig_dish.update_xaxes(type="category")
    fig_dish.update_traces(textposition="outside", width=0.5)
    st.plotly_chart(fig_dish, use_container_width=True)

    st.markdown("**Fun fact:** vegetarian street food is *slightly* more expensive on average!")

# ------- RIGHT: Cooking-method pie ------- #
with right_col:
    st.subheader("Cooking Style Breakdown")

    cooking_counts = filtered_df["CookingMethod"].value_counts()
    fig_cook = px.pie(values=cooking_counts.values,
                      names=cooking_counts.index,
                      title="Street Food by Cooking Style",
                      color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_cook, use_container_width=True)

# ---------------Violin + embedded box + points---------------#
violin_df = filtered_df.copy()
violin_df["DishType"] = np.where(
    violin_df["Vegetarian"].astype(int) == 1,
    "Vegetarian", "Non-Vegetarian"
)

fig_violin = px.violin(
    violin_df,
    x="IngredientCount",
    y="TypicalPrice(USD)",
    color="DishType",
    box=True,             # draw a mini-boxplot inside
    points="all",         # show every dish as a dot
    hover_data=["DishName", "Country"],
    labels={"IngredientCount": "# Ingredients",
            "TypicalPrice(USD)": "Price (USD)"},
    title="Price Distribution by Ingredient Count")

fig_violin.update_traces(meanline_visible=True)  # add dashed mean line
st.plotly_chart(fig_violin, use_container_width=True)

# ------------------- Choropleth Map ----------------------- #
st.subheader("Global Street-Food Prices at a Glance")

avg_price_country = (df.groupby("Country")["TypicalPrice(USD)"]
                     .mean()
                     .reset_index(name="AveragePriceUSD"))

fig_map = px.choropleth(avg_price_country,
                        locations="Country",
                        locationmode="country names",
                        color="AveragePriceUSD",
                        color_continuous_scale=px.colors.sequential.Tealgrn,
                        title="Average Street-Food Price by Country (USD)",
                        labels={"AveragePriceUSD": "Avg Price (USD)"})
fig_map.update_geos(showcoastlines=False, showcountries=True)
st.plotly_chart(fig_map, use_container_width=True)
st.caption("Data source: Kaggle Global Street-Food Dataset · Dashboard built with Streamlit & Plotly")
