# Use an official Amazon Linux base image with Python 3.8 pre-installed
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory
WORKDIR /var/task

# Copy the requirements.txt first, to leverage Docker cache
COPY requirements.txt ./

# Install the necessary packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the CMD to your handler function (module.function)
CMD ["main.handler"]
