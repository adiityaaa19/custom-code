FROM node:18-alpine

COPY --from=mcp/tavily:latest /app /app
 
# Set up the working directory
WORKDIR /app
 
# The command that will run when the container starts
CMD ["sh", "-c", "npx -y supergateway --stdio \"node ./build/index.js\" --outputTransport streamableHttp --port 8080"]




