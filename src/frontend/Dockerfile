FROM nginx:alpine

# Copy static files
COPY src/frontend/ /usr/share/nginx/html/

# Replace the placeholder with environment variable at runtime
CMD ["/bin/sh", "-c", "sed -i \"s|__BACKEND_URL__|$BACKEND_URL|g\" /usr/share/nginx/html/main.js && exec nginx -g 'daemon off;'"]
