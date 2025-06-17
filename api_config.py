import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Konfigurasi OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# Set API key
openai.api_key = OPENAI_API_KEY

# Inisialisasi OpenAI client
client = openai

# Konstanta untuk batasan karakter
MAX_CHARS_OPENAI = 12000  # batas aman karakter untuk input ke OpenAI 