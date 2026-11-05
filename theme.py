"""Cosmic theme, "Astrolabe and nebula": designed for this app (not taken from a photograph).

A deep indigo night, brass accents like the engraved metal of an astrolabe, and nebula tones for the
secondary colours. The background, assets/background.jpg, is a starfield generated in code (a seeded
random Milky Way band of violet, magenta and teal clouds with dust lanes, and about 4,000 stars).
Text contrast is at least 4.5:1 everywhere, even over the brightest star behind a panel.

Palette roles:
  void        #0a0c1c  page base, wheel face
  panel       #131733  panels and cards
  band_a/b    #1b2045 / #262c5a  alternating constellation bands on the wheel
  orbit       #5d64a0  rings, house lines, borders (decoration only, not text)
  starlight   #f3eee2  body text
  dust        #b7bcd9  secondary text, captions
  brass       #e6c06a  primary accent (not used for text): planets above the horizon, buttons, sliders, 'Best'
  brass_pale  #f6dc9b  headings - the only gold text (all other gold text is white, user request)
  ion         #6fd6d8  sextile / trine aspect lines
  ember       #f08a5d  square / opposition aspect lines
  nebula      #a98ae6  'Good' on the elections calendar
  rose        #ef8fb8  off-zodiac flag (a body outside the 13 ecliptic constellations)
"""
import base64, os

PALETTE = {'void': '#0a0c1c', 'panel': '#131733', 'band_a': '#1b2045', 'band_b': '#262c5a', 'orbit': '#5d64a0',
           'starlight': '#f3eee2', 'dust': '#b7bcd9', 'brass': '#e6c06a', 'brass_pale': '#f6dc9b',
           'ion': '#6fd6d8', 'ember': '#f08a5d', 'nebula': '#a98ae6', 'rose': '#ef8fb8'}

WHEEL_THEME = dict(
    fig_bg='none', face=PALETTE['void'], face_alpha=0.85, band_a=PALETTE['band_a'], band_b=PALETTE['band_b'],
    band_edge=PALETTE['void'], band_text=PALETTE['starlight'], ring=PALETTE['orbit'], ink=PALETTE['starlight'],
    grey=PALETTE['dust'], up=PALETTE['brass'], down_face=PALETTE['void'], accent=PALETTE['rose'],
    label_bg=PALETTE['void'], harmony=PALETTE['ion'], tension=PALETTE['ember'], house_line=PALETTE['orbit'],
    harmony_name='teal', tension_name='orange', accent_name='Pink')

# Phone layout: all text except headings is pure white (user request), on the wheel and calendar too.
WHITE = '#ffffff'
WHEEL_THEME_PHONE = dict(WHEEL_THEME, ink=WHITE, grey=WHITE, band_text=WHITE, spoke=PALETTE['dust'], accent_what='circle',
                         glyph_open=WHITE)   # symbol of a planet below the horizon: white inside its coloured ring

# Elections calendar: lightness rises from Avoid to Best, so the order also reads in greyscale.
GRADE_COLOURS = {'avoid': '#20233f', 'fair': '#3f4680', 'good': PALETTE['nebula'], 'best': PALETTE['brass']}


# Phone layout: all text except headings is white (user request). Built as one selector without line breaks inside
# it: in CSS a space or line break between ":is(...)" and ":not(...)" would mean "an element inside", not "and".
_WHITE_TARGETS = ', '.join([
    'p', 'li', 'span', 'label', 'small', 'summary', 'a', 'code', 'blockquote', 'td', 'th', 'b', 'strong', 'em',
    '[data-testid="stMarkdownContainer"]', '[data-testid="stMarkdownContainer"] *',
    '[data-testid="stCaptionContainer"]', '[data-testid="stCaptionContainer"] *',
    '[data-testid="stMetricValue"]', '[data-testid="stMetricValue"] *', '[data-testid="stMetricLabel"] *',
    '[data-testid="stSidebarNav"] *', '[data-baseweb="select"] *', '[role="option"]', '[role="option"] *',
    '[data-testid="stExpander"] summary *', '[data-testid="stAlert"] *'])
_NOT_WHITE = (':not(.lilly-badge)'                                    # grade labels keep their own colours
              ':not(:is(h1, h2, h3, h4, h5, h6))'                     # headings keep gold
              ':not(:is(h1, h2, h3, h4, h5, h6) *)'
              ':not([data-testid="stBaseButton-primary"] *)'          # the gold button keeps its own text colour
              ':not(.lilly-table *)')                                 # tables: black on parchment (below)
