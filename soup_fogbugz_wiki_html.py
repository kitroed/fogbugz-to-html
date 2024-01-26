from glob import glob
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse, quote
import csv
import logging
from os.path import exists
import ast

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('Started')

    top_html_string = '<!DOCTYPE html><html><head><meta charset="utf-8">'
    post_title_html_string = '''<link href="../main-FogBugz-wiki.css" rel="stylesheet">
</head><body><div id="main-wrap"><section class="case">
<article><div class="contentWikiView article-content">
<div id="wiki-page-header">'''
    post_header_html_string = '</div><div id="wiki-page-content">'
    bottom_html_string = '</div></article></section></div></body></html>'

    # load a dictionary of attachment paths that can be looked up by id
    with open('wiki_attachments.csv', mode='r') as attachments_csv_file:
        reader = csv.reader(attachments_csv_file)
        header = next(reader)
        attachments = {rows[0]:rows[1] for rows in reader}

    # load a dictionary from csv with wiki urls that can be looked up by W<id>
    with open('wikis.csv', mode='r') as wiki_csv_file:
        reader = csv.reader(wiki_csv_file)
        header = next(reader)
        wikis = {rows[0]:rows[1] for rows in reader}

    # load a dictionary from csv with wiki create html strings that can be looked up by W<id>
    with open('wiki_revision_1.csv', mode='r') as wiki_create_csv_file:
        reader = csv.reader(wiki_create_csv_file)
        header = next(reader)
        create_spans = {rows[0]:rows[1] for rows in reader}

    # load a dictionary from csv with wiki modified html strings that can be looked up by W<id>
    with open('wiki_revision_final.csv', mode='r') as wiki_modified_csv_file:
        reader = csv.reader(wiki_modified_csv_file)
        header = next(reader)
        modified_spans = {rows[0]:rows[1] for rows in reader}

    for wikihtml in glob('wikis_original/**/*.html', recursive=True):
        # if exists(wikihtml.replace('wikis_original', 'wikis')):
        #     logging.info(wikihtml + ' already processed.')
        #     continue
        with open(wikihtml, 'r', encoding='utf-8-sig') as read_file:
            logging.debug('Parsing file: %s', read_file.name)
            soup = BeautifulSoup(read_file, features='html.parser')


        title = read_file.name
        title = soup.find('h1').text
        wiki_id = read_file.name.split('\\W')[-1].split()[0]

        # rebuild head thru body tag for start of document
        # insert title into new head string and have trailing body tag
        new_head_to_body = top_html_string + '<title>' + str(title) + '</title>' + post_title_html_string + create_spans[wiki_id] + '<br>' + modified_spans[wiki_id] + post_header_html_string

        for input_tag in soup.find_all('input'):
            if input_tag['plugin_type'] == 'toc':
                new_tag = soup.new_tag('code')
                new_tag.string = '[[_TOC_]]'
                input_tag.replace_with(new_tag)
            elif input_tag['plugin_type'] == 'codesnippet':
                jsonlike_data = input_tag['plugin_data']
                # wow! it's a python literal, not json:
                code = ast.literal_eval(jsonlike_data)['sContent']
                new_pre_tag = soup.new_tag('pre')
                new_pre_tag.string = code
                new_pre_tag.string.wrap(soup.new_tag('code'))
                input_tag.replace_with(new_pre_tag)

            else:
                print('decomposing: [[', input_tag, ']]', sep='')
                input_tag.decompose()

        # process all hyperlinks and images for URL updates
        for a_tag in soup.find_all('a'):
            href = urlparse(a_tag.get('href'))
            # if it references internal fogbugz action or search links, just un-hyperlink it.
            if href.netloc == '<fogbugz-instance-name>.kilnhg.com':
                logging.debug('found kilnhg link. Unwrapping <a> tag', href.path)
                a_tag.unwrap()
            elif len(href.path) > 0 and (href.path.startswith('/f/filters') or href.path.startswith('/f/search') or href.path.startswith('/f/personInfo/activity') or 'ixBug' in href.query):
                logging.debug('found url path: %s unwrapping <a> tag', href.path)
                a_tag.unwrap()
            # update case references (works!!)
            elif len(href.path) > 0 and (href.path.startswith('/f/cases/')):
                a_tag['href'] = href._replace(scheme='', netloc='', path=href.path.removeprefix('/f/cases/').rsplit('/')[0]+'.html').geturl()
            # wiki
            elif len(href.path) > 0 and ('default.asp' in href.path and href.query.startswith('W')):
                try:
                    a_tag['href'] = quote('../../' + wikis[href.query])
                except:
                    logging.error('unable to lookup wiki ' + href.query + ' unwrapping instead.')
                    a_tag.unwrap()
            elif len(href.path) > 0 and ('default.asp' in href.path and href.query.isdigit()):
                a_tag['href'] = href._replace(scheme='', netloc='', path='../../cases/' + href.query + '.html', query='').geturl()

            # attachment href replace
            elif len(href.query) > 0 and 'ixAttachment' in href.query:
                a_tag['href'] = '../' + quote(attachments[parse_qs(href.query)['ixAttachment'][0]])

        # images
        for img_tag in soup.find_all('img'):
            src = urlparse(img_tag.get('src'))
            logging.debug(src)
            # if attachment 0, set to hard-coded Kiwi.png path
            if len(src.path) > 0 and (src.path == '/default.asp' and src.query == 'ixAttachment=0&pg=pgDownloadProfilePicture&pxSize=32'):
                img_tag['src'] = '../' + quote('attachments/0/Kiwi.png')
            # if ixPerson in query use the person id in the and get the local url from the lookup
            # elif len(src.query) > 0 and 'ixPerson' in src.query:
            #     img_tag['src'] = quote(avatars[parse_qs(src.query)['ixPerson'][0]])
            # attachment src replace
            elif len(src.query) > 0 and 'ixAttachment' in src.query:
                img_tag['src'] = '../' + quote(attachments[parse_qs(src.query)['ixAttachment'][0]])


        output_soup = BeautifulSoup(new_head_to_body + str(soup) + bottom_html_string, features='html.parser')

        # new html file will be cases/12345.html instead of content/12345.html
        with open(read_file.name.replace('wikis_original', 'wikis'), 'w', encoding='utf-8') as write_file:
            logging.info('Saving %s', write_file.name)
            write_file.write(output_soup.decode(formatter='html5'))
        
    logging.info('Finished')

if __name__ == '__main__':
    main()
