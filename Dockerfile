FROM python:3.9

# Set working directory
WORKDIR /app

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
RUN git clone https://github.com/obahamonde/TTS-la.git && cd TTS-la && pip install -e . && cd ..


# RUN cuda.sh
# Expose port
EXPOSE 8080

# Command to run the application
CMD ["bash","boot.sh"]
