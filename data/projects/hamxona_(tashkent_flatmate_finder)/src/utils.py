import hashlib
import hmac
import json
from urllib.parse import unquote
from fastapi import HTTPException, Header
from src.config import settings

def validate_telegram_data(init_data: str):
    """
    Validates the data received from Telegram Mini App.
    See: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data:
        raise HTTPException(status_code=401, detail="No auth data provided")
        
    try:
        parsed_data = dict(x.split('=') for x in unquote(init_data).split('&'))
        hash_check = parsed_data.pop('hash')
        
        # Sort keys alphabetically
        data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(parsed_data.items())])
        
        secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash != hash_check:
            raise HTTPException(status_code=403, detail="Invalid hash")
            
        user_data = json.loads(parsed_data['user'])
        return user_data
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Validation failed: {str(e)}")