FROM python:3.11-slim

WORKDIR /app

# I've forgotten to save to compiled model in the remote environment, so I had to compile it inside the container.
# Apparently, g++ is required for that.
RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY models/model_original.pth models/
COPY models/tokenizer models/tokenizer/

COPY infer.py .

CMD ["python", "infer.py"]