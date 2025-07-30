# 🧱 Bazowy obraz
FROM python:3.11-slim

# 🌍 Ustaw zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CHROME_DRIVER_VERSION=138.0.7204.183

# 📁 Ustaw katalog roboczy
WORKDIR /app

# 📦 Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libxss1 \
    libxshmfence1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 🌐 Zainstaluj Google Chrome (oficjalny build)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# 🧰 Zainstaluj ChromeDriver w wersji 138.0.7204.183 (dopasowana do Chrome)
RUN wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# 📄 Skopiuj pliki projektu
COPY . /app

# 🔧 Zainstaluj zależności z requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ▶️ Uruchom bota
CMD ["python", "main.py"]
