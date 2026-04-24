FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json .
RUN npm install --only=production

FROM node:20-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S appuser -G app

COPY --from=builder /app/node_modules ./node_modules
COPY app.js .
COPY views ./views

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

EXPOSE 3000

CMD ["node", "app.js"]