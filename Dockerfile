FROM python:3.11.0

COPY requirements.txt .

RUN python3.10 -m pip install --upgrade pip && python3.10 -m pip install -r requirements.txt

COPY . .

CMD ["python3.10", "main.py"]