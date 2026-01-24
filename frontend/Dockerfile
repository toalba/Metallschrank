FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source files
COPY . .

# Build the application for production
RUN npm run build

# Use a simple final stage that just has the build output
FROM alpine:latest

COPY --from=builder /app/build /app/build

# This container is only used to populate the volume
CMD ["echo", "Build completed"]
