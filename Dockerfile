FROM python:3.11-slim

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libgbm-dev \
    libxshmfence1 \
    libgtk-3-0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Instalacja Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/google.gpg
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Instalacja odpowiedniego ChromeDrivera
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') \
 && DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
 && wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" \
 && unzip chromedriver_linux64.zip \
 && mv chromedriver /usr/bin/chromedriver \
 && chmod +x /usr/bin/chromedriver \
 && rm chromedriver_linux64.zip

# Ustaw katalog roboczy
WORKDIR /app

# Kopiuj wymagania i zainstaluj
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj aplikację
COPY . .

# Uruchamianie bota z xvfb (wirtualny ekran)
CMD ["xvfb-run", "python", "main.py"]
