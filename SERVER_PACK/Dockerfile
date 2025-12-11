# Lightweight Node.js base image
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Install dependencies first (better layer caching)
COPY package*.json ./
RUN npm install --production

# Copy app sources
COPY . .

# Make sure timezone and locale are reasonable (optional)
# RUN apk add --no-cache tzdata && cp /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && echo "Europe/Warsaw" > /etc/timezone

# Default command to start both bots
CMD ["node", "START_ALL_BOTS.js"]
