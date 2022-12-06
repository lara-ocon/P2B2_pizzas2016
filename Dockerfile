FROM python:latest
COPY  . .
RUN pip install -r requirements.txt 
CMD [ "python", "./pizzas2.py" ]
