import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import get_peers

st.title("Peer Comparison")

peer = get_peers()

if peer.empty or "peer_group_name" not in peer.columns:

    st.info("Peer percentiles have not been built yet: the peer_groups table has no data.")

    st.stop()

group = st.selectbox(

    "Peer Group",

    sorted(peer["peer_group_name"].dropna().unique())

)

df = peer[peer["peer_group_name"] == group]

st.dataframe(df)

st.plotly_chart(

    px.bar(df, x="company_id", y="percentile_rank", color="metric", barmode="group"),

    width="stretch"

)
