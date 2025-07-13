FROM public.ecr.aws/lambda/python:3.9

# Copy function code and install dependencies
COPY lambda_function.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

# Set the handler
CMD ["lambda_function.lambda_handler"]
