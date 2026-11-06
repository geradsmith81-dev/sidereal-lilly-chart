"""Sidereal Oracle: the real sky read through William Lilly's Christian Astrology (1647) - four pages:
  1. Chart: the chart for one moment, with Lilly's dignities, scores and Forecast.
  2. Auspicious dates: an elections calendar for beginning an undertaking.
  3. Friends: share friend cards, compare two nativities, find times good for both.
  4. About: how the app works and what text informs it.

Run:  streamlit run app.py      (or double-click "Start app.bat")
"""
import os
import streamlit as st
import matplotlib
matplotlib.use('Agg')

import user_profile

st.set_page_config(page_title=user_profile.personal("Sidereal Oracle · William Lilly's reading",
                                                   "{who} Sidereal Oracle · William Lilly's reading"), layout='wide',
                   # the app icon (an astrolabe): browser tab, the app window's title bar and taskbar button
                   page_icon=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'lilly_icon.png'))
try:
    import sidereal_engine  # noqa: F401  (loads, or on first start downloads, the JPL file)
except Exception as e:          # e.g. first start without internet: de440s.bsp cannot be downloaded
    st.error('The NASA JPL planetary data file (de440s.bsp, about 32 MB) could not be loaded or downloaded. '
             'Check the internet connection and reload the page. Details: ' + str(e))
    st.stop()
import theme
import device

HERE = os.path.dirname(os.path.abspath(__file__))
st.markdown(theme.css(os.path.join(HERE, 'assets', 'background.jpg'), phone=device.phone()), unsafe_allow_html=True)
pg = st.navigation([st.Page(os.path.join(HERE, 'chart_page.py'), title='Chart', icon=':material/brightness_7:', default=True),
                    st.Page(os.path.join(HERE, 'elections_page.py'), title='Auspicious dates', icon=':material/calendar_month:'),
                    st.Page(os.path.join(HERE, 'friends_page.py'), title='Friends', icon=':material/group:'),
                    st.Page(os.path.join(HERE, 'about_page.py'), title='About', icon=':material/menu_book:')])
user_profile.sidebar_card()
device.switch()
# credit for the background image (required by its CC BY 4.0 licence), on every page
st.sidebar.caption('Background: Hubble\'s image of the Lagoon Nebula (heic1808a). Credit: NASA, ESA, STScI. '
                   '[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)')
pg.run()
