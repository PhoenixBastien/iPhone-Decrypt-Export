FROM public.ecr.aws/lambda/python:latest-arm64

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copy backup folder
COPY test/00008030-001C050E0EBB802E ${LAMBDA_TASK_ROOT}/backup

# Set the CMD to handler function
CMD [ "lambda_function.handler" ]