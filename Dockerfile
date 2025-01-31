FROM public.ecr.aws/lambda/python:latest-arm64

# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py .

# Copy backup folder
COPY test/00008030-001C050E0EBB802E backup

# Copy imessage-exporter binary
# COPY imessage-exporter .

# Set the CMD to handler function
CMD [ "lambda_function.handler" ]
