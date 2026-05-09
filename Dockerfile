FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 1000 --create-home --shell /bin/bash appuser

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen

COPY src/ ./src/
COPY assets/ ./assets/

RUN mkdir -p data/downloads data/processed data/output \
    && chown -R appuser:appuser /app

USER appuser

CMD ["uv", "run", "python", "src/main.py"]
