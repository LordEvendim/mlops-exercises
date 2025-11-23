import torch
from transformers import AutoModel, AutoTokenizer
import time

tokenizer = AutoTokenizer.from_pretrained("models/tokenizer")

model = AutoModel.from_pretrained("sentence-transformers/multi-qa-mpnet-base-cos-v1")
model.to("cpu")
model.eval()

model.load_state_dict(torch.load("models/model_original.pth", weights_only=True))
compiled_model = torch.compile(model)


def predict(text: str):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    inputs = {k: v.to("cpu") for k, v in inputs.items()}

    with torch.inference_mode():
        compiled_model(**inputs)


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
