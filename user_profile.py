"""The user's profile (name, picture, birth details) and their friends' cards.

Where it is kept
  * Desktop app (started with "Start app.bat", which sets LILLY_LOCAL_PROFILE=1): in the folder profile/ inside the
    app (profile.json, avatar.png, friends.json), so it is there next time. It never leaves the computer.
  * Online (Streamlit Community Cloud) or any other start: only for the current browser session. The server's disk
    is shared by every visitor, so nothing is written there.

Friend cards
  A friend card is a small JSON file (.lillycard) or a copy-paste text code ("LILLY1:..."), holding a name, the birth
  details and, if the sender chooses, the picture. It is sent person to person (e-mail, message); the app has no
  accounts and no server. Imported cards are validated and the picture is re-encoded before use.
"""
import base64
import calendar
import datetime as dt
import html
import io
import json
import os
import re
import uuid
import zlib

import streamlit as st
from PIL import Image, ImageOps

import places

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, 'profile')
LOCAL = os.environ.get('LILLY_LOCAL_PROFILE') == '1'
MAX_NAME = 40
MAX_UPLOAD_MB = 15
MAX_CARD_KB = 1024
AVATAR_PX = 256
KEY, FKEY = 'profile', 'friends'
CARD_FORMAT = 'lilly-friend-card'
CODE_PREFIX = 'LILLY1:'


