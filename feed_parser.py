import feedparser
import re
from datetime import datetime
import random
from bs4 import BeautifulSoup

# Comprehensive list of free RSS Feeds for Indonesian Stock Market & Economy
RSS_FEEDS = {
    "CNBC Indonesia (Market)": "https://www.cnbcindonesia.com/market/rss",
    "CNBC Indonesia (Investment)": "https://www.cnbcindonesia.com/investment/rss",
    "CNBC Indonesia (News)": "https://www.cnbcindonesia.com/news/rss",
    "Kontan (News)": "https://rss.kontan.co.id/news",
    "Kontan (Investasi)": "https://rss.kontan.co.id/investasi",
    "Kontan (Makro)": "https://rss.kontan.co.id/makro",
    "Bisnis Indonesia": "https://feeds.feedburner.com/bisnis-indonesia",
    "Detik Finance": "https://rss.detik.com/index.php/finance",
    "Liputan6 Bisnis": "https://www.liputan6.com/feed/bisnis",
    "Kompas Money": "https://money.kompas.com/rss",
    "Okezone Finance": "https://keuangan.okezone.com/rss",
    "Sindonews Ekbis": "https://ekbis.sindonews.com/rss",
    "Republika Ekonomi": "https://www.republika.co.id/rss/ekonomi",
    "Tempo Bisnis": "https://rss.tempo.co/bisnis"
}

# Ticker synonym mappings to maximize matching accuracy across news text
TICKER_KEYWORDS = {
    "GOTO": ["goto", "gojek", "tokopedia"],
    "TLKM": ["tlkm", "telkom", "telkom indonesia"],
    "BBRI": ["bbri", "bri", "bank rakyat indonesia", "bank bri"],
    "BMRI": ["bmri", "mandiri", "bank mandiri"],
    "BBNI": ["bbni", "bni", "bank negara indonesia", "bank bni"],
    "ASII": ["asii", "astra", "astra international"],
    "UNVR": ["unvr", "unilever", "unilever indonesia"],
    "IHSG": ["ihsg", "indeks harga saham gabungan", "indeks saham", "bursa efek indonesia", "bei"]
}

# Rich set of dummy articles for fallback and local testing
DUMMY_ARTICLES = [
    {
        "title": "IHSG Ditutup Menguat Tipis Ditopang Aksi Beli Saham Perbankan Big Caps",
        "summary": "Indeks Harga Saham Gabungan (IHSG) ditutup menguat pada perdagangan hari ini. Investor asing terpantau banyak mengoleksi saham perbankan besar seperti BBRI dan BMRI di tengah optimisme rilis data ekonomi domestik.",
        "source": "CNBC Indonesia Sim",
        "published": "2026-06-30T16:00:00",
        "link": "https://example.com/news/1"
    },
    {
        "title": "Analisis Saham BBRI: Rekomendasi Beli Seiring Prospek Kinerja Kredit Mikro yang Cerah",
        "summary": "Kinerja PT Bank Rakyat Indonesia (Persero) Tbk (BBRI) diproyeksikan tumbuh solid hingga akhir tahun. Rasio kredit bermasalah (NPL) yang terjaga membuat BBRI tetap menjadi favorit para analis dengan target harga yang menarik.",
        "source": "Kontan Sim",
        "published": "2026-06-30T15:30:00",
        "link": "https://example.com/news/2"
    },
    {
        "title": "Kinerja Saham TLKM Menurun Akibat Ketatnya Persaingan Industri Telekomunikasi",
        "summary": "Saham PT Telkom Indonesia (Persero) Tbk (TLKM) mengalami koreksi seiring dengan kekhawatiran pasar terhadap margin profitabilitas industri telekomunikasi yang kian ketat dan tingginya belanja modal untuk infrastruktur 5G.",
        "source": "Bisnis Indonesia Sim",
        "published": "2026-06-30T14:15:00",
        "link": "https://example.com/news/3"
    },
    {
        "title": "GOTO Luncurkan Layanan Baru untuk Dorong Profitabilitas, Saham Bergerak Netral",
        "summary": "PT GoTo Gojek Tokopedia Tbk (GOTO) meluncurkan fitur terbaru guna meningkatkan frekuensi transaksi pengguna. Investor merespons secara netral dan masih menunggu dampak nyata inovasi ini terhadap laporan keuangan mendatang.",
        "source": "CNBC Indonesia Sim",
        "published": "2026-06-30T13:00:00",
        "link": "https://example.com/news/4"
    },
    {
        "title": "IHSG Rawan Koreksi Menyusul Sentimen Negatif dari Pasar Global",
        "summary": "Sentimen negatif dari bursa global yang dipicu oleh kekhawatiran kenaikan suku bunga The Fed diperkirakan akan menekan pergerakan IHSG hari ini. Saham-saham komoditas diprediksi mengalami volatilitas tinggi.",
        "source": "Kontan Sim",
        "published": "2026-06-30T11:45:00",
        "link": "https://example.com/news/5"
    },
    {
        "title": "Laba Bersih Naik 20%, Saham BMRI Sentuh Rekor Tertinggi Baru",
        "summary": "PT Bank Mandiri (Persero) Tbk (BMRI) melaporkan pertumbuhan laba bersih yang signifikan sepanjang kuartal ini. Saham BMRI melonjak tajam dan memimpin penguatan IHSG hari ini.",
        "source": "Bisnis Indonesia Sim",
        "published": "2026-06-30T10:30:00",
        "link": "https://example.com/news/6"
    },
    {
        "title": "Prospek Saham ASII Cerah Didorong Peningkatan Penjualan Otomotif Nasional",
        "summary": "PT Astra International Tbk (ASII) diyakini mendapat katalis positif seiring meningkatnya angka penjualan mobil nasional dan tingginya permintaan untuk kendaraan ramah lingkungan di pasar domestik.",
        "source": "CNBC Indonesia Sim",
        "published": "2026-06-30T09:15:00",
        "link": "https://example.com/news/7"
    },
    {
        "title": "Sentimen Negatif Melanda UNVR Akibat Kenaikan Biaya Bahan Baku Impor",
        "summary": "Harga saham PT Unilever Indonesia Tbk (UNVR) terus tertekan menyusul pelemahan nilai tukar rupiah yang memicu lonjakan biaya produksi bahan baku impor. Manajemen berupaya melakukan efisiensi operasional.",
        "source": "Kontan Sim",
        "published": "2026-06-30T08:00:00",
        "link": "https://example.com/news/8"
    },
    {
        "title": "Investor Asing Catatkan Net Buy Bersih pada Saham BBRI dan BBNI",
        "summary": "Aksi beli bersih oleh investor asing kembali berlanjut pada perdagangan tengah hari. Saham perbankan BUMN seperti BBRI dan BBNI menjadi tujuan utama dana asing masuk, memberikan dorongan positif bagi indeks.",
        "source": "Bisnis Indonesia Sim",
        "published": "2026-06-30T12:00:00",
        "link": "https://example.com/news/9"
    },
    {
        "title": "GOTO Mengalami Tekanan Jual, Analis Rekomendasikan Sikap Wait and See",
        "summary": "Saham GOTO kembali ditutup di zona merah pada sesi perdagangan pertama. Sejumlah analis menyarankan investor untuk tetap waspada dan menunggu sinyal pembalikan arah yang kuat sebelum melakukan akumulasi.",
        "source": "CNBC Indonesia Sim",
        "published": "2026-06-30T11:00:00",
        "link": "https://example.com/news/10"
    }
]

