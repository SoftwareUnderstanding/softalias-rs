FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/esgg/softalias-rs.git .

RUN pip3 install -r requirements.txt

RUN python -m spacy download en_core_web_sm

EXPOSE 8051

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8051","https://github.com/esgg/softalias-rs.git"]
