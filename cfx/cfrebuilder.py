#!/usr/bin/env python
# This Script helps to rebuild deleted context field
"""
Script   : Context Field Rebuilder for Custom field
Author   : Prince Nyeche
Platform : Atlassian Jira Cloud
Version  : 0.4
**************************************************************************
Required libraries : requests, tqdm
Install via        : requirements.txt file
License            : MIT License Copyright (c) 2020 Prince Nyeche
API Token can be generated from https://id.atlassian.com/manage/api-tokens
**************************************************************************
"""

import json
import requests
from requests.auth import HTTPBasicAuth
import sys
from cfx.cfcreate import CreateField
from tqdm import tqdm
from threading import Thread

__version__ = "0.4"
__author__ = "Prince Nyeche"
email = None
token = None
baseurl = ""
pkey = ""
auth_request = None
headers = None
jql_data = None
cm_dat = None
field_name = None


# we need to find all the Issues where the custom_field existed before
class IssueHistory:
    """
    In order to get the custom_field values, we need to know in the changelog  history
    that it has existed there before at least at one point in time. if we can find it,
    then we can iterate through all the various issue keys. so for now, we store all
    our issue key to d which we unpack as d["key"] then we can call it
    later since we passed it as positional argument or kwargs
    """

    def filter_issue_keys(self, data=None):
        global jql_data  # saving our JQL search here in a Global variable
        global field_name  # our custom field name
        jql_data = json.loads(data.content)
        x = Field()
        i = CreateField()
        print("Filtering Issue Keys, {} Issues returned...".format(jql_data["total"]))
        field_name = input("Enter the Name of the Custom Field: \n")
        # to properly find a way to validate all fields on the instance.
        print("Searching...")
        a = x.get_field_types()
        if a is not None:
            print(f"Found field: \"{field_name}\", Searching option...")
            self.sub_filter(q=field_name)
        elif a is None:
            print(f"\"{field_name}\" seems like it doesn't exist, do you want to Create it? "
                  f"Please check in the UI before proceeding. if unsure!?")
            i.create_cf(field_name=field_name, baseurl=baseurl, auth_request=auth_request, headers=headers)

    @staticmethod
    def sub_filter(q, retries=3, trials="Try Again!"):
        # field_name = q
        x = Field()
        a = x.get_field()
        if a is not None:
            # a = check.get_field_types(field_name=field_name).__getitem__(0)
            r = a.__getitem__(3)
            x.get_field_option(g=r)
        elif x.get_field() is None:
            context = f"A Context doesn't exist on {field_name}, we'll build it now, \n" \
                      f"please add a context via the UI " \
                      f"https://{baseurl}/secure/admin/ViewCustomFields.jspa" \
                      " then press 'Enter' \n"
            repeat(context=context, retries=retries, trials=trials)
            # Certain field types doesn't support customField option endpoint. check `build.py` file
            #  for a list of fields. so no need to rebuild the cf, let's only check if it has context
            no_option()
        # end of if block

    # Issue History search, it finds out the values in the change log then extract and transform it.
    def get_field_issue_history(self):
        print("We're gathering the Custom field options to Rebuild it.\n"
              "We'll let you know when we're done...")
        if list(jql_data["issues"]) is not None:
            total = jql_data["total"]
            maxResults = 50
            startAt = 0
            fullNumber = int(total / 1)
            while total > maxResults or total < maxResults:
                if startAt < fullNumber:
                    webEx = ("https://{}/rest/api/3/search?jql=project%20in%20({})&startAt={}&maxResults={}"
                             .format(baseurl, pkey, startAt, maxResults))
                    info = requests.get(webEx, auth=auth_request, headers=headers)
                    wjson = json.loads(info.content)
                    for d in tqdm(list(wjson["issues"])):
                        # print("Matching, Issue key " + d["key"] + " to URL...") # uncomment if you want to trail
                        webURL = ("https://" + baseurl + "/rest/api/3/issue/" + d["key"] + "/changelog")
                        data = requests.get(webURL, auth=auth_request, headers=headers)
                        fjson = json.loads(data.content)
                        if data.status_code != 200:
                            print("Error: Unable to access the Changelog History...\n", fjson, sep=",")
                        else:
                            if d["key"] is not None:
                                for i in fjson["values"]:
                                    fetch = i["items"]
                                    if fetch is not None:
                                        for j in fetch:
                                            if j["field"] == field_name:
                                                self.create_back_cf_options((j["field"], j["fieldId"],
                                                                             j["fromString"], j["toString"],
                                                                             j["to"]),
                                                                            d=d)
                # show our progress bar with time elapse
                print("", end="\r")
                startAt += 50
                if startAt > (fullNumber - 1):
                    break

        print("*" * 90)
        print("Custom field Options has been Added".upper())
        # end of loop.

    # below method is to create back the options for the custom_field, since we can identify it
    @staticmethod
    def create_back_cf_options(j=None, d=None):
        """
         :param j: stores the value of our fromString and toString we'll need this later
         but we only want the toString which is j[3]
         :param d: stores our issue key, so we can always call this later as d["key"]
         Below we ensure we extract our cf id and the values in j[1].
        """
        x = Field()
        v = CreateField()
        s = j[1]
        seq3 = s.strip("customfield_")
        z = x.get_field().__getitem__(
            2)
        # handling multiple option values to re-create back it's option.
        webURL = ("https://{}/rest/api/3/customField/{}/option".format(baseurl, seq3))
        # create option for multi_select or multi_checkboxes field
        if z == v.multiselect or \
                z == v.multicheckboxes:
            if x.fix_multi(j=j).__len__() > 0:
                c = x.fix_multi(j=j)
                for l in c:
                    if l in str(x.return_op_value()):
                        pass
                    else:
                        payload = (
                            {
                                "options": [
                                    {
                                        "cascadingOptions": [],
                                        "value": l
                                    }
                                ]

                            }
                        )
                        data = requests.post(webURL, auth=auth_request, json=payload, headers=headers)
                        csd(data=data, j=j, d=d, field_name=field_name)
        elif str(j[3]) == "":
            pass
        elif z == v.cascadingselect:
            # Ability to post to options, both fields needs to be split into a tuple
            p = post_cassi(j=j)
            if len(p) > 3:
                payload = (
                    {
                        "options": [
                            {
                                # TODO: work on getting the cascading select list to post multiple values
                                "value": p.__getitem__(1).lstrip(),
                                "cascadingOptions": [p.__getitem__(3).lstrip()
                                                     ]
                            }

                        ]

                    }
                )
                data = requests.post(webURL, auth=auth_request, json=payload, headers=headers)
                csd(data=data, j=j, d=d, field_name=field_name)
            elif len(p) <= 3:
                payload = (
                    {
                        "options": [
                            {
                                "value": p.__getitem__(1).lstrip(),
                                "cascadingOptions": []
                            }
                        ]

                    }
                )
                data = requests.post(webURL, auth=auth_request, json=payload, headers=headers)
                csd(data=data, j=j, d=d, field_name=field_name)
        elif z == v.select or z == v.radiobuttons:
            payload = (
                {
                    "options": [
                        {
                            "cascadingOptions": [],
                            "value": j[3]
                        }
                    ]

                }
            )
            data = requests.post(webURL, auth=auth_request, json=payload, headers=headers)
            csd(data=data, j=j, d=d, field_name=field_name)
        # end create option method


