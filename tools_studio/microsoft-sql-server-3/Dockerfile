FROM node:alpine3.21

ENTRYPOINT ["npx", "-y", "supergateway", "--stdio", "npx -y @bluspace/mssql-mcp-server --user $DB_USER --password $DB_PASSWORD --server $DB_SERVER  --port $PORT --database $DB_NAME --permissions $PERMISSION"]