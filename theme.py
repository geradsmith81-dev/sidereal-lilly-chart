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
  brass       #e6c06a  primary accent: planets above the horizon, metric values, buttons
  brass_pale  #f6dc9b  headings
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

# Elections calendar: lightness rises from Avoid to Best, so the order also reads in greyscale.
GRADE_COLOURS = {'avoid': '#20233f', 'fair': '#3f4680', 'good': PALETTE['nebula'], 'best': PALETTE['brass']}


def css(bg_path='assets/background.jpg', phone=False):
    """phone=True: use the smaller portrait copy of the background (assets/background_phone.jpg) if present."""
    p = PALETTE
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
    [data-testid="stMetricValue"] {{ color: {p['brass']}; font-family: Georgia, serif; }}
    [data-testid="stCaptionContainer"], .stCaption {{ color: {p['dust']} !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {p['orbit']} !important;
        background: rgba(27,32,69,0.55); }}
    blockquote {{ border-left: 3px solid {p['brass']}99 !important; }}
    code {{ color: {p['brass_pale']}; background: rgba(230,192,106,0.10); }}
    a {{ color: {p['ion']}; }}
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
    .lilly-day b {{ color: {p['brass_pale']}; margin-right: 0.4rem; }}
    .lilly-badge {{ padding: 0.08rem 0.5rem; border-radius: 0.6rem; font-weight: 600; white-space: nowrap;
        border: 1px solid {p['orbit']}; margin-right: 0.25rem; }}
    </style>"""
