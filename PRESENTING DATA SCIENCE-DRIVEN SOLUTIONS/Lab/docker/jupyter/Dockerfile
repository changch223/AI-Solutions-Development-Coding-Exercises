# Jupyter Notebook Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    jupyter \
    jupyterlab \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    plotly \
    requests \
    sqlalchemy \
    psycopg2-binary \
    pymssql

# Create a non-root user
RUN useradd -m -s /bin/bash jupyter
USER jupyter
WORKDIR /home/jupyter

# Create notebooks directory
RUN mkdir -p /home/jupyter/notebooks

# Expose Jupyter port
EXPOSE 8888

# Set Jupyter configuration
ENV JUPYTER_ENABLE_LAB=yes

# Start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]

# Build command: docker build -t lab-jupyter .
# Run command: docker run -d --name jupyter-lab -p 8888:8888 -v $(pwd)/notebooks:/home/jupyter/notebooks lab-jupyter