WHITE_SELECTOR = f'body :is({_WHITE_TARGETS}){_NOT_WHITE}'
PHONE_TEXT_CSS = (
    '/* phone layout: all text white except headings, grade labels and the gold button */\n'
    f'    {WHITE_SELECTOR} {{ color: #ffffff !important; }}\n'
    '    body input, body textarea { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }\n'
    '    body a:not(button *) { text-decoration: underline; }\n'
    '    body .lilly-badge[data-g="avoid"], body .lilly-badge[data-g="fair"] { color: #ffffff !important; }\n'
    '    body :is(h4, h5, h6) { color: BRASS_PALE !important; }\n'
    '    /* phone tables (device.html_table): black text on parchment, headings included */\n'
    '    .lilly-table-wrap { overflow-x: auto; margin: 0.25rem 0 0.9rem; border-radius: 8px; border: 1px solid #5d64a0; }\n'
    '    .lilly-table { border-collapse: collapse; width: 100%; margin: 0; font-size: 0.9rem; line-height: 1.35; }\n'
    '    .lilly-table th, .lilly-table td { color: #000000 !important; text-align: left; vertical-align: top;\n'
    '        padding: 0.32rem 0.5rem; border: none; border-bottom: 1px solid #d3c9ae; }\n'
    '    .lilly-table th { background: #e4dac2 !important; font-weight: 700; white-space: nowrap; }\n'
    '    .lilly-table td { background: #f3eee2 !important; min-width: 3.5rem; }\n'
    '    .lilly-table a { color: #000000 !important; text-decoration: underline; }\n')


def css(bg_path='assets/background.jpg', phone=False):
    """phone=True: use the smaller portrait copy of the background (assets/background_phone.jpg) if present,
    and make all text except headings white."""
    p = PALETTE
    phone_css = PHONE_TEXT_CSS.replace('BRASS_PALE', p['brass_pale']) if phone else ''
    bg = ''
    if phone:
        small = os.path.join(os.path.dirname(bg_path), 'background_phone.jpg')
        bg_path = small if os.path.exists(small) else bg_path
    if os.path.exists(bg_path):
        b64 = base64.b64encode(open(bg_path, 'rb').read()).decode()
        bg = (f"background-image: linear-gradient(180deg, rgba(10,12,28,0.35) 0%, rgba(10,12,28,0.60) 55%, "
              f"rgba(10,12,28,0.90) 100%), url('data:image/jpeg;base64,{b64}');"
              "background-size: cover; background-position: center top; background-attachment: fixed;")
    return f"""<style>
    .stApp {{ {bg} }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] > div:first-child {{ background: rgba(19,23,51,0.85); backdrop-filter: blur(6px);
        border-right: 1px solid {p['orbit']}66; }}
    .block-container {{ background: rgba(19,23,51,0.70); border-radius: 16px; padding: 2rem 2.2rem 2.5rem;
        margin-top: 1.2rem; backdrop-filter: blur(5px); border: 1px solid {p['orbit']}55; }}
    h1, h2, h3 {{ font-family: Georgia, 'Palatino Linotype', 'Book Antiqua', serif !important;
        color: {p['brass_pale']} !important; letter-spacing: 0.01em; }}
    h1 {{ text-shadow: 0 0 18px {p['brass']}44; }}
    [data-testid="stMetricValue"] {{ color: #ffffff; font-family: Georgia, serif; }}
    [data-testid="stCaptionContainer"], .stCaption {{ color: {p['dust']} !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {p['orbit']} !important;
        background: rgba(27,32,69,0.55); }}
    blockquote {{ border-left: 3px solid {p['brass']}99 !important; }}
    code {{ color: #ffffff; background: rgba(230,192,106,0.10); }}
    a {{ color: {p['ion']}; }}
    /* gold is kept for headings only (user request): Streamlit draws some text in the accent colour - the value
       above a slider handle, the selected or hovered tab, and buttons while hovered or pressed - make it white.
       The gold primary button keeps its own text colour. */
    [data-testid="stSliderThumbValue"], [data-testid="stSliderThumbValue"] *,
    [data-testid="stTab"], [data-testid="stTab"] * {{ color: #ffffff !important; }}
    button:is(:hover, :active, :focus, :focus-visible):not([data-testid="stBaseButton-primary"]),
    button:is(:hover, :active, :focus, :focus-visible):not([data-testid="stBaseButton-primary"]) * {{ color: #ffffff !important; }}
    [data-testid="stExpander"] summary:hover, [data-testid="stExpander"] summary:hover * {{ color: #ffffff !important; }}
    /* touch screens (phones, tablets): iPhones and iPads ignore a fixed background, so let it scroll */
    @media (hover: none) and (pointer: coarse) {{
        .stApp {{ background-attachment: scroll; }}
    }}
    /* narrow screens (phones held upright): tighter panel, smaller headings */
    @media (max-width: 640px) {{
        .block-container {{ padding: 1.1rem 0.85rem 1.6rem; margin-top: 0.4rem; border-radius: 12px; }}
        h1 {{ font-size: 1.55rem !important; line-height: 1.25 !important; }}
        h2 {{ font-size: 1.3rem !important; }}
        h3 {{ font-size: 1.15rem !important; }}
        h4 {{ font-size: 1.05rem !important; }}
        [data-testid="stMetricValue"] {{ font-size: 1.45rem; }}
        .lilly-day {{ font-size: 1.02rem; }}
    }}
    .lilly-day {{ padding: 0.32rem 0; border-bottom: 1px solid {p['orbit']}44; line-height: 1.9; }}
    .lilly-day b {{ color: #ffffff; margin-right: 0.4rem; }}
    {phone_css}
    .lilly-badge {{ padding: 0.08rem 0.5rem; border-radius: 0.6rem; font-weight: 600; white-space: nowrap;
        border: 1px solid {p['orbit']}; margin-right: 0.25rem; }}
    </style>"""
