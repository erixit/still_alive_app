FROM python:3.10-slim-bullseye

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies first (cached layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 8501

# Default command to run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