def csd(data=None, j=None, d=None, field_name=None):
    if data.status_code != 201:
        pass
        # print("Error: Unable to Post the Data to the Issue {} with reason ...".format(data.status_code, data.reason))
    else:
        pass
        # print("Creating {} field option for {}".format(j[3], j[0]))
        # end or exit post request
        # uncomment if you want to see the post information.


# sub_class to IssueHistory
class Field(IssueHistory):
    """
    `get_field` and `get_field_type`
    check if the field exist by looking at the endpoint /rest/api/3/field.
    if the field has context it should exist, we should search for that instead and see
    if our options exist therein. if it doesn't then we build it back
    """

    # c is returned as a tuple, we can use methods in tuple to fetch the required value
    # e.g. __getitem__() method which accepts int value for index beginning at 0.
    @staticmethod
    def get_field():
        webURL = ("https://" + baseurl + "/rest/api/3/field")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        fjson = json.loads(data.content)
        for c in list(fjson):
            if field_name in c["name"]:
                if c["schema"] is not None:
                    return c["name"], c["id"], c["schema"]["custom"], c["schema"]["customId"]

    # a is returned as a tuple, we think this method is unreliable, change it to extend the function.
    @staticmethod
    def get_field_types():
        #  To find the type of field_type used, use this endpoint
        #  https://<your-instance>.atlassian.net/rest/api/3/field/search?type=custom
        #  values accepted "custom". the default result returned is only 50.
        #  however, we're able to run a loop of each option, record by record.
        webURL = ("https://{}/rest/api/3/field/search?type=custom"
                  .format(baseurl))
        data = requests.get(webURL, auth=auth_request, headers=headers)
        pjson = json.loads(data.content)
        total = pjson["total"]
        maxResults = 50
        startAt = 0
        fullNumber = int(total / 1)
        while total > maxResults or total < maxResults:
            if startAt < fullNumber:
                webEx = ("https://{}/rest/api/3/field/search?type=custom&startAt={}&maxResults={}"
                         .format(baseurl, startAt, maxResults))
                info = requests.get(webEx, auth=auth_request, headers=headers)
                wjson = json.loads(info.content)
                for a in wjson["values"]:
                    if a["name"] == field_name:
                        return a["schema"]["custom"], a["schema"]["customId"], a["id"], a["name"]

            startAt += 50
            if startAt > (fullNumber - 1):
                break

    # wrapping the field options in order to post the issue
    def get_field_option(self, g=None):
        global cm_dat
        v = CreateField()
        user = Field()
        webURL = ("https://{}/rest/api/3/customField/{}/option".format(baseurl, g))
        data = requests.get(webURL, auth=auth_request, headers=headers)
        cm_dat = json.loads(data.content)
        k = user.get_field().__getitem__(
            2)
        if k == v.userpicker or \
                k == v.textfield or \
                k == v.url or \
                k == v.datepicker or \
                k == v.datetime or \
                k == v.float or \
                k == v.textarea or \
                k == v.multigrouppicker or \
                k == v.multiuserpicker or \
                k == v.grouppicker or \
                k == v.labels or \
                k == v.project or \
                k == v.multiversion or \
                k == v.version or \
                k == v.readonlyfield or \
                k == v.importid:
            print(f"{field_name} doesn't need options, this field self rebuilds")
            print(f"Rebuilding not required...OK")
            sys.exit(0)
        else:
            self.get_field_value(cm_dat=cm_dat)

    def get_field_value(self, cm_dat=None):
        if "self" in str(cm_dat):
            if str(cm_dat["values"]) == "[]":
                print(f"The Context for {field_name} has no values, defaulting to build options...")
                # Let's use threading for any post request
                Thread(target=self.get_field_issue_history()).start()
            else:
                print(f"{field_name} has values posting to issue...")
                for a in cm_dat["values"]:
                    if a["value"] is not None:
                        pass
                # Let's use threading for any post request
                Thread(target=self.post_field_data()).start()
        elif "errorMessages" in str(cm_dat):
            print(f"Either Global Context for {field_name} doesn't exist, or \n"
                  f"you do not have permission on it.Please check via the UI")
            sys.exit(1)

    # TODO: check if values has been posted before
    @staticmethod
    def return_op_value(i=None):
        if str(cm_dat["values"]) == "[]":
            return i
        else:
            for i in cm_dat["values"]:
                pass
            return i

    # TODO: get this field value as a list then post it back.
    @staticmethod  # method for getting multi_choices values
    def fix_multi(j=None):
        m = str(j[3]).split(",")
        if m.__len__() > 0:
            return m

    # if values exist, let's just post it instead.
    def post_field_data(self):
        print("We're posting the option values to the Issues. This might take a while... \n"
              "A completion message will be shown, when we're done.")
        if list(jql_data["issues"]) is not None:
            total = jql_data["total"]
            maxResults = 50
            startAt = 0
            fullNumber = int(total / 1)
            while maxResults < total or maxResults > total:
                if startAt < fullNumber:
                    webEx = ("https://{}/rest/api/3/search?jql=project%20in%20({})&startAt={}&maxResults={}"
                             .format(baseurl, pkey, startAt, maxResults))
                    info = requests.get(webEx, auth=auth_request, headers=headers)
                    wjson = json.loads(info.content)
                    for d in tqdm(list(wjson["issues"])):
                        # print("Matching, Issue key " + d["key"] + " to URL...")  # uncomment if you want to trail
                        webURL = ("https://" + baseurl + "/rest/api/3/issue/" + d["key"] + "/changelog")
                        data = requests.get(webURL, auth=auth_request, headers=headers)
                        fjson = json.loads(data.content)
                        if data.status_code != 200:
                            print("Error: Unable to access the Changelog History...\n", fjson, sep=",")
                        else:
                            if d["key"] is not None:
                                for i in fjson["values"]:
                                    fetch = i["items"]
                                    if fetch is not None:
                                        for j in fetch:
                                            if j["field"] == field_name:
                                                self.rebuild_issue_custom_field_values((j["field"], j["fieldId"],
                                                                                        j["fromString"], j["toString"],
                                                                                        j["to"]),
                                                                                       d=d)
                # show our progress bar with time elapse
                print("", end="\r")
                startAt += 50
                if startAt > (fullNumber - 1):
                    print("Total number of Issues fixed: {}, Max Loop/Issue: {},  Loop Record #: {}"
                          .format(total, maxResults, startAt))
                    break

        print("Custom Field Rebuilder Completed...".upper())
        sys.exit(0)

    # base method for creating back custom field values
    def rebuild_issue_custom_field_values(self, j=None, d=None):
        v = CreateField()
        webURL = ("https://{}/rest/api/3/issue/{}".format(baseurl, d["key"]))
        b = self.get_field()
        # if the value of the field is 'None' (empty) we would like to post that as well.
        if j[3] == "":
            # Post "None" data, works for single / cascading select list
            if b.__getitem__(2) == v.multicheckboxes or \
                    b.__getitem__(2) == v.multiselect:
                payload = \
                    {
                        "fields": {
                            b.__getitem__(1):

                                []

                        }
                    }
                response = requests.put(webURL, json=payload, auth=auth_request, headers=headers)
                psd(response=response, d=d, j=j)
            elif b.__getitem__(2) == v.select or \
                    b.__getitem__(2) == v.cascadingselect or \
                    b.__getitem__(2) == v.radiobuttons:
                payload = \
                    {
                        "fields": {
                            b.__getitem__(1):

                                j[4]

                        }
                    }
                response = requests.put(webURL, json=payload, auth=auth_request, headers=headers)
                psd(response=response, d=d, j=j)
                # posting values for multi-checkbox / multi select fields
        #  post values for multiple choice fields (Multi_checkboxes, Multi_select)
        elif b.__getitem__(
                2) == v.multiselect or \
                b.__getitem__(2) == v.multicheckboxes:
            # post method multi choice fields
            payload = \
                {
                    "fields":
                        {
                            b.__getitem__(1):
                            #  iterate through the field options and post it
                                post_multi(j=j)

                        }
                }
            response = requests.put(webURL, auth=auth_request, json=payload, headers=headers)
            psd(response=response, d=d, j=j)
        # below is used to post to cascading select field
        elif b.__getitem__(
                2) == v.cascadingselect:
            p = post_cassi(j=j)
            if len(p) > 3:
                payload = \
                    {
                        "fields":
                            {
                                b.__getitem__(1):
                                    {
                                        "value": p.__getitem__(1).lstrip(),
                                        "child": {
                                            "value": p.__getitem__(3).lstrip()
                                        }
                                    }

                            }
                    }
                response = requests.put(webURL, auth=auth_request, json=payload, headers=headers)
                psd(response=response, d=d, j=j)
            elif len(p) <= 3:
                payload = \
                    {
                        "fields":
                            {
                                b.__getitem__(1):
                                    {
                                        # post  single values of cascading fields
                                        "value": p.__getitem__(1).lstrip()
                                    }

                            }
                    }
                response = requests.put(webURL, auth=auth_request, json=payload, headers=headers)
                psd(response=response, d=d, j=j)
        # Posting single values for normal fields
        elif b.__getitem__(2) == v.radiobuttons or \
                b.__getitem__(2) == v.select:
            payload = \
                {
                    "fields":
                        {
                            b.__getitem__(1):
                                {
                                    "value": j[3]
                                }

                        }
                }
            response = requests.put(webURL, json=payload, auth=auth_request, headers=headers)
            psd(response=response, d=d, j=j)
        else:
            print("Field type not supported...")


