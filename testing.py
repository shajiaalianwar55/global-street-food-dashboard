import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load your data
df = pd.read_csv("global_street_food_cleaned.csv")

st.title("📊 Interactive vs Static Charts Demo")

col1, col2 = st.columns(2)

# 👉 Seaborn static chart (left column)
with col1:
    st.subheader("Seaborn (Static)")
    fig1, ax = plt.subplots()
    sns.barplot(x="Country", y="TypicalPrice(USD)", data=df, ax=ax)
    plt.xticks(rotation=90)
    st.pyplot(fig1)

# 👉 Plotly interactive chart (right column)
with col2:
    st.subheader("Plotly (Interactive)")
    fig2 = px.bar(df, x="Country", y="TypicalPrice(USD)", title="Interactive Bar Chart")
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2)

    import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

df = pd.read_csv("global_street_food_cleaned.csv")

st.subheader("🎻 Violin Plot: Price Distribution by Region")

fig, ax = plt.subplots(figsize=(10, 5))
sns.violinplot(x="Region/City", y="TypicalPrice(USD)", data=df, ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

