FROM python:3.11.7
 
# Creating Application Source Code Directory
RUN mkdir -p /projetDE/src
# Setting Home Directory for containers
WORKDIR /projetDE/src
# Installing python dependencies
COPY requirements.txt /projetDE/src/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# Copying src code to Container
COPY . /projetDE/src
# Running Python Application
CMD [“python”, “main.py”]