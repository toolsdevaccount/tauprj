from urllib.parse import urlencode
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)


def GetUrl(param, incoming_url):
    try:
        parameters = urlencode({'row': param})
        if '?row' in incoming_url:
            incoming_url = incoming_url.split('?')[0]
        else:
            incoming_url = incoming_url.split('&')[0]

        if '?' in incoming_url:
            url = f'{incoming_url}&{parameters}'
        else:
            url = f'{incoming_url}?{parameters}'

    except Exception as e:
        message = "URLを継承するとにエラーが発生しました"
        logger.error(message)

    return url