def clean_html(html_text):
    """Remove HTML tags from text."""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text()

def get_keywords_for_query(query):
    """Return a list of matching search keywords for a given stock query."""
    q_upper = query.strip().upper()
    if q_upper in TICKER_KEYWORDS:
        return TICKER_KEYWORDS[q_upper]
    return [query.lower()]

import streamlit as st

@st.cache_data(ttl=600)
def fetch_feed_data(query="IHSG", use_fallback=True):
    """
    Fetch news articles from Indonesian business RSS feeds filtered by query.
    If fetching fails or returns no matches, it yields simulated dummy articles.
    """
    keywords = get_keywords_for_query(query)
    articles = []
    seen_titles = set()

    # Try fetching from RSS feeds
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                
                # Clean HTML tags
                title = clean_html(title)
                summary = clean_html(summary)
                
                # De-duplicate articles by clean title
                title_clean = title.strip().lower()
                if title_clean in seen_titles:
                    continue
                
                # Check for match (case-insensitive) for any associated keyword
                match_found = False
                for kw in keywords:
                    if kw in title.lower() or kw in summary.lower():
                        match_found = True
                        break
                        
                if match_found:
                    seen_titles.add(title_clean)
                    
                    # Parse published date
                    published_raw = entry.get("published", "")
                    published_str = published_raw
                    try:
                        if entry.get("published_parsed"):
                            published_str = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass
                        
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "source": name,
                        "published": published_str,
                        "link": entry.get("link", "#")
                    })
        except Exception as e:
            pass

    # If no articles found or fetching failed, generate relevant dummy data
    if not articles and use_fallback:
        # Generate some synthetic matching articles if dummy ones match the query
        for dummy in DUMMY_ARTICLES:
            title_clean = dummy["title"].strip().lower()
            if title_clean in seen_titles:
                continue
                
            match_found = False
            for kw in keywords:
                if kw in dummy["title"].lower() or kw in dummy["summary"].lower():
                    match_found = True
                    break
            
            if match_found:
                seen_titles.add(title_clean)
                articles.append(dummy.copy())
                
        # If still empty, create generic simulated articles for the searched ticker
        if not articles:
            sources = ["CNBC Indonesia Sim", "Kontan Sim", "Bisnis Indonesia Sim"]
            for i in range(5):
                sentiment_type = random.choice(["positif", "negatif", "netral"])
                if sentiment_type == "positif":
                    title = f"Prospek Saham {query.upper()} Dinilai Menjanjikan Ditengah Sentimen Positif Pasar"
                    summary = f"Analis memproyeksikan saham {query.upper()} berpotensi mengalami kenaikan signifikan dalam jangka pendek seiring meningkatnya volume perdagangan dan sentimen domestik yang kuat."
                elif sentiment_type == "negatif":
                    title = f"Tekanan Aksi Ambil Untung Menyeret Saham {query.upper()} ke Zona Merah"
                    summary = f"Saham {query.upper()} terpantau melemah hari ini akibat aksi profit taking oleh investor lokal di tengah ketidakpastian kondisi makroekonomi global."
                else:
                    title = f"Saham {query.upper()} Bergerak Sideways Menanti Rilis Laporan Keuangan"
                    summary = f"Saham {query.upper()} ditutup mendatar hari ini. Para pelaku pasar terpantau melakukan aksi wait and see menjelang rilis kinerja keuangan kuartal terbaru."

                articles.append({
                    "title": title,
                    "summary": summary,
                    "source": random.choice(sources),
                    "published": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "link": "https://example.com/simulated"
                })

    # Sort by published date if possible
    try:
        articles.sort(key=lambda x: x["published"], reverse=True)
    except Exception:
        pass

    return articles
