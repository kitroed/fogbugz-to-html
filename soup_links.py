from glob import glob
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urlparse

con = sqlite3.connect('url_data.db')
cur = con.cursor()

# Stuffing hyperlink data into a SQLite database to quickly analyze

# scheme
# netloc
# path
# params
# query
# fragment

cur.execute('CREATE TABLE hyperlink (id INTEGER NOT NULL, source_file TEXT NOT NULL, a TEXT NOT NULL, href TEXT, scheme TEXT, netloc TEXT, path TEXT, params TEXT, query TEXT, fragment TEXT, PRIMARY KEY(id AUTOINCREMENT))')
cur.execute('CREATE TABLE image (id INTEGER NOT NULL, source_file TEXT NOT NULL, img TEXT NOT NULL, src TEXT, scheme TEXT, netloc TEXT, path TEXT, params TEXT, query TEXT, fragment TEXT, PRIMARY KEY(id AUTOINCREMENT))')

for casehtml in glob('cases/case*.html'):
    with open(casehtml, 'r', encoding='utf8') as fp:
        print('parsing file:', fp.name)
        soup = BeautifulSoup(fp, features='html.parser')

        for page_a_tag in soup.find_all('a'):
            h = page_a_tag.get('href')
            pr = urlparse(h)
            cur.execute('insert into hyperlink (source_file, a, href, scheme, netloc, path, params, query, fragment) values (?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(fp.name), str(page_a_tag), h, pr.scheme, pr.netloc, pr.path, pr.params, pr.query, pr.fragment))
        
        for page_img_tag in soup.find_all('img'):
            s = page_img_tag.get('src')
            pr = urlparse(s)
            cur.execute('insert into image (source_file, img, src, scheme, netloc, path, params, query, fragment) values (?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(fp.name), str(page_img_tag), s, pr.scheme, pr.netloc, pr.path, pr.params, pr.query, pr.fragment))

    con.commit()
con.close()


# I grabbed all the attachment links by unioning the two types I was grabbing that contain "ixAttachment" in the name:
# with url_table as (select href as url from hyperlink union select src as url from image) select * from url_table where url like '%ixAttachment%';

# I could try using the urllib.parse to pull it apart for download.
# My biggest challenge right now is getting wget or something to actually download the thing

# another option: `http.cookiejar.MozillaCookieJar(filename, delayload=None, policy=None) + requests? no need for wget?