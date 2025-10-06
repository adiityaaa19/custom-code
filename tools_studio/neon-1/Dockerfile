FROM node:18-alpine

# Copy prebuilt app from the original MCP image
COPY --from=mcp/neon /app /app

WORKDIR /app

# Run Supergateway in streamableHttp mode, wrapping the MCP entrypoint
CMD ["sh", "-c", "npx -y supergateway --stdio \"node ./dist/index.js start $NEON_API_KEY\" --outputTransport streamableHttp --port 8000"]





