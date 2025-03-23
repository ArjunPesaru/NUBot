# Stage 1: Build base environment
FROM python:3.10-slim AS base

# Use faster package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Pre-copy requirements separately for Docker cache efficiency
COPY runtime-requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r runtime-requirements.txt

# Stage 2: Clean runtime image
FROM python:3.10-slim AS runtime

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=base /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/include /usr/local/include
COPY --from=base /usr/local/share /usr/local/share

# Copy app source
COPY . .

# Make sure app uses port 8080 (Cloud Run default)
ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
