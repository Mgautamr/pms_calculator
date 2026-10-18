from app import theme


def test_text_is_escaped():
    out = theme.stat_strip_html([{"label": "<i>x</i>", "value": "<script>1</script>", "note": "a&b"}])
    assert "<script>" not in out and "&lt;script&gt;" in out and "a&amp;b" in out


def test_trusted_markup_is_not_escaped():
    cell = theme.Html("<b>ok</b>")
    assert "<b>ok</b>" in theme.data_table_html(["h"], [[cell]])


def test_html_has_no_blank_lines_or_indented_lines():
    # Markdown would break the HTML block at a blank line or turn indentation into code.
    parts = [
        theme.masthead_html("Title", "Deck"),
        theme.section_html("Heading", "Note"),
        theme.stat_strip_html([{"label": "L", "value": "V", "note": "N", "tone": "good"}]),
        theme.notice_html("Open", items=["one", "two"]),
        theme.data_table_html(["A", "B"], [["1", "2"]], numeric_cols=(1,), min_width=500),
        theme.verdict_rows_html([{"name": "N", "verdict": "open", "verdict_text": "Yes", "detail": "d"}]),
        theme.index_html([("n", "d")]),
        theme.legend_html([("official", "Official")]),
        theme.footnote_html("f"),
    ]
    for html in parts:
        assert "\n" not in html


def test_only_the_first_stat_is_the_lead():
    out = theme.stat_strip_html([{"label": "a", "value": "1"}, {"label": "b", "value": "2"}])
    assert out.count("pms-stat lead") == 1


def test_numeric_columns_are_marked():
    out = theme.data_table_html(["Name", "Amount"], [["x", "1"]], numeric_cols=(1,))
    assert out.count('class="num"') == 2  # header and cell of the second column


def test_status_dot_has_text_for_screen_readers():
    dot = theme.status_dot_html("secondary", "Secondary source")
    assert "dot-secondary" in dot and "Secondary source" in dot


def test_palette_and_status_classes_exist_in_css():
    for status in ("official", "official_reported", "legal_database", "secondary", "not_verified"):
        assert f".dot-{status}" in theme.CSS
    assert theme.SAFFRON in theme.CSS and theme.PAPER in theme.CSS
