import streamlit as st

import plotly.express as px

from src.dashboard.utils.db import *

st.title("Peer Comparison")

peer = get_peers()

group = st.selectbox(

    "Peer Group",

    sorted(
        peer["peer_group_name"].dropna().unique()
    )

)

df = peer[
    peer["peer_group_name"]==group
]

st.dataframe(df)

fig = px.bar(

    df,

    x="company_id",

    y="percentile_rank"

)

st.plotly_chart(
    fig,
    use_container_width=True
)