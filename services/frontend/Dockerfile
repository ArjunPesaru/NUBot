
# Use Python 3.10 slim as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Install Streamlit
RUN pip install streamlit

# Now copy the rest of the application files
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8501

# Entry point to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
