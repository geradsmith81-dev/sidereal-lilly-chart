"""Shared sidebar inputs: place search (GeoNames) or manual coordinates, and elevation.
The last place query is remembered across the two pages."""
import streamlit as st
import places


@st.cache_data(show_spinner=False, max_entries=64, ttl=3600)
def find_places(q):
    return places.search(q, n=12)


def place_picker(prefix):
    st.subheader('Place')
    manual = st.checkbox('Enter coordinates manually', value=st.session_state.get('_manual', False), key=prefix + '_manual')
    st.session_state['_manual'] = manual
    if not manual:
        q = st.text_input('Search place name', st.session_state.get('_place_q', 'London'), key=prefix + '_q',
                          placeholder='e.g. Mortlake, Kraków, Praha, New York')
        st.session_state['_place_q'] = q
        hits = find_places(q)
        if not hits:
            st.warning('No match in the gazetteer (places with population ≥ 1000). Try another spelling '
                       'or enter coordinates manually.')
            st.stop()
        pick = st.selectbox('Matches', range(len(hits)), format_func=lambda i: places.label(hits[i]), key=prefix + '_pick')
        hit = hits[pick]
        place, lat, lon, tzname = f"{hit['name']}, {hit['country']}", hit['lat'], hit['lon'], hit['tz']
        st.caption(f'{lat:.4f}°, {lon:.4f}° · time zone {tzname}')
    else:
        place = st.text_input('Place label', 'Custom location', key=prefix + '_label')
        lat = st.number_input('Latitude (°N)', -89.0, 89.0, 51.5, 0.0001, format='%.4f', key=prefix + '_lat')
        lon = st.number_input('Longitude (°E)', -180.0, 180.0, 0.0, 0.0001, format='%.4f', key=prefix + '_lon')
        tzname = None
    elev = st.number_input('Elevation (m)', 0.0, 9000.0, 0.0, 10.0, key=prefix + '_elev',
                           help='Not in the gazetteer; affects sunrise (planetary hours) slightly.')
    return place, lat, lon, tzname, elev
