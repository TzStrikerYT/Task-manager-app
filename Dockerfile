FROM python:3.9-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy Poetry configuration files
COPY pyproject.toml /app/

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install

# Copy application code
COPY . /app/

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "wsgi.py"] 