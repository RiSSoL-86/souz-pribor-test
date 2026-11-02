from django_project.settings import env

# --- LLM ---
LLM_PROVIDER = env("LLM_PROVIDER", default="open_ai")
PRODUCT_CARD_MAX_ATTEMPTS = 3
