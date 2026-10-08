# Production Dockerfile for Address Standardizer Microservice Daemon
# Pin base images by digest in your own registry mirror for fully reproducible builds.
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install a pinned Rust toolchain for native acceleration compilation
ARG RUST_TOOLCHAIN=1.82.0
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain ${RUST_TOOLCHAIN}
ENV PATH="/root/.cargo/bin:${PATH}"

# pyproject.toml declares README.md and the MIT LICENSE as package metadata, so both must be present
COPY pyproject.toml requirements.txt README.md LICENSE ./
COPY Cargo.toml Cargo.lock ./
COPY src/ ./src/
COPY address_standardizer/ ./address_standardizer/

RUN pip install --no-cache-dir maturin wheel setuptools

# Two wheels: the compiled extension (maturin ships only the Rust module) and the pure-Python package.
RUN maturin build --release --locked --out dist/native \
    && pip wheel --no-cache-dir --no-deps --wheel-dir dist/py .

FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --uid 10001 appuser

# Install the pure-Python wheel (with the server and arrow extras declared in pyproject.toml), then drop the compiled
# extension next to it. The two wheels share a project name, so pip would treat the second as already installed;
# the native wheel only carries the _address_standardizer_rs module, so it is unpacked into site-packages directly.
# There is deliberately no source copy in the working directory that could shadow the installed package.
COPY --from=builder /build/dist/native/*.whl /tmp/native/
COPY --from=builder /build/dist/py/*.whl /tmp/py/
RUN pip install --no-cache-dir "$(ls /tmp/py/address_standardizer-*.whl | head -n 1)[server,arrow]" \
    && python -m zipfile -e "$(ls /tmp/native/*.whl | head -n 1)" /tmp/native_x \
    && cp -r /tmp/native_x/_address_standardizer_rs "$(python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/" \
    && rm -rf /tmp/native /tmp/native_x /tmp/py

ENV PYTHONUNBUFFERED=1
ENV ADDRESS_STANDARDIZER_CACHE_MAX_SIZE=50000

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Bind all interfaces inside the container; publish the port deliberately (see docker-compose.service.yml).
ENTRYPOINT ["uvicorn", "address_standardizer.server:app", "--host", "0.0.0.0", "--port", "8000"]
