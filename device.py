"""Phone layout: one switch that the pages consult to fit a small, upright screen.

The switch starts ON when the browser says it is a phone (its "User-Agent" text contains Mobile, iPhone,
iPod or Android) and OFF otherwise. It sits in the sidebar ("Phone layout"), so it can be changed by hand.
With it on:
  * the input boxes move from the sidebar (hidden on a phone) into a fold-out panel at the top of the page;
  * the calendars come first as a day-by-day list in large text, and the coloured grid is drawn at phone size;
  * the chart wheel is drawn with larger symbols and its key is written underneath;
  * tables show their most important columns only;
  * the starfield background is a smaller portrait copy.
Desktop screens are unchanged.
"""
import streamlit as st

KEY = 'phone_layout'
PHONE_WORDS = ('mobi', 'iphone', 'ipod', 'android')


def detected():
    """True when the browser identifies itself as a phone (or an Android tablet)."""
    try:
        ua = (st.context.headers.get('User-Agent') or '').lower()
    except Exception:            # no browser (tests) or an old Streamlit
        ua = ''
    return any(w in ua for w in PHONE_WORDS)


def phone():
    if KEY not in st.session_state:
        st.session_state[KEY] = detected()
    return bool(st.session_state[KEY])


def switch():
    """The sidebar switch. Call once per run, from app.py, before the page runs."""
    phone()
    st.sidebar.toggle('Phone layout', key=KEY,
                      help='Fits the pages to a phone screen: inputs in a panel at the top of the page, calendars as '
                           'lists, larger chart symbols and shorter tables. It switches on by itself on phones.')


def input_panel(label, expanded=False):
    """Where a page puts its inputs: the sidebar on a computer, a fold-out panel on a phone."""
    if phone():
        return st.expander(label, expanded=expanded, icon=':material/tune:')
    return st.sidebar


def where_inputs():
    """Words for the instructions: where the inputs are."""
    return 'in the panel above' if phone() else 'in the sidebar'


def _cell(v):
    """How a cell is written when the table is styled (numbers as short as the plain table shows them)."""
    if v is None or (isinstance(v, float) and v != v):
        return ''
    if isinstance(v, float):
        return f'{v:g}'
    return str(v)


def table(df, phone_cols=None, **kw):
    """A table. On a phone: only the listed columns (all if phone_cols is None), with the cell text in white.
    (The column headings are drawn by Streamlit in the theme's text colour, #f3eee2, a near-white.)"""
    if phone():
        if phone_cols:
            df = df[[c for c in phone_cols if c in df.columns]]
        df = df.style.set_properties(color='#ffffff').format(_cell)
    st.dataframe(df, hide_index=True, width='stretch', **kw)
