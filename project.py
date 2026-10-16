import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff


st.set_page_config(
    page_title="🏏 IPL 2025 PLAYER PERFORMANCE DASHBOARD",
    page_icon="🏏",
    layout="wide"
    
)


@st.cache_data
def load_data():
    return pd.read_csv("IPL2025Batters.csv")


df = load_data()

numeric_cols = [
    "Runs", "AVG", "SR", "Inn", "Matches",
    "100s", "50s", "4s", "6s"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


df["HS_Num"] = (
    df["HS"]
    .astype(str)
    .str.replace("*", "", regex=False)
)

df["HS_Num"] = pd.to_numeric(
    df["HS_Num"],
    errors="coerce"
)


st.sidebar.title("🎯 Filters")


all_team_list = sorted(df["Team"].dropna().unique())
teams = ["All"] + all_team_list

selected_team = st.sidebar.selectbox(
    "Select Team",
    teams
)


all_player_list = sorted(df["Player Name"].dropna().unique())
players = ["All"] + all_player_list

selected_player = st.sidebar.selectbox(
    "Select Player",
    players
)


compare_players = st.sidebar.multiselect(
    "Compare Players",
    all_player_list,
    default=all_player_list[:2] if len(all_player_list) >= 2 else all_player_list
)

compare_teams = st.sidebar.multiselect(
    "Compare Teams",
    all_team_list,
    default=all_team_list[:2] if len(all_team_list) >= 2 else all_team_list
)


min_runs = st.sidebar.slider(
    "Minimum Runs",
    0,
    int(df["Runs"].max()),
    100
)



min_avg = st.sidebar.slider(
    "Minimum Average",
    0.0,
    float(df["AVG"].max()),
    20.0
)


min_sr = st.sidebar.slider(
    "Minimum Strike Rate",
    0.0,
    float(df["SR"].max()),
    120.0
)



search = st.sidebar.text_input(
    "🔍 Search Player"
)



filtered_df = df.copy()


filtered_df = filtered_df[
    (filtered_df["Runs"] >= min_runs) &
    (filtered_df["AVG"] >= min_avg) &
    (filtered_df["SR"] >= min_sr)
]


if selected_team != "All":
    filtered_df = filtered_df[
        filtered_df["Team"] == selected_team
    ]


if selected_player != "All":
    filtered_df = filtered_df[
        filtered_df["Player Name"] == selected_player
    ]


if search:
    filtered_df = filtered_df[
        filtered_df["Player Name"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]


if filtered_df.empty:
    st.warning("No players match your filters.")
    st.stop()



st.title(
    "🏏 IPL 2025 PLAYER PERFORMANCE DASHBOARD"
)

st.markdown(
    " INTERACTIVE ANALYSIS OF IPL 2025 PLAYERS"
)

st.divider()



c1, c2, c3, c4, c5, c6 = st.columns(6)


c1.metric(
    "Players",
    len(filtered_df)
)

c2.metric(
    "Total Runs",
    int(filtered_df["Runs"].sum())
)

c3.metric(
    "Highest Score",
    int(filtered_df["HS_Num"].max())
)

c4.metric(
    "Avg Runs",
    round(filtered_df["Runs"].mean(),1)
)

c5.metric(
    "Avg Strike Rate",
    round(filtered_df["SR"].mean(),1)
)

c6.metric(
    "Total Sixes",
    int(filtered_df["6s"].sum())
)


st.divider()



col1, col2 = st.columns(2)


with col1:

    top10 = filtered_df.nlargest(
        10,
        "Runs"
    )


    fig = px.bar(
        top10,
        x="Runs",
        y="Player Name",
        color="Team",
        orientation="h",
        text="Runs",
        title="🏆 Top 10 Run Scorers",
        template="plotly_white"
    )

    fig.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    fig2 = px.scatter(
        filtered_df,
        x="SR",
        y="AVG",
        size="Runs",
        color="Team",
        hover_name="Player Name",
        title="Strike Rate vs Average",
        template="plotly_white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )




col3, col4 = st.columns(2)


with col3:

    six_hitters = filtered_df.nlargest(
        10,
        "6s"
    )


    fig3 = px.bar(
        six_hitters,
        x="Player Name",
        y="6s",
        color="Team",
        title="💥 Top Six Hitters",
        template="plotly_white"
    )


    st.plotly_chart(
        fig3,
        use_container_width=True
    )


with col4:

    fig4 = px.scatter(
        filtered_df,
        x="Runs",
        y="6s",
        size="SR",
        color="Team",
        hover_name="Player Name",
        title="Runs vs Sixes",
        template="plotly_white"
    )


    st.plotly_chart(
        fig4,
        use_container_width=True
    )


st.divider()


st.subheader("⚖️ PLAYER & TEAM COMPARISON")

comparison_metric = st.selectbox(
    "Choose Comparison Metric",
    ["Runs", "AVG", "SR", "6s"],
    index=0
)

compare_col1, compare_col2 = st.columns(2)

with compare_col1:
    if compare_players:
        player_compare_df = (
            filtered_df[
                filtered_df["Player Name"].isin(compare_players)
            ][
                ["Player Name", "Team", "Runs", "AVG", "SR", "Matches", "100s", "50s", "4s", "6s"]
            ]
            .sort_values(comparison_metric, ascending=False)
        )

        st.subheader("🏏 Player Comparison")
        st.dataframe(player_compare_df, use_container_width=True, hide_index=True)

        player_fig = px.bar(
            player_compare_df,
            x="Player Name",
            y=comparison_metric,
            color="Team",
            text=comparison_metric,
            title=f"Player Comparison by {comparison_metric}",
            template="plotly_white"
        )

        st.plotly_chart(player_fig, use_container_width=True)
    else:
        st.info("Select one or more players from the sidebar to compare performance.")

with compare_col2:
    if compare_teams:
        team_compare_df = (
            filtered_df[
                filtered_df["Team"].isin(compare_teams)
            ]
            .groupby("Team")
            .agg(
                Total_Runs=("Runs", "sum"),
                Avg=("AVG", "mean"),
                SR=("SR", "mean"),
                Sixes=("6s", "sum"),
                Players=("Player Name", "nunique")
            )
            .sort_values("Total_Runs", ascending=False)
            .reset_index()
        )

        st.subheader("🏟️ Team Comparison")
        st.dataframe(team_compare_df, use_container_width=True, hide_index=True)

        team_fig = px.bar(
            team_compare_df,
            x="Team",
            y="Total_Runs",
            color="Team",
            text="Total_Runs",
            title="Team Comparison by Total Runs",
            template="plotly_white"
        )

        st.plotly_chart(team_fig, use_container_width=True)
    else:
        st.info("Select one or more teams from the sidebar to compare team totals.")

st.divider()


st.subheader("🏆 TEAM LEADERBOARD")


team_stats = (
    filtered_df
    .groupby("Team")
    .agg(
        Total_Runs=("Runs","sum"),
        Avg=("AVG","mean"),
        SR=("SR","mean")
    )
    .sort_values(
        "Total_Runs",
        ascending=False
    )
)


st.dataframe(
    team_stats,
    use_container_width=True
)




st.subheader("🥇 PLAYER RANKING")


ranking = filtered_df.copy()


ranking["Rank"] = (
    ranking["Runs"]
    .rank(
        method="dense",
        ascending=False
    )
    .astype(int)
)


st.dataframe(
    ranking[
        [
            "Rank",
            "Player Name",
            "Team",
            "Runs",
            "AVG",
            "SR"
        ]
    ]
    .sort_values("Rank"),
    use_container_width=True,
    hide_index=True
)




st.subheader("📊 PERFORMANCE CORRELATION")


corr = filtered_df[
    [
        "Runs",
        "AVG",
        "SR",
        "4s",
        "6s"
    ]
].corr()    


fig5 = ff.create_annotated_heatmap(
    corr.values,
    x=list(corr.columns),
    y=list(corr.columns),
    colorscale="Viridis"
)


st.plotly_chart(
    fig5,
    use_container_width=True
)


st.divider()



st.subheader(
    "🔍 PLAYER SCORECARD"
)


player_list = sorted(
    filtered_df["Player Name"].unique()
)


selected = st.selectbox(
    "Choose Player",
    player_list
)


player = filtered_df[
    filtered_df["Player Name"] == selected
].iloc[0]


a,b,c,d = st.columns(4)


a.metric(
    "Team",
    player["Team"]
)

b.metric(
    "Matches",
    player["Matches"]
)

c.metric(
    "Runs",
    int(player["Runs"])
)

d.metric(
    "Highest Score",
    player["HS"]
)


a,b,c,d = st.columns(4)


a.metric(
    "Average",
    round(player["AVG"],2)
)

b.metric(
    "Strike Rate",
    round(player["SR"],2)
)

c.metric(
    "50s / 100s",
    f"{int(player['50s'])}/{int(player['100s'])}"
)

d.metric(
    "4s / 6s",
    f"{int(player['4s'])}/{int(player['6s'])}"
)


st.divider()




st.subheader(
    "📋 DATASET EXPLORER   "
)


st.dataframe(
    filtered_df.sort_values(
        "Runs",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


with st.expander(
    "View Complete Dataset"
):
    st.dataframe(
        df,
        use_container_width=True
    )




csv = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    "📥 Download Filtered Dataset",
    csv,
    "IPL2025_Filtered_Data.csv",
    "text/csv"
)


st.sidebar.success(
    f"Players Found: {len(filtered_df)}"
)


st.markdown(" ")

st.caption(
    "🏏 IPL 2025 PLAYER PERFORMANCE DASHBOARD | Built with Streamlit & Plotly"
     
)



