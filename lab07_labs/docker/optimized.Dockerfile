FROM python:3.11-slim

WORKDIR /app

COPY requirements_optimized.txt .
RUN pip install -r requirements_optimized.txt

COPY models/model_optimized.onnx models/
COPY models/tokenizer models/tokenizer/

COPY infer_optimized.py .

CMD ["python", "infer_optimized.py"]