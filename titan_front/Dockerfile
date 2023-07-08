FROM python:3.9.14-slim

WORKDIR /app

COPY . /app

RUN pip install streamlit

EXPOSE 8501

CMD ["streamlit", "run", "titanic_streamlit_app.py"]
