import uuid
import validators
import requests
from urllib.parse import urlparse
from models import URL


def validate_public_url(url: str) -> dict:
    """驗證 URL 是否為有效且可公開訪問的網址

    Args:
        url (str): 要驗證的 URL 字串

    Returns:
        dict: 包含驗證結果的字典:
            - success (bool): 驗證是否通過
            - reason (str): 失敗原因 (若成功則為 None)
    """
    if not validators.url(url):
        return {"success": False, "reason": "Invalid URL format"}

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return {"success": False, "reason": "URL not reachable"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "reason": f"Error reaching URL: {str(e)}"}

    if not validators.url(url, public=True):
        return {"success": False, "reason": "URL is not publicly accessible"}

    return {"success": True}


def generate_unique_short_id(session):
    """
    生成保證唯一的短 ID (8位隨機字串)

    Args:
        session (sqlalchemy.orm.Session)

    Returns:
        str: 保證在資料庫中唯一的 8 位短 ID 字串
    """
    while True:
        short_id = str(uuid.uuid4())[:8]
        existing_entry = session.query(URL).filter(URL.id == short_id).first()
        if not existing_entry:
            return short_id
