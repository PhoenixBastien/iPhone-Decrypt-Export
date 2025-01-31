FROM public.ecr.aws/lambda/python:latest-amd64

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copy backup folder using device hash
ARG DEVICE_HASH
COPY test/${DEVICE_HASH} ${LAMBDA_TASK_ROOT}/backup

# Set the CMD to handler function
CMD [ "lambda_function.handler" ]