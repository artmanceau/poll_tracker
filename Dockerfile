FROM ubuntu:22.04

# Install Python and required tools
RUN apt-get update && \
    apt-get install -y python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy your pipeline code
COPY src ./src

# Make the Python package discoverable
ENV PYTHONPATH=/app/src

# Run the Wikipedia polling pipeline
CMD ["uv", "run", "python", "-m", "poll_tracker.pipeline.poll_wikipedia"]
