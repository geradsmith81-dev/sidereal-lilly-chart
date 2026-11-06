"""Chart page: the dialog 'The forecast in plain English'.

It restates the Forecast box without the technical terms, in three parts:
  1. In short: the overall picture (how many good signs and warning signs, and whether Lilly's
     cautions before judgment apply);
  2. the same lines in plain English (column 'plain' of data/forecast_rules.csv);
  3. the four undertakings of the Auspicious dates page (romance, friendship, life transition, project),
     judged for this exact moment with the same rules (electional.judge) and graded against the other
     hours of the surrounding week, as the Auspicious dates page grades against its period.
"""
import datetime as dt
from zoneinfo import ZoneInfo

import streamlit as st

import electional as el
import lilly_layer as ll
import theme
import user_profile

ORDER = ('romance', 'friendship', 'transition', 'project')
SHORT = {'romance': 'Romance', 'friendship': 'Friendship', 'transition': 'Life transition', 'project': 'Project'}
GRADE_TXT = {'best': 'Best', 'good': 'Good', 'fair': 'Fair', 'avoid': 'Avoid'}
GRADE_MEANING = {
    'best': 'This moment is one of the best tenth of hours this week.',
    'good': 'This moment is better than most hours this week.',
    'fair': 'This is an ordinary hour: no warning, but nothing special.',
    'avoid': "One of Lilly's warnings applies at this moment, so he would not begin it now.",
}
# Lilly's "Considerations before Judgment" (pp.121-123): signs that the chart may not be safe to read at all.
CAUTIONS = {'not_radical', 'asc_early', 'asc_late', 'asc_ophiuchus', 'moon_via_combusta', 'moon_late',
            'saturn_7', 'lord_7_afflicted', 'testimonies_equal'}
GLOSSARY = [
    ('Rising sign (Ascendant)', 'The constellation coming up over the eastern horizon at this moment. '
                                'Lilly takes it to stand for the person: you, or whoever asks the question.'),
    ('Lord of the Ascendant', 'The planet that rules the rising sign. In this window it is called "the planet that '
                              'stands for you".'),
    ('Planetary day and hour', 'Each day and each of its 24 unequal hours (12 from sunrise to sunset, 12 from sunset '
                               'to sunrise) belongs to one of the seven planets, in a fixed order.'),
    ('Radical', "Lilly's first test of whether a chart is fit to be read: the planet of the hour and the planet that "
                'stands for you must agree (be the same planet, share a triplicity, or share a nature).'),
    ('Fortitudes and debilities', "Lilly's points for and against each planet (his table on p.115). The net score is "
                                  'fortitudes minus debilities.'),
    ('Houses', 'Twelve divisions of the sky, each standing for a part of life: the 7th for partners and love, the '
               '11th for friends and hopes, the 4th for home and endings, the 10th for work and reputation. The four '
               '"angles" (1st, 4th, 7th, 10th) are the strongest places; the "cadent" ones (3rd, 6th, 9th, 12th) the weakest.'),
    ('Helpful and harmful planets', 'Jupiter and Venus are the "fortunes" (helpful); Saturn and Mars the "infortunes" '
                                    '(harmful).'),
    ('Aspects', 'Set angles between two planets. Sextile (60°) and trine (120°) are friendly; square (90°) and '
                'opposition (180°) are hard; a conjunction (0°) is a meeting. "Applying" means the angle is about to be exact.'),
    ('Combust and cazimi', 'A planet within 8½° of the Sun is "combust", lost in its glare and badly weakened. '
                           'Within 17 arc-minutes of the Sun\'s centre it is "cazimi", and strengthened instead.'),
    ('Void of course', 'The Moon makes no further aspect before she leaves the constellation she is in.'),
    ('Via Combusta', 'The "burnt road", the second half of Libra and the first half of Scorpio, which Lilly thought '
                     'unlucky for the Moon.'),
    ('Mutual reception', 'Two planets each standing in a sign the other rules: a sign of cooperation.'),
    ('Part of Fortune', 'A calculated point (Ascendant + Moon − Sun) standing for wealth and well-being.'),
]


def tz_from_key(tzkey):
    return ZoneInfo(tzkey) if not tzkey.startswith('UTC') else dt.timezone(dt.timedelta(hours=float(tzkey[3:])))