# call to if-else function
def psd(response=None, d=None, j=None):
    if response.status_code != 204:
        print("Error: Unable to Post \"{}\" Data to the Issue to {} with Status: {} and reason {} \n"
              .format(j[3], d["key"], response.status_code, response.reason))
        # print("*" * 90)
    else:
        pass
        # print("Custom field Option \"{}\" Added to Issue {}".format(j[3], d["key"]))
        # print("*" * 90)
        # uncomment if you want to see the post information.


# function for self_rebuild fields
def no_option():
    user = Field()
    v = CreateField()
    k = user.get_field().__getitem__(
        2)
    if k == v.userpicker or \
            k == v.textfield or \
            k == v.url or \
            k == v.datepicker or \
            k == v.datetime or \
            k == v.float or \
            k == v.textarea or \
            k == v.multigrouppicker or \
            k == v.multiuserpicker or \
            k == v.grouppicker or \
            k == v.labels or \
            k == v.project or \
            k == v.multiversion or \
            k == v.version or \
            k == v.readonlyfield or \
            k == v.importid:
        print(f"{field_name} doesn't need options, rebuilding...")
        print(f"Rebuilding not required...OK")
        sys.exit(0)
    elif k == v.multiselect or \
            k == v.multicheckboxes or \
            k == v.select or \
            k == v.radiobuttons or \
            k == v.cascadingselect:
        user.get_field_option(g=user.get_field().__getitem__(3))
    else:
        user.get_field_issue_history()


