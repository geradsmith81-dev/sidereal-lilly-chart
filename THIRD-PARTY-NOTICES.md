# Third-party material in The Sidereal Oracle

The MIT License in `LICENSE` covers the code and texts written for this app. The material below
belongs to others and keeps its own terms; the MIT License does not apply to it.

| What | Where in this app | Terms and credit |
| --- | --- | --- |
| Lagoon Nebula image, "Hubble's 28th birthday picture" (heic1808a), 2018 | `assets/background.jpg`, `assets/background_phone.jpg` (cropped and resized) | Credit: **NASA, ESA, STScI**. [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Source: https://esahubble.org/images/heic1808a/ |
| William Lilly, *Christian Astrology* (London, 1647) | Quotations and page references in `data/*.csv` and `glossary.py` | Public domain. Wellcome Library copy, Internet Archive item b30338724 (Public Domain Mark): https://archive.org/details/b30338724 |
| JPL planetary ephemeris DE440s | `ephem/de440s.bsp` (in the desktop version; downloaded from JPL on first start otherwise) | Produced by NASA's Jet Propulsion Laboratory. Park, Folkner, Williams & Boggs (2021), AJ 161:105. https://ssd.jpl.nasa.gov/planets/eph_export.html |
| Hipparcos Catalogue positions (Regulus, Spica, Algol) | `data/fixed_stars.csv` | ESA (1997), The Hipparcos Catalogue. |
| IAU constellation boundaries (Delporte 1930) | via the Skyfield package | Used through Skyfield's constellation lookup (Roman 1987). |
| GeoNames place names | via the geonamescache package (not stored in this repository) | GeoNames, [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). https://www.geonames.org |
| Python packages listed in `requirements.txt` (Streamlit, Skyfield, NumPy, pandas, Matplotlib, Pillow, geonamescache, tzdata) | installed separately | Each under its own open-source license. |

The app shows these credits on its About page and in the sidebar, as the CC BY 4.0 licences require.
