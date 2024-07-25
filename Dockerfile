# Use the base image with Python 3.11
FROM python:3.11-slim

# Create a system group and user for running the application
RUN groupadd -r myuser && useradd -r -g myuser myuser

# Set the working directory inside the Docker container
WORKDIR /portfolio-chat-demo

# Copy all files from the current build context into the container's working directory
COPY . .

# Install Python packages listed in requirements.txt using pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 for external access
EXPOSE 8501

# Switch to the non-root user context
USER myuser

# Define the entry point command to run when the container starts
ENTRYPOINT ["streamlit", "run"]

# Specify the default Streamlit application script to run
CMD ["💵TTW_AskAR.py"]
