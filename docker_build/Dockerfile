# Use a stable Python version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS packages needed by SpeechRecognition / pyaudio (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Set environment variables (optional, but nice)
ENV PYTHONUNBUFFERED=1

# Default command – run Malik
CMD ["python", "app.py"]
