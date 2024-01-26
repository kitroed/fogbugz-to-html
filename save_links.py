from urllib.parse import parse_qs, urlparse
from requests import get
from http import cookiejar

o = urlparse('//<fogbugz-instance-name>.fogbugz.com/default.asp')
if o.query:
    print(o.query)
    pqs = parse_qs(o.query)
print(o)
