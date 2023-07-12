FROM python:3.10.11-slim
ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000 \
    CONFIG_DIR="/config" \
    API_TOKEN="moviepilot" \
    HOST="::" \
    SUPERUSER="admin" \
    SUPERUSER_PASSWORD="password" \
    AUTH_SITE="hhclub" \
    HHCLUB_USERNAME="" \
    HHCLUB_PASSKEY="" \
    LIBRARY_PATH="" \
    DOWNLOAD_PATH="/Downloads" \
    PROXY_HOST="" \
    TMDB_API_DOMAIN="api.themoviedb.org" \
    LIBRARY_CATEGORY="true" \
    COOKIECLOUD_HOST="https://nastool.org/cookiecloud" \
    COOKIECLOUD_KEY="" \
    COOKIECLOUD_PASSWORD="" \
    COOKIECLOUD_INTERVAL="4320" \
    MESSAGER="wechat" \
    WECHAT_CORPID="" \
    WECHAT_APP_SECRET="" \
    WECHAT_APP_ID="" \
    WECHAT_TOKEN="" \
    WECHAT_ENCODING_AESKEY="" \
    DOWNLOADER="qbittorrent" \
    QB_HOST="http://" \
    QB_USER="" \
    QB_PASSWORD="" \
    MEDIASERVER="emby" \
    EMBY_HOST="http://127.0.0.1:8096" \
    EMBY_API_KEY="" \
    FILTER_RULE="!BLU & 4K & CN > !BLU & 1080P & CN > !BLU & 4K > !BLU & 1080P" \
    TRANSFER_TYPE="link" \
    DOUBAN_USER_IDS=""
    USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79"
WORKDIR "/app"
COPY . .
RUN apt-get update \
    && apt-get -y install musl-dev nginx \
    && mkdir -p /etc/nginx \
    && cp -f nginx.conf /etc/nginx/nginx.conf \
    && pip install -r requirements.txt \
    && python_ver=$(python3 -V | awk '{print $2}') \
    && echo "/app/" > /usr/local/lib/python${python_ver%.*}/site-packages/app.pth \
    && echo 'fs.inotify.max_user_watches=5242880' >> /etc/sysctl.conf \
    && echo 'fs.inotify.max_user_instances=5242880' >> /etc/sysctl.conf \
    && playwright install-deps chromium \
    && rm -rf /root/.cache/
EXPOSE 3000
VOLUME ["/config"]
ENTRYPOINT [ "bash", "-c", "/app/start.sh & nginx -g 'daemon off;'" ]
