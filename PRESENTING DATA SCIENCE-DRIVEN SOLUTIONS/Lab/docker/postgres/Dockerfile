# Basic PostgreSQL Dockerfile
FROM postgres:15

# Set environment variables
ENV POSTGRES_DB=labdb
ENV POSTGRES_USER=labuser
ENV POSTGRES_PASSWORD=MyStrongPass123!
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --lc-collate=C --lc-ctype=C"

# Create custom initialization directory
RUN mkdir -p /docker-entrypoint-initdb.d

# Copy initialization scripts (optional)
# COPY init.sql /docker-entrypoint-initdb.d/
# COPY setup.sh /docker-entrypoint-initdb.d/

# Install additional extensions (optional)
RUN apt-get update && apt-get install -y \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# Create custom data directory with proper permissions
RUN mkdir -p /var/lib/postgresql/data
RUN chown -R postgres:postgres /var/lib/postgresql/data

# Expose PostgreSQL port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB

# PostgreSQL will start automatically via the base image

# Build command: docker build -t lab-postgres .
# Run command: docker run -d --name postgres-lab -p 5432:5432 -v postgres_data:/var/lib/postgresql/data lab-postgres