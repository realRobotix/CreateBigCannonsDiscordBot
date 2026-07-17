FROM python:3.12-alpine AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apk add --no-cache \
      build-base \
      libffi-dev \
      openssl-dev \
      python3-dev \
      cargo \
      git

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY README.md ./README.md
COPY LICENSE ./LICENSE

RUN uv sync --frozen --no-dev

# remove build-time packages (keeps runtime deps)
RUN apk del build-base python3-dev cargo git

# Final stage uses the same image but copies the /app folder
FROM python:3.12-alpine AS runtime

WORKDIR /app

# copy everything already prepared in build stage
COPY --from=build /app /app

# create app user
RUN adduser -D -h /home/appuser -s /sbin/nologin appuser
USER appuser

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["cbcbot"]