@st.cache_data(show_spinner=False, max_entries=8, ttl=3600)
def week(lat, lon, elev, tzkey, start, beams_rule):
    """The four undertakings over 7 days from `start`, every hour of the day (00:00-23:00 local).
    Returns, per undertaking, the grade thresholds and the best window of the week."""
    res, _ = el.scan_many(ORDER, lat, lon, elev, tz_from_key(tzkey), start, 7, 0, 24, 60, beams_rule)
    out = {}
    for k in ORDER:
        q = el.grade(res[k])
        wins = el.windows(res[k])
        best = None
        if wins:
            w = wins[0]
            best = dict(date=w['date'], start=w['start'], end=w['end'] + dt.timedelta(minutes=60), grade=w['grade'])
        out[k] = dict(q=q, best=best, n=len(res[k]), n_avoid=sum(r['grade'] == 'avoid' for r in res[k]))
    return out


def week_start(d):
    """Three days before to three days after the chart date, kept inside the ephemeris range (1850-2149)."""
    s = d - dt.timedelta(days=3)
    return min(max(s, dt.date(1850, 1, 1)), dt.date(2149, 12, 25))


def grade_moment(j, q):
    if j['avoid']:
        return 'avoid'
    if q is None:                     # every hour of the week has a warning; this moment has none
        return 'good'
    q90, q65 = q
    return 'best' if j['score'] >= q90 else 'good' if j['score'] >= q65 else 'fair'


def badge(g):
    fg = theme.PALETTE['void'] if g in ('good', 'best') else theme.PALETTE['starlight']
    return (f"<span class='lilly-badge' data-g='{g}' style='background:{theme.GRADE_COLOURS[g]};color:{fg};padding:0.1rem 0.55rem;border-radius:0.6rem;"
            f"font-weight:600;border:1px solid {theme.PALETTE['orbit']}'>{GRADE_TXT[g]}</span>")


def overview(fc, R):
    s, w = fc['strengths'], fc['weaknesses']
    cautions = [x for x in w if x.get('id') in CAUTIONS]
    lines = []
    lord = R['lord_of_asc']
    if lord:
        P = {p['planet']: p for p in R['planets']}
        n = P[lord]['net']
        word = ('strong' if n >= 5 else 'fairly strong' if n > 0 else 'neither strong nor weak' if n == 0
                else 'fairly weak' if n > -5 else 'weak')
        lines.append(f"**{R['asc']['constellation']}** is rising, so **{lord}** is the planet that stands for you. "
                     f"By Lilly's points it is **{word}** (net {n:+d}), in the {ll._ord(P[lord]['house'])} house.")
    else:
        lines.append(f"**{R['asc']['constellation']}** is rising. It has no sign in Lilly, so no planet stands for you, "
                     'and several of his tests cannot be made.')
    tally = f"The Forecast found **{len(s)} good sign{'s' if len(s) != 1 else ''}** and **{len(w)} warning sign{'s' if len(w) != 1 else ''}**."
    if len(s) > len(w) + 1:
        tally += ' On balance the picture is **encouraging**.'
    elif len(w) > len(s) + 1:
        tally += ' On balance the picture is **discouraging**.'
    else:
        tally += ' On balance the picture is **mixed**.'
    lines.append(tally)
    if cautions:
        lines.append(f"{len(cautions)} of the warnings {'is' if len(cautions) == 1 else 'are'} among Lilly's "
                     "*considerations before judgment* (marked ⚠ below). For Lilly these do not say that things will go "
                     'badly; they say that this chart may not be safe to read at all, so he would treat its other '
                     'signs with caution.')
    return '\n\n'.join(lines)


def _plain_list(xs, empty):
    if not xs:
        return f'_{empty}_'
    return '\n'.join(f"- {'⚠ ' if x.get('id') in CAUTIONS else ''}{x.get('plain') or x['text']}" for x in xs)


def _reasons(plain, kinds, n=2):
    xs = [x for x in plain if x[3] in kinds]
    xs.sort(key=lambda x: (x[3] != 'avoid', -abs(x[2])))
    return xs[:n]


