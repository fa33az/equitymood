# EquityMood

**EquityMood** is a real-time sentiment analysis dashboard for the Indonesian stock market (IDX/IHSG). It aggregates financial news from 14+ Indonesian media RSS feeds, runs NLP-based sentiment scoring, and overlays the results with live market data from Yahoo Finance — all in one interactive interface.

> Built with Python, Streamlit, and Plotly. No subscriptions. No paid APIs. Just open data.

---

## Features

- **Real-Time News Aggregation** — Pulls articles from CNBC Indonesia, Kontan, Bisnis Indonesia, Detik Finance, Kompas, Tempo, Republika, and more.
- **Dual Sentiment Engine** — Lexicon-based analysis for speed; optional [IndoBERT](https://huggingface.co/indobenchmark/indobert-base-p1) deep learning model for accuracy.
- **Live Market Data** — Real-time price, daily change, high/low, and volume via Yahoo Finance.
- **Candlestick Chart** — 5-day OHLCV candlestick visualization for the searched ticker.
- **Multi-Ticker Comparison** — Side-by-side candlestick charts and price cards for up to 4 stocks simultaneously.
- **Sentiment Visualizations** — Donut chart, gauge meter, word cloud, treemap, scatter plot, and historical trend.
- **Auto-Refresh** — Configurable auto-refresh timer (1, 2, 5, or 10 minutes) with a live countdown overlay.
- **News Log & CSV Export** — Full article table with sentiment badges, scores, and one-click CSV download.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Interface | [Streamlit](https://streamlit.io) |
| Charting | [Plotly](https://plotly.com/python/) |
| NLP (Lexicon) | Custom Indonesian financial lexicon |
| NLP (Deep Learning) | [IndoBERT](https://huggingface.co/indobenchmark/indobert-base-p1) via Transformers |
| Market Data | [yfinance](https://github.com/ranaroussi/yfinance) |
| Feed Parsing | [feedparser](https://feedparser.readthedocs.io/) + BeautifulSoup |
| Word Cloud | [wordcloud](https://github.com/amueller/word_cloud) |

---

## Project Structure

```
equitymood/
├── app.py                  # Main Streamlit application
├── feed_parser.py          # RSS feed aggregator (14 sources)
├── sentiment_analyzer.py   # Lexicon + IndoBERT sentiment engine
├── market_data.py          # Yahoo Finance real-time price wrapper
├── templates.py            # HTML/SVG component templates
├── style.css               # Global dark theme stylesheet
└── requirements.txt
```

---

## Quickstart

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/equitymood.git
cd equitymood
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

> For IndoBERT support, PyTorch must be installed separately. See [pytorch.org](https://pytorch.org/get-started/locally/) for platform-specific instructions.

**3. Run the app**

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`.

---

## Usage

1. Enter a stock ticker (e.g. `BBRI`, `TLKM`, `GOTO`) or the keyword `IHSG` in the sidebar.
2. Use the quick-select buttons at the top for common tickers.
3. Switch between **Dashboard**, **Perbandingan** (Comparison), and **Log Berita** (News Log) from the sidebar.
4. Toggle **IndoBERT** for higher-accuracy sentiment at the cost of slightly longer load times.
5. Enable **Auto-Refresh** to keep the data current automatically.

---

## News Sources

| Portal | Category |
|---|---|
| CNBC Indonesia | Market, Investment, Economy |
| Kontan | News, Investment, Macro |
| Bisnis Indonesia | General Finance |
| Detik Finance | General Finance |
| Liputan6 Bisnis | Business News |
| Kompas Money | Economy |
| Okezone Finance | Finance |
| Sindonews Ekonomi | Economy |
| Republika Ekonomi | Economy |
| Tempo Bisnis | Business |

---

## Notes

- All news data is sourced from publicly available RSS feeds.
- Market data is fetched via the unofficial Yahoo Finance API (`yfinance`). Data may be delayed by 15 minutes.
- IndoBERT inference runs locally on your machine — no external API calls are made for the NLP model.
- The lexicon-based analyzer is tuned for Indonesian financial text and runs without GPU requirements.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
