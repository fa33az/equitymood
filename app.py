import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from feed_parser import fetch_feed_data
from sentiment_analyzer import analyze_sentiment
from market_data import fetch_realtime_price
import re

# Import templates and SVG assets
from templates import (
    SVG_NEWSPAPER, SVG_GAUGE, SVG_TREND_UP, SVG_TREND_DOWN, SVG_LIVE, SVG_OFFLINE,
    get_header_html, TICKER_TAPE_HTML, get_market_bar_html
)

# Set page configurations
st.set_page_config(
    page_title="EquityMood Stock Sentiment Analytics",
    page_icon="https://img.icons8.com/external-flat-icons-inspirational-tuts/64/external-stock-market-business-and-finance-flat-icons-inspirational-tuts.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "search_query" not in st.session_state:
    st.session_state.search_query = "IHSG"

# Load external style.css
try:
    with open("style.css", "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except Exception:
    pass

# Sidebar - Settings Panel
st.sidebar.markdown("### NAVIGASI", unsafe_allow_html=True)

# Main Navigation
active_view = st.sidebar.radio(
    "Pilih Halaman:",
    options=["Dashboard", "Perbandingan", "Log Berita"],
    help="Pindah tab visualisasi sentimen."
)

st.sidebar.markdown("---")

# Ticker/Stock input
sidebar_query = st.sidebar.text_input(
    "Kode Emiten / Kata Kunci:",
    value=st.session_state.search_query,
    help="Masukkan kode emiten (contoh: BBRI, TLKM, GOTO) atau kata kunci 'IHSG'"
)

if sidebar_query != st.session_state.search_query:
    st.session_state.search_query = sidebar_query
    st.rerun()

# Model Toggle
use_hf = st.sidebar.checkbox(
    "Gunakan Model IndoBERT",
    value=False,
    help="Gunakan model deep learning IndoBERT dari Hugging Face untuk akurasi optimal."
)

# Auto-Refresh Setting
st.sidebar.markdown("**Auto-Refresh**")
auto_refresh = st.sidebar.checkbox("Aktifkan Auto-Refresh", value=False)
refresh_interval = 60  # default fallback
if auto_refresh:
    refresh_interval = st.sidebar.selectbox("Interval", [60, 120, 300, 600], format_func=lambda x: f"{x // 60} menit")
    st.sidebar.caption(f"Halaman akan refresh otomatis tiap {refresh_interval // 60} menit.")

# Sync Button to clear cache
if st.sidebar.button("Sinkronkan Data Baru", use_container_width=True, type="secondary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### SUMBER FEED")
st.sidebar.info("""
Memantau 14 portal berita finansial:
- CNBC Indonesia (News, Market, Investment)
- Kontan (News, Investasi, Makro)
- Bisnis Indonesia
- Detik Finance
- Liputan6 Bisnis
- Kompas Money
- Okezone, Sindonews, Republika, Tempo
""")

# Fetch news data and real-time market data with a modern loading spinner
with st.spinner(f"Menghubungkan ke API Feeds & Mengambil Harga Real-time '{st.session_state.search_query.upper()}'..."):
    articles = fetch_feed_data(st.session_state.search_query, use_fallback=True)
    mkt_data = fetch_realtime_price(st.session_state.search_query)
is_simulated = all(art.get("source", "").endswith("Sim") for art in articles) if articles else True

# Live connection status
if is_simulated:
    status_badge = f'<span class="badge badge-neutral">{SVG_OFFLINE} Mode Simulasi (Offline)</span>'
else:
    status_badge = f'<span class="badge badge-positive" style="background-color:#022c22; color:#4ade80; border-color:#064e3b;">{SVG_LIVE} Live RSS Feeds (Online)</span>'

# Header Component
st.markdown(get_header_html(status_badge), unsafe_allow_html=True)

# Ticker Tape
st.markdown(TICKER_TAPE_HTML, unsafe_allow_html=True)

# Ticker Select Section
st.write("Pilih Ticker Cepat:")
col_tags = st.columns(8)
quick_tickers = ["IHSG", "BBRI", "TLKM", "GOTO", "BMRI", "BBNI", "ASII", "UNVR"]
for i, ticker in enumerate(quick_tickers):
    btn_type = "primary" if st.session_state.search_query == ticker else "secondary"
    if col_tags[i].button(ticker, key=f"quick_btn_{ticker}", use_container_width=True, type=btn_type):
        st.session_state.search_query = ticker
        st.rerun()

if not articles:
    st.warning("Tidak ditemukan data berita terbaru. Silakan masukkan kata kunci lainnya.")
else:
    # Process sentiment labels
    data = []
    for art in articles:
        text_to_analyze = f"{art['title']}. {art['summary']}"
        label, score = analyze_sentiment(text_to_analyze, use_hf=use_hf)
        
        data.append({
            "Waktu": art["published"],
            "Sumber": art["source"],
            "Judul Berita": art["title"],
            "Deskripsi": art["summary"],
            "Sentimen": label,
            "Skor": score,
            "Link": art["link"]
        })
    
    df = pd.DataFrame(data)
    df['Datetime'] = pd.to_datetime(df['Waktu'], errors='coerce')
    df_sorted = df.dropna(subset=['Datetime']).sort_values('Datetime')

    st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)

    # Route content based on selected view
    if active_view == "Dashboard":
        # Metric calculation
        total_articles = len(df)
        positive_count = sum(df["Sentimen"] == "POSITIVE")
        negative_count = sum(df["Sentimen"] == "NEGATIVE")
        neutral_count = sum(df["Sentimen"] == "NEUTRAL")
        
        numeric_sentiments = df["Sentimen"].map({"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0})
        avg_score = numeric_sentiments.mean()
        
        sentiment_text = "Netral"
        sentiment_color = "#cbd5e1"
        if avg_score > 0.15:
            sentiment_text = "Positif"
            sentiment_color = "#4ade80"
        elif avg_score < -0.15:
            sentiment_text = "Negatif"
            sentiment_color = "#fca5a5"
            
        if mkt_data:
            # Let's display real-time stock price metrics
            price_color = "#4ade80" if mkt_data['change_val'] >= 0 else "#fca5a5"
            arrow = "▲" if mkt_data['change_val'] >= 0 else "▼"
            
            st.markdown(get_market_bar_html(
                st.session_state.search_query,
                mkt_data['symbol'],
                mkt_data['price'],
                mkt_data['change_val'],
                mkt_data['change_pct'],
                mkt_data['high'],
                mkt_data['low'],
                mkt_data['volume'],
                price_color,
                arrow
            ), unsafe_allow_html=True)
            
            # Candlestick OHLCV chart
            st.subheader("Candlestick Chart Harga Saham (5 Hari Terakhir)")
            hist_df = mkt_data['history'].reset_index()
            # Handle Datetime conversion safely
            dt_col = 'Datetime' if 'Datetime' in hist_df.columns else 'Date'
            hist_df[dt_col] = hist_df[dt_col].dt.tz_localize(None) if hasattr(hist_df[dt_col].dtype, 'tz') or str(hist_df[dt_col].dtype).startswith('datetime') else hist_df[dt_col]
            try:
                hist_df[dt_col] = pd.to_datetime(hist_df[dt_col]).dt.tz_localize(None)
            except Exception:
                pass

            if {'Open', 'High', 'Low', 'Close'}.issubset(hist_df.columns):
                fig_candle = go.Figure(data=[go.Candlestick(
                    x=hist_df[dt_col],
                    open=hist_df['Open'],
                    high=hist_df['High'],
                    low=hist_df['Low'],
                    close=hist_df['Close'],
                    increasing_line_color='#22c55e',
                    decreasing_line_color='#ef4444',
                    increasing_fillcolor='#15803d',
                    decreasing_fillcolor='#7f1d1d',
                )])
                fig_candle.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(24, 24, 27, 0.6)',
                    font_color='#e4e4e7',
                    xaxis=dict(showgrid=False, rangeslider=dict(visible=False)),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(t=10, b=0, l=0, r=0),
                    height=280
                )
                st.plotly_chart(fig_candle, use_container_width=True)
            else:
                # Fallback to line chart
                fig_price = px.line(hist_df, x=dt_col, y="Close", labels={"Close": "Harga (IDR)"})
                fig_price.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(24,24,27,0.6)', font_color='#e4e4e7', margin=dict(t=10,b=0,l=0,r=0), height=250)
                fig_price.update_traces(line_color="#4ade80" if mkt_data['change_val'] >= 0 else "#ef4444")
                st.plotly_chart(fig_price, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{SVG_NEWSPAPER} Volume Analisis</div>
                    <div class="metric-value">{total_articles} Berita</div>
                </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{SVG_GAUGE} Indeks Rata-Rata</div>
                    <div class="metric-value" style="color: {sentiment_color};">{avg_score:.2f} ({sentiment_text})</div>
                </div>
            """, unsafe_allow_html=True)
        with m_col3:
            pos_pct = (positive_count / total_articles) * 100 if total_articles > 0 else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{SVG_TREND_UP} Aksi Positif</div>
                    <div class="metric-value" style="color: #4ade80;">{pos_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        with m_col4:
            neg_pct = (negative_count / total_articles) * 100 if total_articles > 0 else 0
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{SVG_TREND_DOWN} Aksi Melemah</div>
                    <div class="metric-value" style="color: #fca5a5;">{neg_pct:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Section Row 1: Donut Chart, Speedometer Gauge, and Trend Line (3-Column Responsive Grid)
        v_col1, v_col2, v_col3 = st.columns([1, 1, 1])
        
        with v_col1:
            st.subheader("Distribusi Sentimen")
            sentiment_df = pd.DataFrame({
                "Kategori": ["Positif", "Netral", "Negatif"],
                "Jumlah": [positive_count, neutral_count, negative_count]
            })
            
            fig_pie = px.pie(
                sentiment_df, 
                values="Jumlah", 
                names="Kategori", 
                hole=0.5,
                color="Kategori",
                color_discrete_map={"Positif": "#15803d", "Netral": "#27272a", "Negatif": "#b91c1c"}
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e4e4e7',
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with v_col2:
            st.subheader("Indeks Sentimen")
            
            # Speedometer Gauge Chart for sentiment index (-1 to +1)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [-1.0, 1.0], 'tickwidth': 1, 'tickcolor': "#a1a1aa"},
                    'bar': {'color': "#ef4444"},
                    'bgcolor': "#18181b",
                    'borderwidth': 1,
                    'bordercolor': "#27272a",
                    'steps': [
                        {'range': [-1.0, -0.15], 'color': '#450a0a'},
                        {'range': [-0.15, 0.15], 'color': '#18181b'},
                        {'range': [0.15, 1.0], 'color': '#052e16'}
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e4e4e7',
                margin=dict(t=20, b=0, l=10, r=10),
                height=220
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with v_col3:
            st.subheader("Tren Kumulatif")
            if not df_sorted.empty and len(df_sorted) > 1:
                df_sorted['Kumulatif Sentimen'] = df_sorted['Sentimen'].map({"POSITIVE": 1.0, "NEUTRAL": 0.0, "NEGATIVE": -1.0}).cumsum()
                
                fig_trend = px.line(
                    df_sorted,
                    x="Datetime",
                    y="Kumulatif Sentimen",
                    labels={"Kumulatif Sentimen": "Indeks", "Datetime": "Waktu"},
                    markers=True
                )
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(24, 24, 27, 0.6)',
                    font_color='#e4e4e7',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(t=10, b=0, l=0, r=0),
                    height=220
                )
                fig_trend.update_traces(line_color="#ef4444", marker_color="#fca5a5")
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Data tren historis tidak mencukupi.")

        # Charts Section Row 2: Word Cloud and Advanced Treemap of contributing portals
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        v_col4, v_col5 = st.columns([1, 1])
        
        with v_col4:
            st.subheader("Kata Kunci Dominan (Word Cloud)")
            text_corpus = " ".join(df["Judul Berita"] + " " + df["Deskripsi"])
            indonesian_stopwords = {
                "dan", "di", "yang", "untuk", "ke", "dari", "pada", "dalam", "ini", 
                "itu", "dengan", "adalah", "tersebut", "oleh", "juga", "akan", "telah", 
                "bahwa", "sebagai", "saham", "emiten", "rupiah", "persen", "hari", "indeks", 
                "ihsg", "serta", "karena", "namun", "oleh", "telah", "bagi", "ia", "kami", 
                "kita", "kamu", "mereka", "jika", "atau", "sehingga", "tentang", "pada", "untuk",
                st.session_state.search_query.lower()
            }
            text_corpus_cleaned = re.sub(r'[^\w\s]', '', text_corpus.lower())
            
            if len(text_corpus_cleaned.strip()) > 0:
                try:
                    wordcloud = WordCloud(
                        width=800, 
                        height=400, 
                        background_color='#18181b',
                        colormap='Reds',
                        stopwords=indonesian_stopwords,
                        max_words=80
                    ).generate(text_corpus_cleaned)
                    
                    fig_wc, ax = plt.subplots(figsize=(8, 4), facecolor='#18181b')
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    fig_wc.tight_layout(pad=0)
                    st.pyplot(fig_wc)
                except Exception:
                    st.info("Kosa kata tidak mencukupi.")
            else:
                st.info("Kosa kata tidak mencukupi.")
                
        with v_col5:
            st.subheader("Distribusi Sumber Media (Treemap)")
            source_df = df["Sumber"].value_counts().reset_index()
            source_df.columns = ["Media", "Jumlah Artikel"]
            
            fig_tree = px.treemap(
                source_df,
                path=["Media"],
                values="Jumlah Artikel",
                color="Jumlah Artikel",
                color_continuous_scale="Reds"
            )
            fig_tree.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e4e4e7',
                margin=dict(t=20, b=0, l=0, r=0),
                height=330
            )
            st.plotly_chart(fig_tree, use_container_width=True)

        # Charts Section Row 3: Advanced Chronological Intensity Scatter Plot
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        st.subheader("Intensitas Sentimen Berita Kronologis")
        
        # Ensure sizes are always valid floats
        df_sorted["Size"] = df_sorted["Skor"].abs().add(0.2).astype(float)
        
        fig_scatter = px.scatter(
            df_sorted,
            x="Datetime",
            y="Skor",
            color="Sentimen",
            size="Size",
            hover_data=["Judul Berita", "Sumber"],
            color_discrete_map={"POSITIVE": "#22c55e", "NEUTRAL": "#71717a", "NEGATIVE": "#ef4444"},
            labels={"Skor": "Skor Sentimen", "Datetime": "Waktu Publikasi"}
        )
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(24, 24, 27, 0.6)',
            font_color='#e4e4e7',
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', range=[-1.15, 1.15]),
            margin=dict(t=10, b=0, l=0, r=0),
            height=280
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Comparison Section
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        st.subheader("Konsensus Sentimen Saham Pilihan (IHSG Big Caps)")
        
        tickers_data = [
            {"Ticker": "IHSG", "Harga": "+0.42%", "Konsensus": "POSITIF", "Skor": 0.28, "Vol": 19},
            {"Ticker": "BBRI", "Harga": "+1.25%", "Konsensus": "POSITIF", "Skor": 0.45, "Vol": 12},
            {"Ticker": "TLKM", "Harga": "-0.85%", "Konsensus": "NEGATIF", "Skor": -0.32, "Vol": 8},
            {"Ticker": "GOTO", "Harga": "-1.54%", "Konsensus": "NETRAL", "Skor": -0.05, "Vol": 10},
            {"Ticker": "BMRI", "Harga": "+0.95%", "Konsensus": "POSITIF", "Skor": 0.38, "Vol": 9},
            {"Ticker": "BBNI", "Harga": "+1.80%", "Konsensus": "POSITIF", "Skor": 0.52, "Vol": 7},
            {"Ticker": "ASII", "Harga": "+2.10%", "Konsensus": "POSITIF", "Skor": 0.61, "Vol": 6},
            {"Ticker": "UNVR", "Harga": "-0.20%", "Konsensus": "NEGATIF", "Skor": -0.22, "Vol": 5}
        ]
        
        # Override active emiten details with actual parsed database info
        for t in tickers_data:
            if t["Ticker"] == st.session_state.search_query.upper():
                t["Vol"] = total_articles
                t["Skor"] = avg_score
                if avg_score > 0.15:
                    t["Konsensus"] = "POSITIF"
                elif avg_score < -0.15:
                    t["Konsensus"] = "NEGATIF"
                else:
                    t["Konsensus"] = "NETRAL"
        
        # Render Comparison Table
        comp_rows = ""
        for t in tickers_data:
            badge_class = "badge-positive" if t["Konsensus"] == "POSITIF" else "badge-negative" if t["Konsensus"] == "NEGATIF" else "badge-neutral"
            score_color = "#4ade80" if t["Skor"] > 0 else "#fca5a5" if t["Skor"] < 0 else "#cbd5e1"
            is_active = "background-color: #1f1f23; border-top: 1px solid #ef4444; border-bottom: 1px solid #ef4444;" if t["Ticker"] == st.session_state.search_query.upper() else ""
            
            comp_rows += f"""
<tr style="border-bottom: 1px solid #27272a; {is_active}">
<td style="padding: 12px; font-weight: 800; color: #ffffff;">{t['Ticker']}</td>
<td style="padding: 12px; color: {'#4ade80' if '+' in t['Harga'] else '#fca5a5'}; font-weight: 700;">{t['Harga']}</td>
<td style="padding: 12px;"><span class="badge {badge_class}">{t['Konsensus']}</span></td>
<td style="padding: 12px; font-weight: 700; color: {score_color};">{t['Skor']:.2f}</td>
<td style="padding: 12px; color: #a1a1aa;">{t['Vol']} Artikel</td>
</tr>
"""
            
        comp_table_html = f"""<div style="overflow-x: auto; border-radius: 6px; border: 1px solid #27272a; margin-top: 10px;">
<table style="width:100%; border-collapse: collapse; background: #121216; text-align: left; font-size: 13px;">
<thead>
<tr style="background: #27272a; border-bottom: 2px solid #ef4444;">
<th style="padding: 12px; color: #ffffff;">Emiten</th>
<th style="padding: 12px; color: #ffffff;">Perubahan Harga</th>
<th style="padding: 12px; color: #ffffff;">Sentimen Konsensus</th>
<th style="padding: 12px; color: #ffffff;">Skor Rata-Rata</th>
<th style="padding: 12px; color: #ffffff;">Volume Berita</th>
</tr>
</thead>
<tbody>
{comp_rows}
</tbody>
</table>
</div>"""
        st.markdown(comp_table_html, unsafe_allow_html=True)

    elif active_view == "Perbandingan":
        st.subheader("Perbandingan Multi-Emiten Real-Time")
        st.caption("Bandingkan harga, sentimen, dan tren saham secara side-by-side.")

        compare_tickers = st.multiselect(
            "Pilih 2–4 Emiten untuk Dibandingkan:",
            options=["IHSG", "BBRI", "TLKM", "GOTO", "BMRI", "BBNI", "ASII", "UNVR", "BBCA", "BUMN"],
            default=["BBRI", "TLKM"],
            max_selections=4,
            help="Pilih maksimal 4 emiten untuk perbandingan side-by-side."
        )

        if compare_tickers:
            comp_cols = st.columns(len(compare_tickers))
            for i, tick in enumerate(compare_tickers):
                with comp_cols[i]:
                    with st.spinner(f"Memuat {tick}..."):
                        tick_mkt = fetch_realtime_price(tick)

                    if tick_mkt:
                        p_color = "#4ade80" if tick_mkt['change_val'] >= 0 else "#ef4444"
                        arr = "▲" if tick_mkt['change_val'] >= 0 else "▼"

                        # Mini price card
                        st.markdown(f"""
<div style="background-color:#18181b; border:1px solid #27272a; border-radius:6px; padding:16px; margin-bottom:12px;">
  <div style="font-size:11px; color:#a1a1aa; text-transform:uppercase; font-weight:700;">{tick}</div>
  <div style="font-size:24px; font-weight:800; color:{p_color}; margin:6px 0;">IDR {tick_mkt['price']:,.0f}</div>
  <div style="font-size:12px; font-weight:700; color:{p_color};">{arr} {tick_mkt['change_val']:.2f} ({tick_mkt['change_pct']:.2f}%)</div>
  <div style="display:flex; gap:12px; margin-top:10px; font-size:11px; color:#a1a1aa;">
    <span>H: <strong style="color:#fff">IDR {tick_mkt['high']:,.0f}</strong></span>
    <span>L: <strong style="color:#fff">IDR {tick_mkt['low']:,.0f}</strong></span>
  </div>
</div>""", unsafe_allow_html=True)

                        # Mini candlestick chart
                        h_df = tick_mkt['history'].reset_index()
                        dc = 'Datetime' if 'Datetime' in h_df.columns else 'Date'
                        try:
                            h_df[dc] = pd.to_datetime(h_df[dc]).dt.tz_localize(None)
                        except Exception:
                            pass

                        if {'Open', 'High', 'Low', 'Close'}.issubset(h_df.columns):
                            fig_c = go.Figure(data=[go.Candlestick(
                                x=h_df[dc],
                                open=h_df['Open'], high=h_df['High'],
                                low=h_df['Low'], close=h_df['Close'],
                                increasing_line_color='#22c55e', decreasing_line_color='#ef4444',
                                increasing_fillcolor='#15803d', decreasing_fillcolor='#7f1d1d',
                            )])
                            fig_c.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(24,24,27,0.6)',
                                font_color='#e4e4e7',
                                xaxis=dict(showgrid=False, rangeslider=dict(visible=False), showticklabels=False),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                margin=dict(t=5, b=5, l=0, r=0),
                                height=180, showlegend=False
                            )
                            st.plotly_chart(fig_c, use_container_width=True)
                    else:
                        st.warning(f"Data tidak tersedia untuk {tick}.")

        else:
            st.info("Pilih minimal 2 emiten dari dropdown di atas untuk memulai perbandingan.")

    elif active_view == "Log Berita":
        st.subheader("Detail Log Analisis Sentimen Saham")
        
        # Export option
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Unduh Data Sentimen (CSV)",
            data=csv_data,
            file_name=f"sentimen_{st.session_state.search_query.lower()}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        def format_sentiment_label(val):
            if val == "POSITIVE":
                return f'<span class="badge badge-positive">{SVG_LIVE} Positif</span>'
            elif val == "NEGATIVE":
                return f'<span class="badge badge-negative">{SVG_OFFLINE} Negatif</span>'
            else:
                return '<span class="badge badge-neutral">Netral</span>'

        table_rows = ""
        for idx, row in df.iterrows():
            score_color = "#4ade80" if row['Skor'] > 0 else "#fca5a5" if row['Skor'] < 0 else "#cbd5e1"
            
            # Simple flat badges inside table
            table_badge = ""
            if row['Sentimen'] == "POSITIVE":
                table_badge = '<span class="badge badge-positive">Positif</span>'
            elif row['Sentimen'] == "NEGATIVE":
                table_badge = '<span class="badge badge-negative">Negatif</span>'
            else:
                table_badge = '<span class="badge badge-neutral">Netral</span>'

            table_rows += f"""
                <tr style="border-bottom: 1px solid #27272a;">
                    <td style="padding: 14px; font-size: 13px; color: #a1a1aa; white-space: nowrap;">{row['Waktu']}</td>
                    <td style="padding: 14px; font-size: 13px; font-weight: 700; color: #ef4444;">{row['Sumber']}</td>
                    <td style="padding: 14px; font-size: 14px;">
                        <a href="{row['Link']}" target="_blank" class="table-link">{row['Judul Berita']}</a>
                        <br><small style="color: #a1a1aa; font-weight: 400; line-height: 1.4;">{row['Deskripsi']}</small>
                    </td>
                    <td style="padding: 14px; text-align: center; vertical-align: middle;">{table_badge}</td>
                    <td style="padding: 14px; text-align: center; font-weight: 700; font-size: 14px; color: {score_color};">{row['Skor']:.2f}</td>
                </tr>
            """
            
        full_table_html = f"""
            <div style="overflow-x: auto; border-radius: 6px; border: 1px solid #27272a;">
                <table style="width:100%; border-collapse: collapse; background: #18181b; text-align: left;">
                    <thead>
                        <tr style="background: #27272a; border-bottom: 2px solid #ef4444;">
                            <th style="padding: 14px; color: #ffffff; font-weight: 700; font-size: 13px;">Waktu</th>
                            <th style="padding: 14px; color: #ffffff; font-weight: 700; font-size: 13px;">Sumber Media</th>
                            <th style="padding: 14px; color: #ffffff; font-weight: 700; font-size: 13px;">Ringkasan Informasi</th>
                            <th style="padding: 14px; text-align: center; color: #ffffff; font-weight: 700; font-size: 13px;">Sentimen</th>
                            <th style="padding: 14px; text-align: center; color: #ffffff; font-weight: 700; font-size: 13px;">Skor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        """
        st.markdown(full_table_html, unsafe_allow_html=True)

# ─── Auto-Refresh Mechanism ─────────────────────────────────────────────────────
if auto_refresh:
    import time
    countdown_placeholder = st.empty()
    for secs_left in range(refresh_interval, 0, -1):
        mins, s = divmod(secs_left, 60)
        countdown_placeholder.markdown(
            f'<div style="position:fixed; bottom:16px; right:16px; background:#18181b; '
            f'border:1px solid #27272a; padding:8px 16px; border-radius:6px; '
            f'font-size:12px; color:#a1a1aa; z-index:9999;">'
            f'🔄 Auto-refresh dalam <strong style="color:#ef4444">{mins:02d}:{s:02d}</strong>'
            f'</div>',
            unsafe_allow_html=True
        )
        time.sleep(1)
    st.cache_data.clear()
    st.rerun()
