# FROM node:alpine3.21

# CMD ["npx","-y","supergateway","--stdio","npx -y @antv/mcp-server-chart"]

FROM node:18-alpine

# Install the package globally
RUN npm install -g @antv/mcp-server-chart


# Run the server with SSE transport on port 8000
CMD ["mcp-server-chart", "--transport", "sse", "--port", "8000"]
