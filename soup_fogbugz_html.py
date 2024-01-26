from glob import glob
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse, quote
import csv
import logging
from os.path import exists

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('Started')

    top_html_string = '<!DOCTYPE html><html><head><meta charset="utf-8">'
    post_title_html_string = '<link href="styles/main-FogBugz.css" rel="stylesheet"><link href="images/favicon_fogbugz.ico" rel="shortcut icon"><link href="images/apple-touch-icon.png" rel="apple-touch-icon"></head><body>'
    bottom_html_string = '</body></html>'

    # load a dicationary of avatar images that can be looked up by id
    with open('avatars.csv', mode='r') as avatars_csv_file:
        reader = csv.reader(avatars_csv_file)
        header = next(reader)
        avatars = {rows[0]:rows[1] for rows in reader}

    # load a dictionary of attachment paths that can be looked up by id
    with open('attachments.csv', mode='r') as attachments_csv_file:
        reader = csv.reader(attachments_csv_file)
        header = next(reader)
        attachments = {rows[0]:rows[1] for rows in reader}

    # load a dictionary from csv with wiki urls that can be looked up by W<id>
    with open('wikis.csv', mode='r') as wiki_csv_file:
        reader = csv.reader(wiki_csv_file)
        header = next(reader)
        wikis = {rows[0]:rows[1] for rows in reader}

    for casehtml in glob('content/*.html'):
        if exists(casehtml.replace('content', 'cases')):
            logging.info(casehtml + ' already processed.')
            continue
        with open(casehtml, 'r', encoding='utf8') as read_file:
            logging.info('Parsing file: %s', read_file.name)
            soup = BeautifulSoup(read_file, features='html.parser')

        # main article parent, parent, parent is div id 'main-wrap' (or just get by id)
        # main_wrap = soup.article.parent.parent.parent
        main_wrap = soup.find('div', id='main-wrap')

        # rebuild head thru body tag for start of document
        # insert title into new head string and have trailing body tag
        new_head_to_body = top_html_string + str(soup.title) + post_title_html_string

        # delete <div id="top-notifications">
        try:
            main_wrap.find('div', id='top-notifications').decompose()
        except:
            logging.debug("didn't find top-notifications")

        # delete all nav inner html (top)
        try:
            for nav_tag in main_wrap.find_all('nav'):
                logging.debug("found nav to clear out")
                # clear contents
                nav_tag.clear()
        except:
            logging.debug("didn't find nav to clean")

        #  delete <label id="sidebarCorrespondent"
        try:
            main_wrap.find('label', id='sidebarCorrespondent').decompose()
        except:
            logging.debug("didn't find sidebarCorrespondent")
        
        # delete <label id="sidebarReleaseNotes"
        try:
            main_wrap.find('label', id='sidebarReleaseNotes').decompose()
        except:
            logging.debug("didn't find sidebarReleaseNotes")
        # delete <div class="toggle-duplicates-container">
        try:
            main_wrap.find('div', 'toggle-duplicates-container').decompose()
        except:
            logging.debug("didn't find div toggle-duplicates-container")
        # delete <span class="rss field">
        try:
            main_wrap.find('span', 'rss').decompose()
        except:
            logging.debug("didn't find span rss")
        # delete `<div id="sidebarSubscribe">`
        try:
            main_wrap.find('div', id='sidebarSubscribe').decompose()
        except:
            logging.debug("didn't find sidebarSubscribe")
        # delete <button class="m-btn working-on-case"
        try:
            main_wrap.find('button', 'working-on-case').decompose()
        except:
            logging.debug("didn't find button working-on-case")
        # delete inner html of <span class="right-event-action-wrapper">
        try:
            for span in main_wrap.find_all('span', 'right-event-action-wrapper'):
                span.clear()
        except:
            logging.debug("didn't find span right-event-action-wrapper")
        # delete <div class="drop-mask hidden">
        try:
            main_wrap.find('div', 'drop-mask').decompose()
        except:
            logging.debug("didn't find div drop-mask")
        # delete <div id="case-errors-container">
        try:
            main_wrap.find('div', id='case-errors-container').decompose()
        except:
            logging.debug("didn't find div case-errors-container")
        # delete <div id="sidebar-outline">
        try:
            main_wrap.find('div', id='sidebar-outline').decompose()
        except:
            logging.debug("didn't find div sidebar-outline")

        # process all hyperlinks and images for URL updates
        for a_tag in main_wrap.find_all('a'):
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
            elif len(href.path) > 0 and (href.path == '/default.asp' and href.query.startswith('W')):
                try:
                    a_tag['href'] = quote('../' + wikis[href.query])
                except:
                    logging.error('unable to lookup wiki ' + href.query + ' unwrapping instead.')
                    a_tag.unwrap()
            # attachment href replace
            elif len(href.query) > 0 and 'ixAttachment' in href.query:
                a_tag['href'] = quote(attachments[parse_qs(href.query)['ixAttachment'][0]])

        # images
        for img_tag in main_wrap.find_all('img'):
            src = urlparse(img_tag.get('src'))
            logging.debug(src)
            # if attachment 0, set to hard-coded Kiwi.png path
            if len(src.path) > 0 and (src.path == '/default.asp' and src.query == 'ixAttachment=0&pg=pgDownloadProfilePicture&pxSize=32'):
                img_tag['src'] = quote('attachments/0/Kiwi.png')
            # if ixPerson in query use the person id in the and get the local url from the lookup
            elif len(src.query) > 0 and 'ixPerson' in src.query:
                img_tag['src'] = quote(avatars[parse_qs(src.query)['ixPerson'][0]])
            # attachment src replace
            elif len(src.query) > 0 and 'ixAttachment' in src.query:
                img_tag['src'] = quote(attachments[parse_qs(src.query)['ixAttachment'][0]])


        output_soup = BeautifulSoup(new_head_to_body + str(main_wrap) + bottom_html_string, features='html.parser')

        # new html file will be cases/12345.html instead of content/12345.html
        with open(read_file.name.replace('content', 'cases'), 'w', encoding='utf8') as write_file:
            logging.info('Saving %s', write_file.name)
            write_file.write(output_soup.decode(formatter='html5'))
        
    logging.info('Finished')

if __name__ == '__main__':
    main()
