import time
from openai import OpenAI


def benchmark_performance():
    client = OpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")
    prompts = [
        "What is the capital of Italy?",
        "Calculate 10 plus 5",
        "Write a shrot poem about the ocean",
        "Who wrote the Romeo and Juliet?",
        "Translate this to spanish: 'Good morning, how are you?'",
        "Who actually discovered the heliocentric model?",
        "List five uncommon fruits from Asia.",
        "How many days are in 15 weeks?",
        "Create a simple script to solve foo-bar problem",
        "What is the boiling point of water?",
    ]

    start_time = time.time()

    for i, prompt in enumerate(prompts):
        client.chat.completions.create(
            model="",
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=200,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )

    end_time = time.time()
    total_time = end_time - start_time
    print(f"[RESULT] {total_time}s")


if __name__ == "__main__":
    benchmark_performance()
