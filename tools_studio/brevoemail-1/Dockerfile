# # FROM supercorp/supergateway:uvx

# # # Install git and curl
# # RUN apk update && \
# #     apk add --no-cache git curl

# # EXPOSE 8080

# # # Note: You can pass ELEVENLABS_API_KEY at runtime if needed
# # CMD ["supergateway","--stdio", "uvx --from git+https://github.com/jkawamoto/mcp-youtube-transcript mcp-youtube-transcript","--outputTransport", "streamableHttp","--port", "8080"]







# # # Use a base image with Node.js (since Supergateway is a Node.js tool)
# # FROM node:22-alpine
 
# # # Install Supergateway
# # RUN npm install -g supergateway
 
# # # Copy the Tavily MCP tool (assuming we're building from the original)
# # # Alternatively, we could just use the existing image as a base
# # COPY --from=mcp/kubernetes /app /app
 
# # # Set up the working directory
# # WORKDIR /app
 
# # # The command that will run when the container starts
# # CMD ["sh", "-c", "supergateway --stdio \"node dist/index.js\" --outputTransport streamableHttp --port 8080"]




# FROM node:22-alpine


# CMD ["npx","-y","supergateway","--stdio","@alanse/mcp-neo4j-server","--outputTransport","streamableHttp","--port","8080"]




# # FROM node:22-alpine

# # # Install kubectl (required for mcp-server-kubernetes)
# # RUN apk add --no-cache curl && \
# #     curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
# #     install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
# #     rm -f kubectl

# # # Optionally, ensure supergateway and mcp-server-kubernetes are installed globally
# # RUN npm install -g supergateway mcp-server-kubernetes

# # # Correct CMD: Use a shell to properly chain the commands
# # CMD ["sh", "-c", "npx -y supergateway --stdio 'mcp-server-kubernetes' --outputTransport streamableHttp --port 8080"]






# # FROM node:18-alpine

# # COPY --from=mcp/tavily:latest /app /app
 
# # # Set up the working directory
# # WORKDIR /app
 
# # # The command that will run when the container starts
# # CMD ["sh", "-c", "npx -y supergateway --stdio \"node ./build/index.js\" --outputTransport streamableHttp --port 8080"]




# Use the prebuilt SMTP email server image from Docker Hub
FROM adityaaa19/smtpbrevo:latest

# Set the working directory inside the container
WORKDIR /app

# Expose the port your server is running on
# Replace 5000 with the port your server listens on
EXPOSE 8000

# Command to start the server
# Replace with the actual start command if different
CMD ["python", "gmail.py"]

