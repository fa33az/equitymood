# Inline SVGs to avoid any missing external FontAwesome icon loading issues
SVG_NEWSPAPER = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><path d="M16 8h2"></path><path d="M16 12h2"></path><path d="M16 16h2"></path><path d="M6 8h6v8H6z"></path></svg>'
SVG_GAUGE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path></svg>'
SVG_TREND_UP = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
SVG_TREND_DOWN = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fca5a5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
SVG_LIVE = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><circle cx="12" cy="20" r="2" fill="#4ade80"></circle></svg>'
SVG_OFFLINE = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#a1a1aa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><line x1="1" y1="1" x2="23" y2="23"></line><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"></path><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"></path><path d="M10.71 5.05A16 16 0 0 1 22.58 9"></path><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"></path><circle cx="12" cy="20" r="2"></circle></svg>'

# HTML templates
def get_header_html(status_badge):
    return f"""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div class="header-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
                EquityMood
            </div>
            <div>
                {status_badge}
            </div>
        </div>
        <div class="header-subtitle">Dashboard analisis sentimen saham IHSG berbasis data RSS real-time.</div>
    </div>
    """

TICKER_TAPE_HTML = """
<div class="ticker-wrap">
    <div class="ticker">
        <div class="ticker-item"><b>IHSG</b>: <span>+0.42%</span></div>
        <div class="ticker-item"><b>BBRI</b>: <span>+1.25%</span></div>
        <div class="ticker-item"><b>TLKM</b>: <span class="neg">-0.85%</span></div>
        <div class="ticker-item"><b>ASII</b>: <span>+2.10%</span></div>
        <div class="ticker-item"><b>GOTO</b>: <span class="neg">-1.54%</span></div>
        <div class="ticker-item"><b>BMRI</b>: <span>+0.95%</span></div>
        <div class="ticker-item"><b>BBNI</b>: <span>+1.80%</span></div>
        <div class="ticker-item"><b>IHSG</b>: <span>+0.42%</span></div>
        <div class="ticker-item"><b>BBRI</b>: <span>+1.25%</span></div>
        <div class="ticker-item"><b>TLKM</b>: <span class="neg">-0.85%</span></div>
        <div class="ticker-item"><b>ASII</b>: <span>+2.10%</span></div>
        <div class="ticker-item"><b>GOTO</b>: <span class="neg">-1.54%</span></div>
        <div class="ticker-item"><b>BMRI</b>: <span>+0.95%</span></div>
        <div class="ticker-item"><b>BBNI</b>: <span>+1.80%</span></div>
    </div>
</div>
"""

def get_market_bar_html(query, symbol, price, change_val, change_pct, high, low, volume, price_color, arrow):
    return f"""
    <div style="background-color: #121216; border: 1px solid #27272a; padding: 16px; border-radius: 6px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div>
            <small style="color: #a1a1aa; font-weight: 700; text-transform: uppercase;">HARGA PASAR REALTIME (YAHOO FINANCE)</small>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-top: 4px;">
                {query.upper()} ({symbol})
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 28px; font-weight: 800; color: {price_color};">
                IDR {price:.2f}
            </div>
            <div style="font-size: 13px; font-weight: 700; color: {price_color}; margin-top: 2px;">
                {arrow} {change_val:.2f} ({change_pct:.2f}%)
            </div>
        </div>
        <div style="display: flex; gap: 20px; font-size: 11px; border-left: 1px solid #27272a; padding-left: 20px;">
            <div>
                <span style="color: #a1a1aa; display:block;">Tertinggi</span>
                <strong style="color: #ffffff; font-size: 13px;">IDR {high:.2f}</strong>
            </div>
            <div>
                <span style="color: #a1a1aa; display:block;">Terendah</span>
                <strong style="color: #ffffff; font-size: 13px;">IDR {low:.2f}</strong>
            </div>
            <div>
                <span style="color: #a1a1aa; display:block;">Volume</span>
                <strong style="color: #ffffff; font-size: 13px;">{int(volume):,}</strong>
            </div>
        </div>
    </div>
    """
