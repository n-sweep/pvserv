### build layer with dependencies ##############################################

FROM python:3.13-bookworm AS builder

RUN pip install uv

WORKDIR /app

# copy and install dependencies first for better caching
COPY pyproject.toml ./
RUN uv venv .venv && uv pip install -e . --python /app/.venv/bin/python

# copy the rest of the application
COPY . .


### build minimal image using dependencies #####################################

FROM python:3.13-slim-bookworm

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY --from=builder /app .

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

CMD [ "python", "main.py" ]

# docker stop pvserv && docker rm pvserv && docker rmi pvserv
# docker build -t pvserv .
# docker run -dit --name pvserv \
# -e TS_IP="$(tailscale ip --4)" \
# -v "${PWD}"/.data:/app/.data \
# -p 8080:8080 \
# pvserv

# tailscale serve --bg --http 80 --set-path /pvserv http://localhost:8080
