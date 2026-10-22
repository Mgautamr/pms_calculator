"""Shared look for every page: warm editorial (paper, ink, saffron).

The `*_html` functions are pure and return single-line HTML (no blank lines or
indentation, which Markdown would mangle). The matching render functions call
st.markdown. All text is escaped; pass `Html(...)` for markup you built yourself.
"""
import html
from string import Template

import altair as alt
import streamlit as st

PAPER = "#05070A"
SIDEBAR = "#0A0E12"
INK = "#DFE7E0"
MUTED = "#8F9A93"
RULE = "#2A3238"
SAFFRON = "#E0231C"
SAFFRON_DEEP = "#FF5A3C"
GREEN = "#7FB59A"
BRICK = "#E0231C"
SLATE = "#78837C"

BODY_FONT = "Onest"


class Html(str):
    """Marks a string as trusted markup so it is not escaped."""


def esc(value):
    return value if isinstance(value, Html) else html.escape(str(value))


CSS = Template("""
@import url('https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&display=swap');
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: $PAPER; color: $INK; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea { font-family: 'Onest', system-ui, -apple-system, 'Segoe UI', sans-serif; }
.stApp h1, .stApp h2, .stApp h3 { font-family: 'Onest', system-ui, sans-serif; font-weight: 400; letter-spacing: -0.01em; color: $INK; }
[data-testid="stHeader"] { background: transparent; }
.stDeployButton, [data-testid="stAppDeployButton"] { display: none; }
[data-testid="stSidebar"] { background: $SIDEBAR; border-right: 1px solid $RULE; }
.block-container { max-width: 1120px; padding-top: 2.25rem; }
.stTabs [data-baseweb="tab-list"] { gap: 1.75rem; border-bottom: 1px solid $RULE; }
.stTabs [data-baseweb="tab"] { font-family: 'Onest', system-ui, sans-serif; font-size: 1.1rem; padding-left: 0; padding-right: 0; color: $MUTED; }
.stTabs [aria-selected="true"] { color: $INK; }
.stTabs [data-baseweb="tab-highlight"] { background: $SAFFRON; height: 3px; }
[data-baseweb="input"], [data-baseweb="select"] > div { border-color: $RULE; }
a { color: $SAFFRON_DEEP; }

.stApp .pms-masthead { padding: 0 0 1.25rem; border-bottom: 1px solid $INK; margin-bottom: 1.75rem; }
.stApp .pms-masthead h1 { font-size: clamp(2rem, 4.2vw, 3.1rem); line-height: 1.08; letter-spacing: -0.02em; margin: 0 0 0.6rem; padding: 0; }
.stApp .pms-masthead p { max-width: 62ch; color: $MUTED; font-size: 1.05rem; line-height: 1.55; margin: 0; }

.stApp .pms-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); border-top: 1px solid $RULE; border-bottom: 1px solid $RULE; margin: 0 0 2rem; }
.stApp .pms-stat { padding: 1rem 1.25rem 1.1rem; border-left: 1px solid $RULE; }
.stApp .pms-stat:first-child { border-left: none; padding-left: 0; }
.stApp .pms-stat .label { font-size: 0.9rem; color: $MUTED; }
.stApp .pms-stat .value { font-family: 'Onest', system-ui, sans-serif; font-size: clamp(1.8rem, 3.1vw, 2.55rem); line-height: 1.15; margin: 0.25rem 0 0.4rem; font-variant-numeric: lining-nums tabular-nums; }
.stApp .pms-stat.lead .value span { background: linear-gradient(transparent 62%, rgba(224, 35, 28, 0.45) 62%); }
.stApp .pms-stat .note { font-size: 0.88rem; line-height: 1.4; color: $MUTED; }
.stApp .pms-stat .note.good { color: $GREEN; }
.stApp .pms-stat .note.bad { color: $BRICK; }

.stApp .pms-section { margin: 2.1rem 0 0.8rem; }
.stApp .pms-section h2 { font-size: 1.55rem; margin: 0; padding: 0; line-height: 1.2; }
.stApp .pms-section p { color: $MUTED; margin: 0.25rem 0 0; max-width: 66ch; line-height: 1.5; }

.stApp .pms-notice { border-left: 3px solid $SAFFRON; background: rgba(224, 35, 28, 0.10); padding: 0.8rem 1.1rem; margin: 0.4rem 0 1.4rem; line-height: 1.5; }
.stApp .pms-notice strong { font-family: 'Onest', system-ui, sans-serif; font-size: 1.05rem; font-weight: 600; }
.stApp .pms-notice ul { margin: 0.35rem 0 0 1.1rem; padding: 0; }
.stApp .pms-notice li { margin: 0.2rem 0; }

.stApp .pms-tablewrap { overflow-x: auto; margin: 0.5rem 0 1rem; }
.stApp .pms-table { width: 100%; border-collapse: collapse; font-size: 0.95rem; line-height: 1.45; }
.stApp .pms-table th { font-family: 'Onest', system-ui, sans-serif; font-size: 1.02rem; font-weight: 600; text-align: left; padding: 0.55rem 0.9rem 0.55rem 0; border-bottom: 1px solid $INK; vertical-align: bottom; }
.stApp .pms-table td { padding: 0.7rem 0.9rem 0.7rem 0; border-bottom: 1px solid $RULE; vertical-align: top; }
.stApp .pms-table td:first-child { font-weight: 600; white-space: nowrap; }
.stApp .pms-table .num { text-align: right; font-variant-numeric: lining-nums tabular-nums; white-space: nowrap; }
.stApp .pms-table th.num { text-align: right; }

.stApp .dot { display: inline-block; width: 0.6rem; height: 0.6rem; border-radius: 50%; margin-left: 0.3rem; vertical-align: baseline; }
.stApp .dot-official { background: $GREEN; }
.stApp .dot-official_reported { background: #5E9A7C; }
.stApp .dot-legal_database { background: #4A6FA5; }
.stApp .dot-secondary { background: #C9A24A; }
.stApp .dot-not_verified { background: transparent; border: 1.5px solid #8C867A; }
.stApp .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.stApp .pms-legend { display: flex; flex-wrap: wrap; gap: 0.4rem 1.4rem; font-size: 0.9rem; color: $MUTED; margin: 0.2rem 0 1rem; }
.stApp .pms-legend .dot { margin: 0 0.4rem 0 0; }

.stApp .pms-rows .row { display: grid; grid-template-columns: minmax(150px, 1.2fr) 8.5rem 3fr; gap: 0.4rem 1rem; padding: 0.75rem 0; border-bottom: 1px solid $RULE; line-height: 1.45; }
.stApp .pms-rows .name { font-family: 'Onest', system-ui, sans-serif; font-size: 1.12rem; font-weight: 600; }
.stApp .pms-rows .open { color: $GREEN; font-weight: 600; }
.stApp .pms-rows .below { color: $BRICK; font-weight: 600; }
.stApp .pms-rows .caution { color: $SAFFRON_DEEP; display: block; margin-top: 0.15rem; }

.stApp .pms-index .row { display: grid; grid-template-columns: minmax(180px, 1fr) 3fr; gap: 0.3rem 1.5rem; padding: 0.95rem 0; border-bottom: 1px solid $RULE; line-height: 1.5; }
.stApp .pms-index .name { font-family: 'Onest', system-ui, sans-serif; font-size: 1.3rem; font-weight: 500; }
.stApp .pms-foot { color: $MUTED; font-size: 0.85rem; line-height: 1.5; border-top: 1px solid $RULE; padding-top: 0.9rem; margin-top: 2.5rem; max-width: 80ch; }
.stApp .pms-muted { color: $MUTED; }

.stApp::before { content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none; background: radial-gradient(125% 95% at 50% 42%, transparent 40%, rgba(2, 4, 6, 0.6)); }
.stApp::after { content: ''; position: fixed; inset: -1px; z-index: 1; pointer-events: none; opacity: 0.06; mix-blend-mode: overlay; background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>"); }
.stApp .pms-masthead h1 { text-transform: uppercase; font-weight: 400; letter-spacing: -0.01em; }
.stApp .pms-stat .value { font-weight: 300; }

@media (max-width: 640px) {
  .stApp .pms-rows .row, .stApp .pms-index .row { grid-template-columns: 1fr; }
  .stApp .pms-stat { border-left: none; padding-left: 0; border-top: 1px solid $RULE; }
  .stApp .pms-stat:first-child { border-top: none; }
}
""").safe_substitute(
    PAPER=PAPER, SIDEBAR=SIDEBAR, INK=INK, MUTED=MUTED, RULE=RULE, SAFFRON=SAFFRON,
    SAFFRON_DEEP=SAFFRON_DEEP, GREEN=GREEN, BRICK=BRICK,
)


