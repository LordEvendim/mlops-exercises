import requests

BASE_URL = "http://sentiment-app-alb-698939200.us-east-1.elb.amazonaws.com"


def test_welcome():
    response = requests.get(f"{BASE_URL}/")

    print(f"Response: {response.json()}")


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Response: {response.json()}")


def test_predict(text):
    payload = {"text": text}
    response = requests.post(f"{BASE_URL}/predict", json=payload)

    print("-----")
    print(f"Text: {text}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    test_welcome()
    test_health()
    test_predict("This is a very positive message")
    test_predict("This is a very negative message")
    test_predict("This message is okay, I guess")
