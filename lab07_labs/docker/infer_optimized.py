import onnxruntime as ort
from transformers import AutoTokenizer
import time

tokenizer = AutoTokenizer.from_pretrained("models/tokenizer")
sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
ort_session = ort.InferenceSession(
    "models/model_optimized.onnx",
    sess_options=sess_options,
    providers=["CPUExecutionProvider"],
)


def predict(text: str):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="np")

    inputs_onnx = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
    }

    ort_session.run(None, inputs_onnx)


if __name__ == "__main__":
    sample_text = "This is a test sentence for inference."

    for _ in range(5):
        predict(sample_text)

    num_requests = 100
    start = time.time()
    for _ in range(num_requests):
        predict(sample_text)
    end = time.time()

    avg_time = (end - start) / num_requests
    print(f"Average inference time: {avg_time}s")
