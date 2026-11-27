import os
import base64
import json
import time
import requests
import zipfile
import io
import certifi
from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import httpx
from dotenv import load_dotenv, set_key
import uuid
import authentication_provider

class DellAI:
    """Utility class for interacting with Dell AIA (AI Gateway)."""

    aia_base_url = "https://aia.gateway.dell.com/genai/dev/v1"
    headers = {}
    token = None
    _certs_initialized = False  # ← only download certs once

    @classmethod
    def _is_token_valid(cls):
        """Check if the cached token is still valid by decoding its JWT expiry."""
        if cls.token is None:
            return False
        try:
            payload_b64 = cls.token.split('.')[1]
            # JWT base64 may lack padding
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.b64decode(payload_b64))
            exp = payload.get('exp', 0)
            return time.time() < (exp - 60)  # 60s buffer before expiry
        except Exception:
            return False  # treat any decode error as invalid

    def __new__(cls, env_file='.env'):
        """Create and return an OpenAI client directly.
        
        Args:
            env_file: Path to .env file (default: '.env')
        """
        # Load environment variables
        load_dotenv(env_file, override=True)
        
        # Download Dell certificates only once per session
        if not cls._certs_initialized:
            dell_cert_url = "https://pki.dell.com//Dell%20Technologies%20PKI%202018%20B64_PEM.zip"
            print("Downloading Dell certificates...")
            response = requests.get(dell_cert_url)
            response.raise_for_status()
            cert_path = certifi.where()
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                for name in z.namelist():
                    if name.endswith('.pem'):
                        cert_content = z.read(name).decode('utf-8')
                        with open(cert_path, "a") as bundle:
                            bundle.write("\n" + cert_content + "\n")
            print("Certificates added successfully.")
            cls._certs_initialized = True
 
        # Load token from .env into memory if not already cached
        if cls.token is None:
            cls.token = os.getenv("SSO_TOKEN")

        # Only request a new token if the cached one is invalid/expired
        if not cls._is_token_valid():
            auth_provider = authentication_provider.AuthenticationProvider()
            cls.token = auth_provider.generate_auth_token()

            # Persist token to .env for next run
            set_key(env_file, "SSO_TOKEN", cls.token)            

            cls.headers = {
                "x-correlation-id": str(uuid.uuid4()),
                'accept': '*/*',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {cls.token}'
            }
            print("Token refreshed.")
        else:
            print("Using cached token.")
            cls.headers = {
                "x-correlation-id": str(uuid.uuid4()),
                'accept': '*/*',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {cls.token}'
            }

    @classmethod
    def ChatOpenAI(cls, temperature=0, model=None):
        """
        Create and return a ChatOpenAI client for Dell AIA.
        
        Args:
            temperature: Sampling temperature (default: 0)
            model: Model name to use (default: from AI_MODEL env var or 'llama-3-3-70b-instruct')
            Available models:
            - florence-2-large-ft
            - llama-3-2-3b-instruct
            - llama-3-3-70b-instruct
            - pixtral-12b-2409
            - detr
            - gemma-3-27b-it
            - mistral-small-3-1-24b-instruct-2503
            - gpt-oss-20b
            - gpt-oss-120b
            - nomic-embed-text-v1-5
            - nomic-embed-text-v1
            - granite-embedding-278m-multilingual
            - ms-marco-minilm-l12-v2
            - embeddinggemma-300m
            - granite-embedding-reranker-english-r2
            - multilingual-e5-large-instruct
            - mmarco-mminilmv2-l12-h384-v1
            - llama-guard-3-8b
            - whisper-large-v3-turbo
            - gemma-4-e4b-it
            - finetuned-gemma-4-e4b-it
            - laya
            - shieldstral-1-0-3b
            - ctxl-rerank-ml-6b
            - nomic-embed-vision-v1-5
            - search-model-multi
        """
        
        cls()

        # Get model name from parameter or environment
        if model is None:
            model = "llama-3-3-70b-instruct"

        # Return a langchain-compatible ChatOpenAI instance
        client = ChatOpenAI(
            base_url=cls.aia_base_url,
            api_key=cls.token,
            model=model,
            temperature=temperature,
            default_headers=cls.headers,
            http_client=httpx.Client(verify=certifi.where())
        )
        return client

    @classmethod
    def OpenAIEmbeddings(cls, model=None):
        """
        Create and return an OpenAIEmbeddings client for Dell AIA.
        
        Args:
            model: Model name to use (default: from AI_MODEL env var or 'nomic-embed-text-v1-5')
            Available embedding models:
            - nomic-embed-text-v1-5
            - nomic-embed-text-v1
            - granite-embedding-278m-multilingual
            - embeddinggemma-300m
            - multilingual-e5-large-instruct
        """

        cls()
        
        # Get model name from parameter or environment
        if model is None:
            model = "nomic-embed-text-v1-5"

        # Return a langchain-compatible ChatOpenAI instance
        client = OpenAIEmbeddings(
            base_url=cls.aia_base_url,
            api_key=cls.token,
            model=model,
            default_headers=cls.headers,
            http_client=httpx.Client(verify=certifi.where())
        )
        return client
