FROM nginx:alpine

# Copy static files
COPY src/frontend/ /usr/share/nginx/html/

# Copy the cartel image from the data folder (since it's gitignored in frontend)
COPY data/cartel_feria_2025.jpeg /usr/share/nginx/html/

# Replace the placeholder with environment variable at runtime
# AND fix Nginx to listen on the port Cloud Run expects ($PORT)
CMD ["/bin/sh", "-c", "sed -i \"s|listen.*80;|listen ${PORT:-80};|g\" /etc/nginx/conf.d/default.conf && sed -i \"s|__BACKEND_URL__|$BACKEND_URL|g\" /usr/share/nginx/html/main.js && exec nginx -g 'daemon off;'"]
