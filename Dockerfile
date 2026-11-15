# The Sidereal Oracle on its own web address (siderealoracle.com), for the Google Play app.
# Render.com builds this file by itself. Streamlit Community Cloud ignores it, so the free version keeps working.
#
# Inside the server two programs run side by side:
#   Streamlit (the app itself)         -> https://siderealoracle.com/app/
#   Caddy (a small web server in front) -> the welcome page, privacy policy, icons, and the
#                                          /.well-known/assetlinks.json file that Google Play needs.

FROM python:3.12-slim

# Caddy, the small web server, copied from its official image.
COPY --from=caddy:2 /usr/bin/caddy /usr/bin/caddy

WORKDIR /srv/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The app's dark "Lagoon" colours. GitHub's drag-and-drop upload skips the .streamlit folder, so a copy of its
# config.toml is kept as streamlit_config.toml and put in place here.
RUN mkdir -p .streamlit && cp streamlit_config.toml .streamlit/config.toml

# Download the NASA JPL planet tables (de440s.bsp, 32 MB) once, while building, so the app starts quickly.
RUN python -c "import sidereal_engine"

# The address printed in friend-card QR codes. Change it here if the web address ever changes.
ENV LILLY_APP_URL=https://siderealoracle.com/app/
ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.baseUrlPath app --server.headless true --browser.gatherUsageStats false --client.toolbarMode viewer & exec caddy run --config /srv/app/Caddyfile --adapter caddyfile"]