# running get request for authentication and keep our session active
def make_session(email=None, token=None):
    global auth_request
    global headers
    auth_request = HTTPBasicAuth(email, token)
    headers = {"Content-Type": "application/json"}


# Basic Auth Using python completed within <STDIN>
def jira_basic_auth():
    global email
    global token
    global baseurl
    global pkey
    # TODO: consider using command line argument
    # parser = argparse.ArgumentParser(prog='builder', description='Rebuild custom field', usage='%(prog)s [options]')
    # parser.add_argument('-e', '--email', help='Email of your Atlassian Account')
    # parser.add_argument('-t', '--token', help='API token to your Atlassian Account')
    # parser.add_argument('-l', '--baseurl', help='Instance URL to Jira Cloud')
    # parser.add_argument('-p', '--pkey', help='Project key of your Project')
    # args = parser.parse_args()

    email = input("Enter your Email Address: \n")
    validate(email=email)
    token = input("Enter your API Token: \n")
    validate(token=token)
    baseurl = input("Enter your Instance Full URL (e.g. nexusfive.atlassian.net): \n")
    validate(baseurl=baseurl)
    pkey = input("Enter your Project Key (e.g. for Multiple Projects separate by comma e.g NB, GT ): \n")
    validate(pkey=pkey)
    login(baseurl, email, token)


