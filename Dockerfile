FROM node:22-slim

WORKDIR /app

# Install from npm
RUN npm install -g asrai-mcp@0.5.2

EXPOSE 8402

CMD ["asrai-mcp-server"]
