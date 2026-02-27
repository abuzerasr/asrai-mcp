FROM python:3.11-slim-bookworm

WORKDIR /app

# Install from PyPI
RUN pip install --no-cache-dir "asrai-mcp[sse]==0.4.4"

EXPOSE 8402

CMD ["asrai-mcp-server"]
