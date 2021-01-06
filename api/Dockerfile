FROM python:3

WORKDIR /api

COPY ./source ./

RUN pip install flask
RUN pip install pymongo

ENV FLASK_APP="/api/flask_app.py"


# CMD ["/bin/bash"]
CMD ["flask", "run", "--host=0.0.0.0"]