FROM python:3.9.14-slim 
# python:3.9.14-alpine3.16


WORKDIR /app

COPY . /app

# RUN apk --update add gcc build-base freetype-dev libpng-dev openblas-dev

# RUN pip install --no-cache-dir pandas && pip install -r requirements.txt

# RUN apk add py3-scikit-learn && 

RUN pip install -r requirements.txt


EXPOSE 8000

CMD ["uvicorn", "titan_model:app", "--host", "0.0.0.0", "--port", "8000"]
