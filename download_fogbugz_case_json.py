
# download case data (json format) from API
import os
import requests
from urllib.parse import parse_qs, urlparse
import json


api_token = '<api-token-here>'
subdomain = '<fogbugz-instance-name>'

start_case = 1
end_case = 13327

cases = list((str(i) for i in range(start_case, end_case+1)))

url = 'https://' + subdomain + '.fogbugz.com/api/viewCase'

print("Start")
for case in cases:
    response = requests.post(url, data=json.dumps({"ixBug": case, "token": api_token,"cols": ["ixBug",
                                                    "ixBugParent", "ixBugChildren", "tags", "fOpen", "sTitle", "sOriginalTitle", "sLatestTextSummary",
                                                    "ixBugEventLatestText", "ixProject", "ixArea", "ixPersonAssignedTo", "sPersonAssignedTo", "sEmailAssignedTo", "ixPersonOpenedBy",
                                                    "ixPersonClosedBy", "ixPersonResolvedBy", "ixPersonLastEditedBy", "ixStatus", "ixBugDuplicates", "ixBugOriginal", "ixPriority",
                                                    "ixFixFor", "sFixFor", "dtFixFor", "sVersion", "sComputer", "hrsOrigEst", "hrsCurrEst",
                                                    "hrsElapsedExtra", "hrsElapsed", "sCustomerEmail", "ixMailbox", "ixCategory", "dtOpened", "dtResolved",
                                                    "dtClosed", "ixBugEventLatest", "dtLastUpdated", "fReplied", "fForwarded", "sTicket", "ixDiscussTopic",
                                                    "dtDue", "sReleaseNotes", "ixBugEventLastView", "dtLastView", "ixRelatedBugs", "sScoutDescription", "sScoutMessage",
                                                    "fScoutStopReporting", "dtLastOccurrence", "fSubscribed", "dblStoryPts", "nFixForOrder", "events", "minievents", "ixKanbanColumn",
                                                    "sKanbanColumn"]}),headers = {'content-type': 'application/json'}).json()

    if not os.path.exists(os.path.join('json', case + '.json')) and len(response) > 0:
        print('Saving file', case + '.json')
        with open(os.path.join('json', case + '.json'), 'w', encoding='utf8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)
print("Finished")
