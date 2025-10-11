import os


def test_exporting_secrets():
    # export_secrets()

    print(os.environ.get("EXAMPLE_API_KEY"))

    assert "EXAMPLE_API_KEY" in os.environ
    assert os.environ["EXAMPLE_API_KEY"]


def test_exporting_envs():
    # export_envs("test")

    assert "ENVIRONMENT" in os.environ
    assert "APP_NAME" in os.environ
    assert "DATABASE_URL" in os.environ
