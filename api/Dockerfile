FROM python:3

WORKDIR /api

RUN pip install flask
RUN pip install pymongo

ENV FLASK_APP="/api/flask_app.py"
ENV FLASK_ENV="development"

COPY ./source ./

# CMD ["/bin/bash"]
CMD ["flask", "run", "--host=0.0.0.0"]