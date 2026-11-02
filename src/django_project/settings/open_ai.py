from django_project.settings import env

# --- OpenAI ---
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4.1-mini")
OPENAI_TIMEOUT = env.float("OPENAI_TIMEOUT", default=60.0)
OPENAI_MAX_RETRIES = env.int("OPENAI_MAX_RETRIES", default=2)
OPENAI_PROXY = env("OPENAI_PROXY", default="")
OPENAI_TEMPERATURE = 0.3
