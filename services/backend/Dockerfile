# Stage 1: Build base environment
FROM python:3.10-slim AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY runtime-requirements.txt .

RUN pip install --no-cache-dir -r runtime-requirements.txt

# Stage 2: Runtime image
FROM python:3.10-slim AS runtime

WORKDIR /app

COPY --from=base /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/include /usr/local/include
COPY --from=base /usr/local/share /usr/local/share

# Copy all app source
COPY . .
RUN chmod +x runscripts.sh

ENV PORT=5002
EXPOSE 5002

# 👇 This will be triggered unless overridden in docker-compose
CMD ["./runscripts.sh"]
