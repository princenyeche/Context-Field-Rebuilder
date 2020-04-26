#!/usr/bin/env python
# This Script helps to rebuild deleted context field
"""
Script   : Context Field Rebuilder for Custom field
Author   : Prince Nyeche
Platform : Atlassian Jira Cloud
Version  : 0.2
**************************************************************************
Required libraries : requests
Download URL       : http://python-requests.org
License            : MIT License Copyright (c) 2020 Prince Nyeche
API Token can be generated from https://id.atlassian.com/manage/api-tokens
**************************************************************************
"""

import json
import requests
from requests.auth import HTTPBasicAuth
import sys
from cfcreate import CreateField

__version__ = '0.2'
__author__ = 'Prince Nyeche'
email = None
token = None
baseurl = ""
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
        print("Filtering Issue Keys, {} Issues returned...".format(str(jql_data["total"])))
        field_name = input("Enter the Name of the Custom Field: \n")
        # TODO: to properly find a way to validate all fields on the instance.
        context = f"Make sure a context for \"{field_name}\" exist, by checking it " \
                  f"via the UI https://{baseurl}/secure/admin/ViewCustomFields.jspa " \
                  f"and Add a context, then press 'Enter' to continue.\n"
        input(context)
        a = x.get_field()
        if a is not None:
            self.sub_filter(q=field_name)
        elif a is None:
            print(f"\"{field_name}\" seems like it doesn't exist, do you want to Create it? Please check in the"
                  f" UI before proceeding. if unsure!?")
            i.create_cf(field_name=field_name, baseurl=baseurl, auth_request=auth_request, headers=headers)

    @staticmethod
    def sub_filter(q, retries=3, trials="Try Again!"):
        field_name = q
        x = Field()
        if x.get_field().__getitem__(0) == field_name:
            # a = check.get_field_types(field_name=field_name).__getitem__(0)
            a = x.get_field().__getitem__(3)
            x.get_field_option(g=a)
        elif x.get_field().__getitem__(0) != field_name:
            context = f"A Context doesn't exist on {field_name}, we'll build it now, please add a context via the UI" \
                      " then press 'Enter' \n"
            repeat(context=context, retries=retries, trials=trials)
            # TODO: Certain field types doesn't support customField option endpoint. check `build.py`
            #  for a list of fields. so no need to rebuild that, let's only check if it has context
            no_option()
        # end of if block

    # Issue History search, it finds out the values in the change log then extract and transform it.
    def get_field_issue_history(self):
        if list(jql_data["issues"]) is not None:
            for d in list(jql_data["issues"]):
                print("Matching, Issue key " + d["key"] + " to URL...")
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
                                                                     j["fromString"], j["toString"], j["to"]),
                                                                    d=d)
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
        print("*" * 90)
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
            # TODO: Ability to post to options, both fields needs to be split into a tuple
            p = post_cassi(j=j)
            print("Hello cf cassi")
            payload = (
                {
                    "options": [
                        {
                            "value": p.__getitem__(0),
                            "cascadingOptions": [
                                p.__getitem__(1)
                            ]
                        }

                    ]

                }
            )
            data = requests.post(webURL, auth=auth_request, json=payload, headers=headers)
            csd(data=data, j=j, d=d, field_name=field_name)
        else:
            print("Hello cf normal")
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
        print("Error: Unable to Post the Data to the Issue...".format(data.status_code))
    else:
        print("Creating {} field option for {}".format(j[3], j[0]))
        # end or exit post request


