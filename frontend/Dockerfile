FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
# Ensure public/ exists so the COPY in the runner stage never fails
RUN mkdir -p /app/public

# Bake NEXT_PUBLIC_API_URL into the Next.js bundle at build time.
# Railway passes service variables as Docker build args automatically
# when the variable name matches the ARG name.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# Production runner using standalone output
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0

# Copy standalone server and required static files
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 8080

# Next.js standalone server reads PORT env var automatically.
# Railway injects PORT=8080 at runtime; domain must target the same port.
CMD ["node", "server.js"]
