FROM python:3.9

# Set working directory
WORKDIR /app
ENV COQUI_TOS_AGREED=1
# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Install PyTorch CPU version
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy and install requirements
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN spacy download en_core_web_sm && spacy link es_core_news_sm

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["sh", "boot.sh"]