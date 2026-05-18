FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
# Ensure public/ exists so the COPY in the runner stage never fails
RUN mkdir -p /app/public
RUN npm run build

# Production runner using standalone output
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Copy standalone server and required static files
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

# Next.js standalone server reads PORT env var automatically.
# Railway overrides PORT at runtime if it assigns a different port.
CMD ["node", "server.js"]