# ---------------------------------------------------------------- storage
def _read_json(name, default):
    try:
        with open(os.path.join(DIR, name), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write_json(name, obj):
    os.makedirs(DIR, exist_ok=True)
    tmp = os.path.join(DIR, name + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(DIR, name))


def _read_disk():
    d = _read_json('profile.json', {})
    av = None
    p = os.path.join(DIR, 'avatar.png')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            av = f.read()
    return dict(name=d.get('name', ''), avatar=av, birth=_valid_birth(d.get('birth')))


def _write_disk(prof):
    _write_json('profile.json', {'name': prof['name'], 'birth': prof.get('birth')})
    p = os.path.join(DIR, 'avatar.png')
    if prof['avatar']:
        with open(p + '.tmp', 'wb') as f:
            f.write(prof['avatar'])
        os.replace(p + '.tmp', p)
    elif os.path.exists(p):
        os.remove(p)


def get():
    """The current profile: dict(name=str, avatar=PNG bytes or None, birth=dict or None)."""
    if KEY not in st.session_state:
        st.session_state[KEY] = _read_disk() if LOCAL else dict(name='', avatar=None, birth=None)
    st.session_state[KEY].setdefault('birth', None)
    return st.session_state[KEY]


def save(name, avatar, birth):
    prof = dict(name=clean_name(name), avatar=avatar, birth=_valid_birth(birth))
    st.session_state[KEY] = prof
    if LOCAL:
        _write_disk(prof)


def friends():
    if FKEY not in st.session_state:
        raw = _read_json('friends.json', []) if LOCAL else []
        st.session_state[FKEY] = [f for f in (_friend_from_store(x) for x in raw) if f]
    return st.session_state[FKEY]


def _store_friends():
    if LOCAL:
        _write_json('friends.json', [dict(id=f['id'], name=f['name'], birth=f['birth'],
                                          avatar=base64.b64encode(f['avatar']).decode() if f['avatar'] else None)
                                     for f in friends()])


def _friend_from_store(x):
    try:
        av = base64.b64decode(x['avatar']) if x.get('avatar') else None
        b = _valid_birth(x.get('birth'))
        return dict(id=str(x['id']), name=clean_name(x['name']), birth=b, avatar=av) if b else None
    except Exception:
        return None


def add_friend(f):
    """f: dict from parse_card. Replaces an earlier card of the same person (same name and birth)."""
    lst = [x for x in friends() if not (x['name'] == f['name'] and x['birth'] == f['birth'])]
    lst.append(dict(f, id=uuid.uuid4().hex[:12]))
    st.session_state[FKEY] = lst
    _store_friends()


def remove_friend(fid):
    st.session_state[FKEY] = [x for x in friends() if x['id'] != fid]
    _store_friends()


# ---------------------------------------------------------------- validation and helpers
def clean_name(name):
    """Trim, collapse spaces, drop control characters, at most MAX_NAME characters."""
    name = re.sub(r'[\x00-\x1f\x7f]', '', str(name or ''))
    return re.sub(r'\s+', ' ', name).strip()[:MAX_NAME]


def _valid_birth(b):
    """Return a clean birth dict, or None. Fields: date YYYY-MM-DD, time HH:MM, time_known, place, lat, lon,
    tz (IANA name or None), utc_offset (hours, of the local clock at birth)."""
    if not isinstance(b, dict):
        return None
    try:
        d = dt.date.fromisoformat(str(b['date']))
        t = dt.time.fromisoformat(str(b.get('time') or '12:00'))
        lat, lon, off = float(b['lat']), float(b['lon']), float(b['utc_offset'])
        if not (1850 <= d.year <= 2149 and -90 <= lat <= 90 and -180 <= lon <= 180 and -14 <= off <= 14):
            return None
        tz = b.get('tz')
        tz = str(tz)[:64] if tz else None
        return dict(date=d.isoformat(), time=t.strftime('%H:%M'), time_known=bool(b.get('time_known', True)),
                    place=clean_name(b.get('place', ''))[:MAX_NAME] or f'{lat:.2f}, {lon:.2f}',
                    lat=round(lat, 5), lon=round(lon, 5), tz=tz, utc_offset=off)
    except (KeyError, ValueError, TypeError):
        return None


def birth_utc(b):
    """UTC datetime of a birth dict (noon local if the time is unknown)."""
    local = dt.datetime.combine(dt.date.fromisoformat(b['date']), dt.time.fromisoformat(b['time']))
    return (local - dt.timedelta(hours=b['utc_offset'])).replace(tzinfo=dt.timezone.utc)


def birth_text(b):
    if not b:
        return 'no birth details'
    d = dt.date.fromisoformat(b['date'])
    t = b['time'] if b['time_known'] else 'time unknown'
    return f"born {d:%d %b %Y}, {t}, {b['place']}"


def _md_escape(s):
    """Stop Markdown from formatting a name such as *Star* or [link]."""
    return re.sub(r'([\\`*_{}\[\]<>()#+!|~])', r'\\\1', s)


def possessive(name):
    return f"{name}'" if name.lower().endswith('s') else f"{name}'s"


def personal(base, name_form):
    """base: the title without a name. name_form: the same title with {who} where the possessive goes."""
    n = get()['name']
    return name_form.format(who=possessive(n)) if n else base


def to_avatar(file_bytes):
    """Picture -> square PNG, AVATAR_PX pixels, turned upright from the camera's EXIF."""
    im = Image.open(io.BytesIO(file_bytes))
    im = ImageOps.exif_transpose(im).convert('RGB')
    s = min(im.size)
    left, top = (im.width - s) // 2, (im.height - s) // 2
    im = im.crop((left, top, left + s, top + s)).resize((AVATAR_PX, AVATAR_PX), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, format='PNG', optimize=True)
    return out.getvalue()


def img_html(png, size, border='#e6c06a'):
    b64 = base64.b64encode(png).decode()
    return (f'<img src="data:image/png;base64,{b64}" width="{size}" height="{size}" alt="profile picture" '
            f'style="border-radius:50%; object-fit:cover; border:2px solid {border}; box-shadow:0 0 14px {border}44;">')


def initials_html(name, size, border='#e6c06a'):
    ini = ''.join(w[0] for w in name.split()[:2]).upper() or '✦'
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;border:2px solid {border};'
            f'display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;'
            f'font-size:{size * 0.4:.0f}px;color:#ffffff;background:rgba(230,192,106,0.08);">{html.escape(ini)}</div>')


def person_avatar(p, size=64, border='#e6c06a'):
    if p.get('avatar'):
        return img_html(p['avatar'], size, border)
    if p.get('name'):
        return initials_html(p['name'], size, border)
    return ''


def avatar_html(size=64):
    return person_avatar(get(), size)


