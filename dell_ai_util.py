import os
import requests
import zipfile
import io
import certifi
from openai import OpenAI
from langchain_openai import ChatOpenAI
import httpx
from dotenv import load_dotenv
import authentication_provider

class ChatDellAI:
    """Utility class for interacting with Dell AIA (AI Gateway)."""

    def __new__(cls, env_file='.env', temperature=0, model=None):
        """Create and return an OpenAI client directly.
        
        Args:
            env_file: Path to .env file (default: '.env')
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
        # Load environment variables
        load_dotenv(env_file, override=True)
        
        # Setup certificates
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
        
        # Create and return the OpenAI client
        import uuid
        aia_base_url = "https://aia.gateway.dell.com/genai/dev/v1"
        
        # Get fresh token from authentication provider
        auth_provider = authentication_provider.AuthenticationProvider()
        token = auth_provider.generate_auth_token()
        
        headers = {
            "x-correlation-id": str(uuid.uuid4()),
            'accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        # Get model name from parameter or environment
        if model is None:
            model = os.getenv("AI_MODEL", "llama-3-3-70b-instruct")
        
        # Return a langchain-compatible ChatOpenAI instance
        client = ChatOpenAI(
            base_url=aia_base_url,
            api_key=token,
            model=model,
            temperature=temperature,
            default_headers=headers,
            http_client=httpx.Client(verify=certifi.where())
        )
        
        return client
