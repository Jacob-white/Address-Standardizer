# Production Dockerfile for Address Standardizer Microservice Daemon
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain for native acceleration compilation
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY pyproject.toml requirements.txt ./
COPY Cargo.toml Cargo.lock ./
COPY src/ ./src/
COPY address_standardizer/ ./address_standardizer/

RUN pip install --no-cache-dir maturin wheel setuptools
RUN maturin build --release --out dist

FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl fastapi uvicorn pydantic pyarrow duckdb polars requests \
    && rm -rf /tmp/*.whl

COPY address_standardizer /app/address_standardizer

ENV PYTHONUNBUFFERED=1
ENV ADDRESS_STANDARDIZER_CACHE_MAX_SIZE=50000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["uvicorn", "address_standardizer.server:app", "--host", "0.0.0.0", "--port", "8000"]