# ---------------------------------------------------------------- friend cards
def make_card(include_picture=True):
    p = get()
    card = {'format': CARD_FORMAT, 'version': 1, 'name': p['name'], 'birth': p['birth']}
    if include_picture and p['avatar']:
        card['picture_png_base64'] = base64.b64encode(p['avatar']).decode()
    return card


def card_file(include_picture=True):
    return json.dumps(make_card(include_picture), ensure_ascii=False, indent=1).encode('utf-8')


def card_code():
    """Short text code without the picture: LILLY1:<base64url(zlib(json))>."""
    raw = json.dumps(make_card(False), ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return CODE_PREFIX + base64.urlsafe_b64encode(zlib.compress(raw, 9)).decode().rstrip('=')


def parse_card(data):
    """data: bytes of a .lillycard file, or the text code. Returns a friend dict; raises ValueError (plain message)."""
    if isinstance(data, bytes):
        if len(data) > MAX_CARD_KB * 1024:
            raise ValueError('That file is too large to be a friend card.')
        text = data.decode('utf-8', errors='replace').strip()
    else:
        text = str(data).strip()
    if text.startswith(CODE_PREFIX):
        try:
            b = text[len(CODE_PREFIX):].strip()
            b += '=' * (-len(b) % 4)
            text = zlib.decompress(base64.urlsafe_b64decode(b), bufsize=65536).decode('utf-8')
        except Exception:
            raise ValueError('That code could not be read. Check that it was copied completely, starting with LILLY1:')
    try:
        card = json.loads(text)
    except ValueError:
        raise ValueError('That is not a friend card. Ask your friend to send the .lillycard file or the LILLY1: code.')
    if not isinstance(card, dict) or card.get('format') != CARD_FORMAT:
        raise ValueError('That is not a friend card from this app.')
    name = clean_name(card.get('name'))
    birth = _valid_birth(card.get('birth'))
    if not name:
        raise ValueError('The card has no name.')
    if not birth:
        raise ValueError(f'{name}\'s card has no birth details yet. Ask them to add their birth date, time and place '
                         'in their profile and send the card again.')
    av = None
    if card.get('picture_png_base64'):
        try:
            av = to_avatar(base64.b64decode(card['picture_png_base64']))
        except Exception:
            av = None          # a damaged picture is dropped; the rest of the card is still used
    return dict(name=name, birth=birth, avatar=av)


# ---------------------------------------------------------------- the dialog
def _date_inputs(prefix, default):
    y0, m0, d0 = default.year, default.month, default.day
    c1, c2, c3 = st.columns([1.3, 1.4, 1])
    y = c1.number_input('Year', 1850, 2149, y0, 1, key=prefix + '_y')
    m = c2.selectbox('Month', range(1, 13), index=m0 - 1, format_func=lambda k: calendar.month_abbr[k], key=prefix + '_m')
    nd = calendar.monthrange(int(y), int(m))[1]
    d = c3.number_input('Day', 1, nd, min(d0, nd), 1, key=prefix + '_d')
    return dt.date(int(y), int(m), int(d))


@st.dialog('Your profile', width='large')
def edit_dialog():
    p = get()
    b0 = p['birth'] or {}
    st.markdown('**Name and picture**')
    name = st.text_input('Your name', p['name'], max_chars=MAX_NAME, placeholder='e.g. Gerad')
    up = st.file_uploader('Profile picture (JPG, PNG or WEBP)', type=['jpg', 'jpeg', 'png', 'webp'])
    new_av, err = None, None
    if up is not None:
        data = up.getvalue()
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            err = f'That picture is larger than {MAX_UPLOAD_MB} MB. Please choose a smaller one.'
        else:
            try:
                new_av = to_avatar(data)
            except Exception:
                err = 'That file could not be read as a picture. Please try a JPG or PNG.'
    if err:
        st.error(err)
    remove = False
    if p['avatar'] and new_av is None:
        remove = st.checkbox('Remove my current picture', value=False)
    show = new_av if new_av is not None else (None if remove else p['avatar'])
    if show:
        st.markdown(img_html(show, 110), unsafe_allow_html=True)

    st.markdown('**Birth details** (used on the Auspicious dates and Friends pages)')
    has_birth = st.checkbox('Add my birth date, time and place', value=bool(p['birth']), key='pf_has_birth')
    birth = None
    if has_birth:
        bdate = _date_inputs('pf', dt.date.fromisoformat(b0['date']) if b0 else dt.date(1990, 1, 1))
        unknown = st.checkbox('I do not know my birth time', value=not b0.get('time_known', True), key='pf_unknown')
        btime = dt.time(12, 0) if unknown else st.time_input(
            'Birth time (local clock)', dt.time.fromisoformat(b0['time']) if b0 else dt.time(12, 0), step=60, key='pf_time')
        q = st.text_input('Birthplace', b0.get('place', '').split(',')[0] if b0 else '', key='pf_place',
                          placeholder='e.g. London, Mortlake, Kraków')
        hits = places.search(q, n=10) if q else []
        if q and not hits:
            st.warning('No match in the gazetteer (places with at least 1,000 inhabitants). Try a nearby town.')
        if hits:
            same = [k for k, hh in enumerate(hits) if b0 and abs(hh['lat'] - b0['lat']) < 1e-3 and abs(hh['lon'] - b0['lon']) < 1e-3]
            i = st.selectbox('Matches', range(len(hits)), index=same[0] if same else 0,
                             format_func=lambda k: places.label(hits[k]), key='pf_pick')
            h = hits[i]
            local = dt.datetime.combine(bdate, btime)
            off, note = places.utc_offset_hours(h['tz'], local)
            if st.checkbox(f'Override the UTC offset at birth (automatic: {off:+.2f} h)', key='pf_override'):
                off = st.number_input('UTC offset at birth (hours)', -12.0, 14.0, float(off), 0.25, key='pf_off')
            elif note:
                st.caption(note)
            birth = _valid_birth(dict(date=bdate.isoformat(), time=btime.strftime('%H:%M'), time_known=not unknown,
                                      place=f"{h['name']}, {h['country']}", lat=h['lat'], lon=h['lon'], tz=h['tz'],
                                      utc_offset=off))
            st.caption(f"{birth_text(birth)} · {h['lat']:.3f}°, {h['lon']:.3f}° · UTC{off:+.2f}")
        elif b0 and not q:
            birth = p['birth']
    st.caption('On this computer your profile is saved in the app\'s "profile" folder and never leaves it.'
               if LOCAL else
               'Online, your profile is kept only while this browser tab is open; nothing is stored on the server.')
    c1, c2 = st.columns(2)
    if c1.button('Save', type='primary', width='stretch', disabled=bool(err)):
        save(name, show, birth if has_birth else None)
        st.rerun()
    if c2.button('Cancel', width='stretch'):
        st.rerun()


def sidebar_card():
    """Picture, name and the Edit button, at the top of the sidebar on every page."""
    p = get()
    with st.sidebar:
        if p['name'] or p['avatar']:
            st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin:2px 0 6px 0;">{avatar_html(56)}'
                        f'<div><div style="font-family:Georgia,serif;font-size:1.15rem;color:#ffffff;">'
                        f'{html.escape(p["name"]) or "&nbsp;"}</div>'
                        f'<div style="font-size:0.75rem;color:#b7bcd9;">{html.escape(birth_text(p["birth"]))}</div></div></div>',
                        unsafe_allow_html=True)
            label = 'Edit profile'
        else:
            label = 'Add your name and picture'
        if st.button(label, key='profile_btn', icon=':material/account_circle:', width='stretch'):
            edit_dialog()
        st.divider()


def title(base, name_form):
    """Page title with the user's picture beside it, when there is a profile."""
    text = personal(base, name_form)
    text = _md_escape(text) if get()['name'] else text
    av = avatar_html(64)
    if av:
        a, b = st.columns([0.07, 0.93], vertical_alignment='center')
        a.markdown(av, unsafe_allow_html=True)
        b.title(text)
    else:
        st.title(text)
