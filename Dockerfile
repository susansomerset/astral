FROM node:22-bookworm-slim AS nodebin

FROM python:3.12-slim-bookworm

COPY --from=nodebin /usr/local/bin/node /usr/local/bin/node
COPY --from=nodebin /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

WORKDIR /app
COPY . .

# Vite inlines these during `npm run build` inside scripts/build_railway.sh.
# Railway only passes a service variable into a Dockerfile build when the
# stage declares a matching ARG. ARG is not persisted as image ENV.
# VITE_STYTCH_PUBLIC_TOKEN is absent from the AST-2249 warning list
# (Docker's check allowlists names containing "public").
ARG VITE_STYTCH_PUBLIC_TOKEN
ARG VITE_STYTCH_REDIRECT_URL

RUN bash scripts/build_railway.sh