# sub_class to IssueHistory
class Field(IssueHistory):
    """
    `get_field` and `get_field_type`
    check if the field exist by looking at the endpoint /rest/api/3/field.
    if the field has context it should exist, we should search for that instead and see
    if our options exist therein. if it doesn't then we build it back
    """

    @staticmethod
    # c is returned as a tuple, we can use methods in tuple to fetch the required value
    # e.g. __getitem__() method which accepts int value for index beginning at 0.
    def get_field():
        webURL = ("https://" + baseurl + "/rest/api/3/field")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        fjson = json.loads(data.content)
        for c in list(fjson):
            if field_name in c["name"]:
                if c["schema"] is not None:
                    return c["name"], c["id"], c["schema"]["custom"], c["schema"]["customId"]

    @staticmethod
    # a is returned as a tuple, we think this method is unreliable, change it to extend the function.
    def get_field_types():
        # TODO: to find the type of field_type used, use this endpoint
        #  https://<your-instance>.atlassian.net/rest/api/3/field/search?type=custom
        #  values accepted "custom". not reliable, since the default page returned is only 50.
        webURL = ("https://{}/rest/api/3/field/search?type=custom"
                  .format(baseurl))
        data = requests.get(webURL, auth=auth_request, headers=headers)
        pjson = json.loads(data.content)
        for a in pjson["values"]:
            if a["name"] == field_name:
                return a["schema"]["custom"], a["schema"]["customId"], a["id"], a["name"]

    # wrapping the field options in order to post the issue
    def get_field_option(self, g=None):
        global cm_dat
        v = CreateField()
        user = Field()
        webURL = ("https://" + baseurl + "/rest/api/3/customField/" + str(g) + "/option")
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
                k == v.labels:
            print(f"{field_name} doesn't need options, this field self rebuilds")
            print(f"Rebuilding not required...OK")
            sys.exit(0)
        else:
            self.get_field_value(cm_dat=cm_dat)

    def get_field_value(self, cm_dat=None):
        if str(cm_dat["values"]) == "[]":
            print(f"The Context for {field_name} has no values, defaulting to build options...")
            self.get_field_issue_history()
        else:
            print(f"{field_name} has values posting to issue...")
            for a in cm_dat["values"]:
                if a["value"] is not None:
                    pass
            self.post_field_data()

    @staticmethod
    # TODO: check if values has been posted before
    def return_op_value(i=None):
        if str(cm_dat["values"]) == "[]":
            return i
        else:
            for i in cm_dat["values"]:
                pass
            return i

    @staticmethod  # method for getting multi_choices values
    # TODO: get this field value as a list then post it back.
    def fix_multi(j=None):
        m = str(j[3]).split(",")
        if m.__len__() > 0:
            return m

    # if values exist, let's just post it instead.
    def post_field_data(self):
        if list(jql_data["issues"]) is not None:
            for d in list(jql_data["issues"]):
                print("Matching, Issue key " + d["key"] + " to URL...")
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

        sys.exit(0)

    # base method for creating back custom field values
    def rebuild_issue_custom_field_values(self, j=None, d=None):
        v = CreateField()
        webURL = ("https://{}/rest/api/3/issue/{}".format(baseurl, d["key"]))
        b = self.get_field()
        # if the value of the field is 'None' (empty) we would like to post that as well.
        if j[3] == "":
            # we're now able to Post "None" data, works for single / cascading select list
            print("Hello select")
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
            else:
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
        # TODO: Be able to post values for multiple choice fields (Multi_checkboxes, Multi_select)
        elif b.__getitem__(
                2) == v.multiselect or \
                b.__getitem__(2) == v.multicheckboxes:
            # TODO: post method multi choice fields
            print("hello multi")
            payload = \
                {
                    "fields":
                        {
                            b.__getitem__(1):
                            #  we need to be able to iterate through the field options and post it
                                post_multi(j=j)

                        }
                }
            response = requests.put(webURL, auth=auth_request, json=payload, headers=headers)
            psd(response=response, d=d, j=j)
        # TODO: below is used to post to cascading select field, we think the transmutation should work
        elif b.__getitem__(
                2) == v.cascadingselect:
            p = post_cassi(j=j)
            payload = \
                {
                    "fields":
                        {
                            b.__getitem__(1):
                                {
                                    "value": p.__getitem__(0),
                                    "child": {
                                        "value": p.__getitem__(1)
                                    }
                                }

                        }
                }
            response = requests.put(webURL, auth=auth_request, json=payload, headers=headers)
            psd(response=response, d=d, j=j)
        # Posting single values for normal fields
        else:
            print("hello single")
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


# call to if-else function
def psd(response=None, d=None, j=None):
    if response.status_code != 204:
        print("Error: Unable to Post {} Data to the Issue to {} with Status: {} \n"
              .format(j[3], d["key"], response.status_code))
        print("*" * 90)
    else:
        print("Custom field Option {} Added to Issue {}".format(j[3], d["key"]))
        print("*" * 90)


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
            k == v.labels:
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
    # TODO: consider using command line argument
    # parser = argparse.ArgumentParser(prog='builder', description='Rebuild custom field', usage='%(prog)s [options]')
    # parser.add_argument('-e', '--email', help='Email of your Atlassian Account')
    # parser.add_argument('-t', '--token', help='API token to your Atlassian Account')
    # parser.add_argument('-l', '--baseurl', help='Instance URL to Jira Cloud')
    # parser.add_argument('-j', '--jql', help='JQL of your Search')
    # args = parser.parse_args()

    email = input("Enter your Email Address: \n")
    validate(email=email)
    token = input("Enter your API Token: \n")
    validate(token=token)
    baseurl = input("Enter your Instance Full URL (e.g. nexusfive.atlassian.net): \n")
    validate(baseurl=baseurl)
    login(baseurl, email, token)


# authenticate user
def login(baseurl, email, token):
    if email and token is not None:
        make_session(email, token)
        webURL = ("https://" + baseurl + "/rest/api/3/search?jql=project%20in%20(T6)&startAt=0&maxResults=1000")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        if data.status_code == 200:
            print("Login Successful...\n")
            run = IssueHistory()
            run.filter_issue_keys(data)
        else:
            sys.stderr.write("Authentication Failed...\n")
            sys.exit(1)


# simply validate login details
def validate(email=None, token=None, baseurl=None):
    # p1 = re.compile('[A-Za-z0-9._%+-+@[A-Za-z0-9.-]+.\[A-Za-z]{3,4}')
    if email == "":
        print("Email Address can't be empty")
    elif token == "":
        print("Your token can't be empty")
    elif baseurl == "":
        print("Your Instance Name can't be empty...")


def repeat(context=None, retries=None, trials=None):
    check = Field()
    while check.get_field().__getitem__(0) != field_name:
        input(context)
        # give the viewer 2 chances to add a context before proceeding.
        retries -= 1
        if retries < 0:
            sys.stderr.write("It seems you do not want to add a context on \"{}\" field"
                             .format(field_name))
        print(trials)


# Posting multi_choice fields
def post_multi(j=None):
    # TODO: post function multi choice fields
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


def context_check():
    # TODO: check the context endpoint
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
        return b.pop(0), i.pop(0)
