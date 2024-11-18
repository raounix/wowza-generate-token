# wowza-generate-token
### this code in python version of wowza-generate-token in this repo: https://github.com/mehdirajabi59/wowza-generate-token

**Example** :

```
from wowza_generate_token import WowzaGenerateToken
import time

token = WowzaGenerateToken("wowzatoken","mySharedSecret")
token.set_client_ip("192.168.1.1")
token.set_url("https://ws.classino.com/redirect/vod_test/_definst_/konkor1404/khani/mehr/farsi/1/smil:hd_test.smil")

token.set_hash_method(token.SHA256)
start_time = int(time.time())  # Current time in seconds since epoch
end_time = start_time + (3 * 60 * 60)  # Add 3 hours in seconds

token.set_extra_params({"endtime": end_time, "starttime": start_time})

print(token.get_full_url())
```