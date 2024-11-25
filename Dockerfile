FROM python:3.9

WORKDIR /app
ENV COQUI_TOS_AGREED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
RUN spacy download en_core_web_sm && spacy link es_core_news_sm

EXPOSE 8080

CMD ["sh", "boot.sh"]