# authenticate user
def login(baseurl, email, token):
    if email and token is not None:
        make_session(email, token)
        webURL = ("https://{}/rest/api/3/search?jql=project%20in%20({})&startAt=0&maxResults=100"
                  .format(baseurl, pkey))
        data = requests.get(webURL, auth=auth_request, headers=headers)
        if data.status_code == 200:
            print("Login Successful...\n")
            run = IssueHistory()
            run.filter_issue_keys(data)
        else:
            sys.stderr.write("Authentication Failed...\n")
            sys.exit(1)
    else:
        sys.stderr.write("We cannot login with No values...\n")
        sys.exit(1)


# simply validate login details
def validate(email=None, token=None, baseurl=None, pkey=None):
    # p1 = re.compile('[A-Za-z0-9._%+-+@[A-Za-z0-9.-]+.\[A-Za-z]{3,4}')
    if email == "":
        print("Email Address can't be empty")
    elif token == "":
        print("Your token can't be empty")
    elif baseurl == "":
        print("Your Instance Name can't be empty...")
    elif pkey == "":
        print("Your Project key can't be empty.")


# might not be used in this context, we'll leave it here
def repeat(context=None, retries=None, trials=None):
    t = Field()
    while t.get_field() is None:
        input(context)
        # give the viewer 3 chances to add a context before proceeding.
        retries -= 1
        if retries < 0:
            sys.stderr.write("It seems you do not want to add a context on \"{}\" field"
                             .format(field_name))
            sys.exit(1)
        print(trials)


# Posting multi_choice fields
def post_multi(j=None):
    m = str(j[3])
    f = "value"
    c = []
    if m.split(",").__len__() == 1:
        k = [{f: m}]
        return k
    # consider using  m.split("," or " ")
    elif m.split(",").__len__() > 1:
        for u in m.split(","):
            r = {f: u}
            c.append(r)
        return c


# TODO: check the context endpoint
def context_check():
    x = Field()
    webURL = ("https://{}/rest/api/3/field/{}/contexts".
              format(baseurl, x.get_field().__getitem__(3)))
    data = requests.get(webURL, auth=auth_request, headers=headers)
    rest = json.loads(data.content)
    if rest["values"] == "[]":
        return True
    elif str(rest["errors"]):
        return True
    else:
        return False


# function for cascading select list
def post_cassi(j=None):
    m = str(j[3])
    f = str(j[3])
    h = str(j[3])
    if m.__len__() > 0:
        k = f.split(")", maxsplit=5)
        d = h.split(")", maxsplit=5)
        z = k.__getitem__(0).split("(")
        e = d.__getitem__(1).split("(")

        b = z.__getitem__(0).split(":")
        i = e.__getitem__(0).split(":")
        vec = [b, i]
        var = [val for elem in vec for val in elem]
        return var
