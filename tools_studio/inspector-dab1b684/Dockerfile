FROM node:18-alpine3.21  

# Install MCP Inspector
RUN npm install -g @modelcontextprotocol/inspector

# Run the inspector
CMD ["npx","-y","supergateway","--stdio","npx -y @modelcontextprotocol/inspector"]