@st.dialog('The forecast in plain English', width='large')
def show(fc, R, rows, bands, cusps, stars, ph, lat, lon, elev, tzkey, local, beams_rule, place):
    name = user_profile.get()['name']
    st.caption(f"{place} · {local:%A %d %B %Y, %H:%M} local time"
               + (f" · prepared for {name}" if name else ''))
    st.markdown('The **Forecast** box reads the chart of this moment the way William Lilly read a chart cast for a '
                "question put to him. It looks for good signs and warning signs in his rules. This window says the "
                'same things without the technical terms.')

    st.markdown('#### In short')
    st.markdown(overview(fc, R))

    st.markdown('#### What the Forecast is saying')
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('**Good signs**')
        st.markdown(_plain_list(fc['strengths'], 'None under the current rules.'))
    with c2:
        st.markdown('**Warning signs**')
        st.markdown(_plain_list(fc['weaknesses'], 'None under the current rules.'))

    st.markdown('#### If you began something at this moment')
    st.markdown('The **Auspicious dates** page uses the same rules to look for good times to begin four kinds of '
                'undertaking. Here each one is judged for this exact moment. The grade compares this moment with every '
                'hour of the surrounding week, as the Auspicious dates page compares the times in its period.')
    rules = el.load_rules()
    start = week_start(local.date())
    with st.spinner('Comparing this moment with the rest of the week ...'):
        W = week(lat, lon, elev, tzkey, start, beams_rule)
    cols = st.columns(2)
    for i, k in enumerate(ORDER):
        u = el.UNDERTAKINGS[k]
        j = el.judge(rows, bands, cusps, stars, R['sun_up'], k, ph['hour_ruler'], rules, beams_rule)
        g = grade_moment(j, W[k]['q'])
        with cols[i % 2].container(border=True):
            st.markdown(f"**{SHORT[k]}** &nbsp; {badge(g)}", unsafe_allow_html=True)
            st.caption(f"{u['label']} · read from the {ll._ord(u['house'])} house and {u['natural']}")
            st.markdown(GRADE_MEANING[g])
            good = _reasons(j['plain'], ('good',))
            bad = _reasons(j['plain'], ('avoid', 'bad'))
            if good:
                st.markdown('**Helping:**\n' + '\n'.join(f'- {t}' for _, t, _, _ in good))
            if bad:
                st.markdown('**Against:**\n' + '\n'.join(f"- {'⚠ ' if kk == 'avoid' else ''}{t}" for _, t, _, kk in bad))
            b = W[k]['best']
            if b:
                st.caption(f"Best time this week: {b['start']:%a %d %b}, {b['start']:%H:%M}–{b['end']:%H:%M} "
                           f"({GRADE_TXT[b['grade']]}).")
            else:
                st.caption('Every hour this week has one of Lilly\'s warnings for this undertaking.')
    st.caption(f"Week compared: {start:%d %b} to {start + dt.timedelta(days=6):%d %b %Y}, every hour, at {place}. "
               'For other weeks, other hours or finer time steps, use the Auspicious dates page. '
               'Grades are relative (an app rule): Best is the top tenth of the hours without a warning, Good the next quarter.')

    with st.expander('Words used in the Forecast'):
        st.markdown('\n'.join(f'- **{t}**: {d}' for t, d in GLOSSARY))

    st.info('This is a reading in the terms of a 1647 book, for study and reflection. Controlled studies have not found '
            'astrological charts to predict events, so please do not base important decisions on it.')

# ---------------------------------------------------------------- the Strengths and the Weaknesses, each in its own window
def _rule_items(items):
    for x in items:
        with st.container(border=True):
            st.markdown(('⚠ ' if x.get('id') in CAUTIONS else '') + x['text'])
            basis = str(x.get('basis') or '')
            st.caption(x['source'] + (f' · {basis}' if basis and basis != 'nan' else ''))


def _rule_header(place, local):
    name = user_profile.get()['name']
    st.caption(f"{place} · {local:%A %d %B %Y, %H:%M} local time" + (f" · prepared for {name}" if name else ''))


@st.dialog('Strengths', width='large')
def show_strengths(fc, place, local):
    _rule_header(place, local)
    st.markdown("Lilly's rules that **favour** this moment, in his words, each with the page of *Christian Astrology* "
                "(1647) it comes from.")
    if fc['strengths']:
        _rule_items(fc['strengths'])
    else:
        st.info('None of the strengths in Lilly\'s rules apply at this moment.')
    st.caption('For the same in plain English, close this window and press "What does this mean? (plain English)".')


@st.dialog('Weaknesses', width='large')
def show_weaknesses(fc, place, local):
    _rule_header(place, local)
    st.markdown("Lilly's rules that **count against** this moment, in his words, each with the page of *Christian "
                "Astrology* (1647) it comes from. Lines marked ⚠ are among his *considerations before judgment*: they "
                "warn that the chart may not be safe to read at all, rather than that things will go badly.")
    if fc['weaknesses']:
        _rule_items(fc['weaknesses'])
    else:
        st.info('None of the weaknesses in Lilly\'s rules apply at this moment.')
    st.caption('For the same in plain English, close this window and press "What does this mean? (plain English)".')
