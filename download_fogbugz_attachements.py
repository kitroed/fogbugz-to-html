# download attachements script
from os import makedirs, path
import requests
from urllib.parse import parse_qs, urlparse
import csv

api_token = '<api-token-here>'
subdomain = '<fogbugz-instance-name>'

# load a dicationary of avatar images that can be looked up by id
with open('wiki_attachments_querystring.csv', mode='r') as attachments_querystring_csv_file:
    reader = csv.reader(attachments_querystring_csv_file)
    header = next(reader)
    attachments_querystring = {rows[0]:rows[1] for rows in reader}

for querystring in attachments_querystring.values():
        attachment_id = parse_qs(querystring)['ixAttachment'][0]
        filename = parse_qs(querystring)['sFilename'][0].replace(':', '_').replace('?', '_').replace('"', '_').replace('*', '_').replace('/', '_').replace('\\', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('.unsafe', '')
        save_dir = path.join('wikis', 'attachments', attachment_id)
        file_path = path.join(save_dir, filename)
        url = 'https://' + subdomain + '.fogbugz.com/default.asp?' + querystring + '&token=' + api_token

        if not path.exists(file_path):
            if not path.isdir(save_dir):
                makedirs(save_dir)
            r = requests.get(url, allow_redirects=True)
            print('Saving file', file_path)
            with open(file_path, 'wb') as f:
                f.write(r.content)
