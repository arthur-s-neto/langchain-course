import os
from aia_auth import auth
from dotenv import load_dotenv

load_dotenv()


class AuthenticationProvider:
    """Handles authentication for Dell AIA gateway using SSO or OAuth."""
    
    def __init__(self):
        self.use_sso = os.getenv("USE_SSO", "false").lower() == "true"
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

    def generate_auth_token(self):
        """Generate authentication token based on configured method."""
        if self.use_sso:
            return self._get_sso_token()
        return self._get_oauth_token()

    def _get_sso_token(self):
        """Generate token using SSO flow."""
        print("Getting SSO token...")
        access_token = auth.sso()
        return access_token.token

    def _get_oauth_token(self):
        """Generate token using OAuth client credentials flow."""
        self._validate_credentials()
        return auth.client_credentials(self.client_id, self.client_secret).token

    def _validate_credentials(self):
        """Validate that OAuth credentials are properly set."""
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "CLIENT_ID and CLIENT_SECRET must be set when USE_SSO=false"
            )
