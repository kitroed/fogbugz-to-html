
# download case data (json format) from API
import os
import requests
from urllib.parse import parse_qs, urlparse
import csv
import json
import xmltodict

    # load a dictionary of person names
with open('persons.csv', mode='r') as persons_csv_file:
    reader = csv.reader(persons_csv_file)
    header = next(reader)
    persons = {rows[0]:rows[1] for rows in reader}

api_token = '<api-token-here>'
subdomain = '<fogbugz-instance-name>'

print('id', 'revision', 'person', 'timestamp', sep='\t')

response = requests.get('https://' + subdomain + '.fogbugz.com/api.asp?token=' + api_token + '&cmd=listWikis')
wiki_data = xmltodict.parse(response.content)
# print(json.dumps(wiki_data, indent=4))
for wiki in wiki_data['response']['wikis']['wiki']:
    wiki_response = requests.get('https://' + subdomain + '.fogbugz.com/api.asp?token=' + api_token + '&cmd=listArticles&ixWiki=' + wiki['ixWiki'])
    # print(json.dumps(xmltodict.parse(wiki_response.content), indent=4))
    wiki_page_data = xmltodict.parse(wiki_response.content)
    for page in wiki_page_data['response']['articles']['article']:
        if type(page) is dict:
            revisions_response = requests.get('https://' + subdomain + '.fogbugz.com/api.asp?token=' + api_token + '&cmd=listRevisions&ixWikiPage=' + page['ixWikiPage'])
            revisions_data = xmltodict.parse(revisions_response.content)
            # print(json.dumps(xmltodict.parse(revisions_response.content), indent=4))
            # for revision in revisions_data['response']['revisions']['revision']:
            #     if type(revision) is dict:
            #         print(page['ixWikiPage'], revision['nRevision'], persons[revision['ixPerson']], revision['dt'], sep='\t')
            #     else:
            #         print(page['ixWikiPage'], revision, sep='\t')
            try:
                rev1 = revisions_data['response']['revisions']['revision'][len(revisions_data['response']['revisions']['revision'])-1]
            except:
                rev1 = revisions_data['response']['revisions']['revision']
            print(page['ixWikiPage'], rev1['nRevision'], persons[rev1['ixPerson']], rev1['dt'], sep='\t')
        else:
            print(page)
        
        # article_response = requests.get('https://' + subdomain + '.fogbugz.com/api.asp?token=' + api_token + '&cmd=viewArticle&ixWikiPage=' + page['ixWikiPage'])
        # print(json.dumps(xmltodict.parse(article_response.content), indent=4))


# if not os.path.exists(os.path.join('json', case + '.json')) and len(response) > 0:
#     print('Saving file', case + '.json')
#     with open(os.path.join('json', case + '.json'), 'w', encoding='utf-8') as f:
#         json.dump(response, f, ensure_ascii=False, indent=4)
