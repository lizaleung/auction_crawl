import json
import re

import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64"
}
response = requests.get(
    "https://onlineonly.christies.com/s/patrick-moorhead-hidden-treasures/lots/1975?filters=&page=5&searchphrase=&sortby=LotNumber&themes=&lid=1&sc_lang=en",
    verify=False, headers=headers)
data_dump = re.match(r".*window.chrComponents = ({.*?});", response.text, re.DOTALL).group(1)
data = json.loads(data_dump)
print(data)