def apply():
    """Inject the shared styles. Call once near the top of every page."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ---------- pure HTML builders ----------
def masthead_html(title, deck=None):
    deck_html = f"<p>{esc(deck)}</p>" if deck else ""
    return f'<div class="pms-masthead"><h1>{esc(title)}</h1>{deck_html}</div>'


def section_html(title, note=None):
    note_html = f"<p>{esc(note)}</p>" if note else ""
    return f'<div class="pms-section"><h2>{esc(title)}</h2>{note_html}</div>'


def stat_strip_html(stats):
    """stats: list of dicts with label, value, optional note and tone (good, bad, neutral).

    The first stat is the lead figure and gets the saffron highlighter.
    """
    cells = []
    for i, s in enumerate(stats):
        lead = " lead" if i == 0 else ""
        note = ""
        if s.get("note"):
            tone = s.get("tone", "neutral")
            tone_class = "" if tone == "neutral" else f" {tone}"
            note = f'<div class="note{tone_class}">{esc(s["note"])}</div>'
        cells.append(
            f'<div class="pms-stat{lead}"><div class="label">{esc(s["label"])}</div>'
            f'<div class="value"><span>{esc(s["value"])}</span></div>{note}</div>'
        )
    return f'<div class="pms-stats">{"".join(cells)}</div>'


def notice_html(title, items=None, text=None):
    body = f"<div>{esc(text)}</div>" if text else ""
    if items:
        body += "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"
    return f'<div class="pms-notice"><strong>{esc(title)}</strong>{body}</div>'


def data_table_html(headers, rows, numeric_cols=(), min_width=None):
    head = "".join(
        f'<th class="{"num" if i in numeric_cols else ""}">{esc(h)}</th>' for i, h in enumerate(headers))
    body = "".join(
        "<tr>" + "".join(
            f'<td class="{"num" if i in numeric_cols else ""}">{esc(c)}</td>' for i, c in enumerate(row)
        ) + "</tr>"
        for row in rows)
    style = f' style="min-width:{int(min_width)}px"' if min_width else ""
    return f'<div class="pms-tablewrap"><table class="pms-table"{style}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def status_dot_html(status, label):
    return Html(f'<span class="dot dot-{html.escape(status)}" title="{html.escape(label)}"></span>'
                f'<span class="sr"> ({html.escape(label)})</span>')


def legend_html(items):
    """items: list of (status, label)."""
    parts = "".join(f'<span><span class="dot dot-{html.escape(s)}"></span>{esc(l)}</span>' for s, l in items)
    return f'<div class="pms-legend">{parts}</div>'


def verdict_rows_html(rows):
    """rows: list of dicts with name, verdict (open or below), verdict_text, detail, optional caution."""
    out = []
    for r in rows:
        caution = f'<span class="caution">{esc(r["caution"])}</span>' if r.get("caution") else ""
        out.append(
            f'<div class="row"><div class="name">{esc(r["name"])}</div>'
            f'<div class="{html.escape(r["verdict"])}">{esc(r["verdict_text"])}</div>'
            f'<div>{esc(r["detail"])}{caution}</div></div>')
    return f'<div class="pms-rows">{"".join(out)}</div>'


def index_html(entries):
    """entries: list of (name, description)."""
    rows = "".join(f'<div class="row"><div class="name">{esc(n)}</div><div>{esc(d)}</div></div>'
                   for n, d in entries)
    return f'<div class="pms-index">{rows}</div>'


def footnote_html(text):
    return f'<div class="pms-foot">{esc(text)}</div>'


# ---------- render helpers ----------
def _render(markup):
    st.markdown(markup, unsafe_allow_html=True)


def masthead(title, deck=None):
    _render(masthead_html(title, deck))


def section(title, note=None):
    _render(section_html(title, note))


def stat_strip(stats):
    _render(stat_strip_html(stats))


def notice(title, items=None, text=None):
    _render(notice_html(title, items, text))


def data_table(headers, rows, numeric_cols=(), min_width=None):
    _render(data_table_html(headers, rows, numeric_cols, min_width))


def footnote(text):
    _render(footnote_html(text))


# ---------- charts ----------
def style_chart(chart):
    """Give an Altair chart the same paper, ink and hairline look as the pages."""
    return (chart.configure(background=PAPER)
            .configure_view(stroke=None)
            .configure_axis(labelFont=BODY_FONT, titleFont=BODY_FONT, labelColor=MUTED,
                            titleColor=MUTED, gridColor=RULE, gridOpacity=0.7, domainColor=RULE,
                            tickColor=RULE, labelFontSize=12, titleFontSize=12,
                            titleFontWeight="normal")
            .configure_legend(labelFont=BODY_FONT, labelColor=INK, labelFontSize=13,
                              symbolType="stroke", symbolStrokeWidth=3))


def show_chart(chart):
    st.altair_chart(style_chart(chart), theme=None)


__all__ = ["Html", "alt"]
