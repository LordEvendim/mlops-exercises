from transformers import AutoModel, AutoTokenizer

model_name = "sentence-transformers/multi-qa-mpnet-base-cos-v1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

tokenizer.save_pretrained("models/tokenizer")
