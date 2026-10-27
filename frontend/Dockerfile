# Stage 1: Build SvelteKit static production assets
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies with lockfile caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy application source code
COPY . .

# Run type checks and compile production bundle
RUN npm run check
RUN npm run build

# Stage 2: Serve production build via unprivileged (non-root) Nginx
FROM nginxinc/nginx-unprivileged:alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 8041

# Health check against frontend web server
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8041/ || exit 1


CMD ["nginx", "-g", "daemon off;"]
