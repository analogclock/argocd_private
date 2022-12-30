From python:3.8

RUN mkdir /app
WORKDIR /app
ADD . /app
RUN pip install -r requirement.txt

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["/app/main.py"]
