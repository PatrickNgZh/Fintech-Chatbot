import base64
import json
import os

import requests


class ImageUtil:
    def __init__(self):
        self.key = os.getenv('IMAGE_KEY', None)
        self.base = 'https://api.imgbb.com/1/upload?key='
        self.url = self.base + self.key

    def upload(self, file):
        base64_data = base64.b64encode(file)
        data = {'image': base64_data}
        response = requests.post(url=self.url, data=data)
        result = json.loads(response.text)['data']['url']
        return result
