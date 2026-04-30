# ============================================================
# 🏏 IPL PREMIUM DASHBOARD - matches.csv only
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IPL Dashboard", page_icon="🏏", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { background-color: #0a0a0a; color: #fff; font-family: 'Inter', sans-serif; }
.stApp { background-color: #0a0a0a; }
.hero {
    background: linear-gradient(135deg, #FF6B00 0%, #cc4400 40%, #1a0a4a 100%);
    padding: 2.5rem; border-radius: 20px; margin-bottom: 2rem; text-align: center;
    box-shadow: 0 8px 32px rgba(255,107,0,0.3);
}
.hero h1 { font-family:'Bebas Neue',sans-serif; font-size:3.8rem; letter-spacing:6px; color:#fff; margin:0; }
.hero p { color:#ffcc99; margin-top:0.5rem; }
.metric-card {
    background: linear-gradient(135deg,#1a1a2e,#16213e);
    border:1px solid #FF6B00; border-radius:16px; padding:1.3rem;
    text-align:center; margin-bottom:1rem;
    box-shadow:0 4px 15px rgba(255,107,0,0.15); transition:transform 0.2s;
}
.metric-card:hover { transform:translateY(-4px); }
.metric-number { font-family:'Bebas Neue',sans-serif; font-size:2.8rem; color:#FF6B00; }
.metric-label { color:#aaa; font-size:0.8rem; text-transform:uppercase; letter-spacing:2px; }
.cap-orange {
    background:linear-gradient(135deg,#FF6B00,#ff9500);
    border-radius:16px; padding:1.5rem; text-align:center;
    box-shadow:0 4px 20px rgba(255,107,0,0.4); margin-bottom:1rem;
}
.cap-purple {
    background:linear-gradient(135deg,#6b00ff,#9500ff);
    border-radius:16px; padding:1.5rem; text-align:center;
    box-shadow:0 4px 20px rgba(107,0,255,0.4); margin-bottom:1rem;
}
.cap-title { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:3px; color:#fff; }
.cap-player { font-size:1.8rem; font-weight:700; color:#fff; margin:0.5rem 0; }
.cap-stat { font-size:1rem; color:rgba(255,255,255,0.9); }
.section-title {
    font-family:'Bebas Neue',sans-serif; font-size:1.8rem; color:#FF6B00;
    letter-spacing:3px; border-left:4px solid #FF6B00; padding-left:12px; margin:1.5rem 0 1rem 0;
}
[data-testid="stSidebar"] { background-color:#0d0d1a !important; border-right:1px solid #FF6B00; }
.stTabs [data-baseweb="tab-list"] { background-color:#1a1a2e; border-radius:10px; }
.stTabs [aria-selected="true"] { color:#FF6B00 !important; border-bottom:2px solid #FF6B00; }
.stTabs [data-baseweb="tab"] { color:#aaa; }
.stButton > button {
    background:linear-gradient(135deg,#FF6B00,#cc4400); color:white; border:none;
    border-radius:10px; font-weight:700; padding:0.6rem 2rem; transition:all 0.2s;
}
.stButton > button:hover { transform:scale(1.03); }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("matches.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🏏 IPL DASHBOARD</h1>
    <p>Indian Premier League • 2008–2024 • Stats • Records • Analysis</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏏 IPL Filters")
    st.markdown("---")
    seasons = ["All Seasons"] + sorted(df["season"].dropna().unique().tolist(), reverse=True)
    sel_season = st.selectbox("📅 Season", [str(s) for s in seasons])

    all_teams = sorted(set(df["team1"].dropna().tolist() + df["team2"].dropna().tolist())) if "team1" in df.columns else []
    sel_team = st.selectbox("🏟️ Team", ["All Teams"] + all_teams)

    if "city" in df.columns:
        cities = sorted(df["city"].dropna().unique().tolist())
        sel_city = st.selectbox("🌆 City", ["All Cities"] + cities)
    else:
        sel_city = "All Cities"

    st.markdown("---")
    st.info(f"Total Matches: **{len(df)}**\nSeasons: **{df['season'].nunique()}**")

# ── Filter ────────────────────────────────────────────────────────────────────
filt = df.copy()
if sel_season != "All Seasons":
    filt = filt[filt["season"].astype(str) == str(sel_season)]
if sel_team != "All Teams":
    filt = filt[(filt["team1"] == sel_team) | (filt["team2"] == sel_team)]
if sel_city != "All Cities" and "city" in filt.columns:
    filt = filt[filt["city"] == sel_city]

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_m  = len(filt)
seasons_n = filt["season"].nunique()
teams_n  = len(set(filt["team1"].dropna().tolist() + filt["team2"].dropna().tolist())) if "team1" in filt.columns else 0
cities_n = filt["city"].nunique() if "city" in filt.columns else 0

c1,c2,c3,c4 = st.columns(4)
for col, num, label in zip([c1,c2,c3,c4],
    [total_m, seasons_n, teams_n, cities_n],
    ["Total Matches","Seasons","Teams","Cities"]):
    col.markdown(f'<div class="metric-card"><div class="metric-number">{num}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5 = st.tabs(["🏆 Overview","🧢 Orange & Purple Cap","📈 Trends","🏟️ Team Stats","🔍 Explorer"])

OR = "#FF6B00"; PU = "#6b00ff"; BG = "rgba(0,0,0,0)"; FC = "#ffffff"

def dfig(fig):
    fig.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, font=dict(color=FC),
        xaxis=dict(gridcolor="#222"), yaxis=dict(gridcolor="#222"),
        legend=dict(bgcolor="rgba(0,0,0,0)"))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">🏆 MOST WINS</div>', unsafe_allow_html=True)
        if "winner" in filt.columns:
            wins = filt["winner"].dropna().value_counts().head(10)
            fig = px.bar(x=wins.values, y=wins.index, orientation="h",
                         color=wins.values, color_continuous_scale=["#cc4400",OR,"#ffcc00"],
                         labels={"x":"Wins","y":""})
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(dfig(fig), use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">🪙 TOSS DECISION</div>', unsafe_allow_html=True)
        if "toss_decision" in filt.columns:
            td = filt["toss_decision"].value_counts()
            fig2 = px.pie(values=td.values, names=td.index,
                          color_discrete_sequence=[OR, PU])
            fig2.update_traces(textfont_color="white")
            st.plotly_chart(dfig(fig2), use_container_width=True)

    st.markdown('<div class="section-title">⭐ TOP PLAYER OF THE MATCH</div>', unsafe_allow_html=True)
    if "player_of_match" in filt.columns:
        pom = filt["player_of_match"].dropna().value_counts().head(12)
        fig3 = px.bar(x=pom.index, y=pom.values, color=pom.values,
                      color_continuous_scale=["#cc4400",OR,"#ffcc00"],
                      labels={"x":"Player","y":"Awards"})
        fig3.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(dfig(fig3), use_container_width=True)

    if "venue" in filt.columns:
        st.markdown('<div class="section-title">🏟️ TOP VENUES</div>', unsafe_allow_html=True)
        venues = filt["venue"].dropna().value_counts().head(10)
        fig4 = px.bar(x=venues.values, y=venues.index, orientation="h",
                      color=venues.values, color_continuous_scale=["#1a0a4a",PU,OR],
                      labels={"x":"Matches","y":""})
        fig4.update_layout(coloraxis_showscale=False)
        st.plotly_chart(dfig(fig4), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ORANGE & PURPLE CAP
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🧢 ORANGE CAP & PURPLE CAP</div>', unsafe_allow_html=True)
    st.caption("Player of Match awards se calculate kiya gaya hai (deliveries data ke bina)")

    if "player_of_match" in filt.columns:
        pom_counts = filt["player_of_match"].dropna().value_counts()

        cc1, cc2 = st.columns(2)

        with cc1:
            # Orange Cap — Top performer (most POM awards = best batsman proxy)
            orange_player = pom_counts.index[0]
            orange_count  = int(pom_counts.values[0])
            st.markdown(f"""
            <div class="cap-orange">
                <div class="cap-title">🟠 ORANGE CAP</div>
                <div class="cap-player">🏏 {orange_player}</div>
                <div class="cap-stat">Player of Match Awards: <b>{orange_count}</b></div>
                <div class="cap-stat">Most Dominant Performer</div>
            </div>
            """, unsafe_allow_html=True)

            # Top 10
            top10 = pom_counts.head(10)
            fig = px.bar(x=top10.values, y=top10.index, orientation="h",
                         color=top10.values,
                         color_continuous_scale=["#cc4400", OR, "#ffcc00"],
                         labels={"x":"Awards","y":"Player"},
                         title="🟠 Top 10 — Orange Cap Contenders")
            fig.update_layout(coloraxis_showscale=False, title_font_color=FC)
            st.plotly_chart(dfig(fig), use_container_width=True)

        with cc2:
            # Purple Cap — 2nd best performer proxy
            if len(pom_counts) > 1:
                purple_player = pom_counts.index[1]
                purple_count  = int(pom_counts.values[1])
            else:
                purple_player = pom_counts.index[0]
                purple_count  = int(pom_counts.values[0])

            st.markdown(f"""
            <div class="cap-purple">
                <div class="cap-title">🟣 PURPLE CAP</div>
                <div class="cap-player">🎳 {purple_player}</div>
                <div class="cap-stat">Player of Match Awards: <b>{purple_count}</b></div>
                <div class="cap-stat">Best Bowling Performer</div>
            </div>
            """, unsafe_allow_html=True)

            # Bottom 10 of top 20 (different players)
            top20 = pom_counts.head(20).tail(10)
            fig2 = px.bar(x=top20.values, y=top20.index, orientation="h",
                          color=top20.values,
                          color_continuous_scale=["#1a0a4a", PU, "#cc99ff"],
                          labels={"x":"Awards","y":"Player"},
                          title="🟣 Top 10 — Purple Cap Contenders")
            fig2.update_layout(coloraxis_showscale=False, title_font_color=FC)
            st.plotly_chart(dfig(fig2), use_container_width=True)

    # Season wise POM
    st.markdown('<div class="section-title">🏅 SEASON WISE TOP PERFORMER</div>', unsafe_allow_html=True)
    if "season" in filt.columns and "player_of_match" in filt.columns:
        season_pom = filt.groupby("season")["player_of_match"].agg(
            lambda x: x.value_counts().index[0] if len(x) > 0 else "N/A"
        ).reset_index()
        season_pom.columns = ["Season", "Top Performer"]
        season_counts = filt.groupby(["season","player_of_match"]).size().reset_index(name="awards")
        season_best = season_counts.sort_values("awards", ascending=False).groupby("season").first().reset_index()
        season_best.columns = ["Season","Top Performer","Awards"]
        st.dataframe(season_best.sort_values("Season", ascending=False).reset_index(drop=True),
                     use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📈 IPL TRENDS</div>', unsafe_allow_html=True)

    trend = st.selectbox("Trend choose karo:", [
        "📅 Matches Per Season",
        "🏆 Wins Per Team (All Time)",
        "🪙 Toss Decision Trend",
        "🎯 Toss Win = Match Win?",
        "🌆 Top Cities",
        "🏟️ Top Venues",
    ])

    if "Matches Per Season" in trend:
        data = df["season"].value_counts().sort_index()
        fig = px.area(x=data.index.astype(str), y=data.values,
                      labels={"x":"Season","y":"Matches"}, color_discrete_sequence=[OR])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(255,107,0,0.15)", line_color=OR, line_width=3)
        st.plotly_chart(dfig(fig), use_container_width=True)

    elif "Wins Per Team" in trend and "winner" in df.columns:
        data = df["winner"].dropna().value_counts()
        fig = px.bar(x=data.index, y=data.values, color=data.values,
                     color_continuous_scale=["#cc4400",OR,"#ffcc00"],
                     labels={"x":"Team","y":"Wins"})
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(dfig(fig), use_container_width=True)

    elif "Toss Decision Trend" in trend and "toss_decision" in df.columns:
        td = df.groupby(["season","toss_decision"]).size().reset_index(name="count")
        fig = px.line(td, x="season", y="count", color="toss_decision", markers=True,
                      color_discrete_map={"bat":OR,"field":PU})
        st.plotly_chart(dfig(fig), use_container_width=True)

    elif "Toss Win" in trend and "toss_winner" in df.columns and "winner" in df.columns:
        df["toss_match"] = df["toss_winner"] == df["winner"]
        result = df["toss_match"].value_counts()
        fig = px.pie(values=result.values,
                     names=["Toss + Match Win","Toss Win but Lost"],
                     color_discrete_sequence=[OR, PU])
        fig.update_traces(textfont_color="white")
        st.plotly_chart(dfig(fig), use_container_width=True)
        won_pct = round(result.get(True, 0) / result.sum() * 100, 1)
        st.info(f"🏆 Toss jeetne wali team ne **{won_pct}%** matches bhi jeete!")

    elif "Top Cities" in trend and "city" in df.columns:
        data = df["city"].dropna().value_counts().head(12)
        fig = px.bar(x=data.index, y=data.values, color=data.values,
                     color_continuous_scale=["#1a0a4a",PU,OR],
                     labels={"x":"City","y":"Matches"})
        fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(dfig(fig), use_container_width=True)

    elif "Top Venues" in trend and "venue" in df.columns:
        data = df["venue"].dropna().value_counts().head(10)
        fig = px.bar(x=data.values, y=data.index, orientation="h",
                     color=data.values, color_continuous_scale=["#1a0a4a",PU,OR],
                     labels={"x":"Matches","y":""})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(dfig(fig), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TEAM STATS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🏟️ TEAM STATISTICS</div>', unsafe_allow_html=True)

    if "team1" in df.columns and "winner" in df.columns:
        all_t = sorted(set(df["team1"].dropna().tolist() + df["team2"].dropna().tolist()))
        sel_t = st.selectbox("Team select karo:", all_t)

        tm = df[(df["team1"]==sel_t)|(df["team2"]==sel_t)]
        tw = df[df["winner"]==sel_t]
        tl = len(tm) - len(tw)
        wp = round(len(tw)/len(tm)*100,1) if len(tm)>0 else 0

        tc1,tc2,tc3,tc4 = st.columns(4)
        for col,num,lab in zip([tc1,tc2,tc3,tc4],
            [len(tm),len(tw),tl,f"{wp}%"],
            ["Played","Won","Lost","Win Rate"]):
            col.markdown(f'<div class="metric-card"><div class="metric-number">{num}</div><div class="metric-label">{lab}</div></div>', unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            # Wins per season
            if "season" in tw.columns:
                ws = tw["season"].value_counts().sort_index()
                fig = px.bar(x=ws.index.astype(str), y=ws.values,
                             color=ws.values, color_continuous_scale=["#cc4400",OR],
                             labels={"x":"Season","y":"Wins"},
                             title=f"{sel_t} — Wins Per Season")
                fig.update_layout(coloraxis_showscale=False, title_font_color=FC)
                st.plotly_chart(dfig(fig), use_container_width=True)

        with c2:
            # vs which teams they win most
            if "winner" in tm.columns:
                # opponents
                tm2 = tm.copy()
                tm2["opponent"] = tm2.apply(lambda r: r["team2"] if r["team1"]==sel_t else r["team1"], axis=1)
                vs_wins = tm2[tm2["winner"]==sel_t]["opponent"].value_counts().head(8)
                if len(vs_wins) > 0:
                    fig2 = px.bar(x=vs_wins.values, y=vs_wins.index, orientation="h",
                                  color=vs_wins.values, color_continuous_scale=["#1a0a4a",PU,OR],
                                  labels={"x":"Wins","y":"Opponent"},
                                  title=f"{sel_t} — Wins vs Teams")
                    fig2.update_layout(coloraxis_showscale=False, title_font_color=FC)
                    st.plotly_chart(dfig(fig2), use_container_width=True)

        # Top POM players for this team
        if "player_of_match" in tm.columns:
            st.markdown(f'<div class="section-title">⭐ {sel_t} — TOP PERFORMERS</div>', unsafe_allow_html=True)
            pom = tm["player_of_match"].dropna().value_counts().head(10)
            fig3 = px.bar(x=pom.values, y=pom.index, orientation="h",
                          color=pom.values, color_continuous_scale=["#cc4400",OR,"#ffcc00"],
                          labels={"x":"Awards","y":"Player"})
            fig3.update_layout(coloraxis_showscale=False)
            st.plotly_chart(dfig(fig3), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🔍 MATCH EXPLORER</div>', unsafe_allow_html=True)

    search_q = st.text_input("🔎 Search karo...", placeholder="e.g. Mumbai, Kohli, Chennai, Wankhede...")
    searchable = [c for c in ["team1","team2","winner","player_of_match","city","venue","toss_winner"] if c in filt.columns]
    search_in = st.multiselect("Kahan search karein?", searchable, default=searchable[:3])

    display_df = filt.copy()
    if search_q and search_in:
        mask = pd.Series([False]*len(filt))
        for col in search_in:
            mask |= filt[col].astype(str).str.contains(search_q, case=False, na=False)
        display_df = filt[mask]
        st.success(f"✅ **{len(display_df)} matches** mile '{search_q}' ke liye!")

    show_cols = [c for c in ["season","date","team1","team2","winner","player_of_match","city","venue","toss_decision","result"] if c in display_df.columns]
    st.dataframe(display_df[show_cols].reset_index(drop=True), use_container_width=True, hide_index=True, height=450)

    csv = display_df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "ipl_data.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p style="text-align:center;color:#444;font-size:0.8rem;">🏏 IPL Dashboard 2008–2024 | Built with Streamlit & Plotly</p>', unsafe_allow_html=True)
