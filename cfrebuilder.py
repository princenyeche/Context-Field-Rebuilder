# This Script helps to rebuild deleted context field
"""
Script   : Context Field Rebuilder for Custom field
Author   : Prince Nyeche
Platform : Atlassian Jira Cloud
Version  : 0.2
**************************************************************************
Required libraries : requests
Download URL       : http://python-requests.org
API Token can be generated from https://id.atlassian.com/manage/api-tokens
**************************************************************************
"""

import json
import requests
from requests.auth import HTTPBasicAuth
import sys

__version__ = '0.2'
__author__ = 'Prince Nyeche'


# we need to find all the Issues where the customfield existed before
class IssueHistory:
    """
    In order to get the custom_field, we need to know in the changelog
    history that it has existed there before at least at one point in time.
    if we can find it, then we can iterate through all the various issue keys.
    so for now, we store all our issue key to d which we unpack as d["key"]
    then we can call it later since we passed it as positional argument or kwargs
    """

    def filter_issue_keys(self, data):
        global jql_data  # saving our JQL search here in a Global variable
        jql_data = json.loads(data.content)
        print("Filtering Issue Keys, {} Issues returned...".format(str(jql_data["total"])))
        field_name = input("Enter the Name of the Custom Field: \n")
        if field_name is not None:
            self.sub_filter(v=field_name)

    def sub_filter(self, v):
        field_name = v
        check = Field()
        if check.get_field(field_name) == field_name:
            a = check.get_field_types(field_name=field_name).__getitem__(1)
            check.get_field_option(field_name=field_name, g=a)
        elif check.get_field(field_name) != field_name:
            context = f"A Context doesn't exist on {field_name}, we'll build it now, please add a context " \
                      "then press 'Enter' \n"
            input(context)
            if list(jql_data["issues"]) is not None:
                for d in list(jql_data["issues"]):
                    print("Reading Issues: {} ".format(d["key"]))
                    self.get_field_issue_history(d, field_name)
        # TODO: later we might add a condition to recreate a field back
        # else:
        # check.post_field_data(field_name=field_name)

    def get_field_issue_history(self, d, field_name):
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
                                self.rebuild_field_options((j["field"], j["fieldId"],
                                                            j["fromString"], j["toString"], j["to"]),
                                                           d=d, field_name=field_name)
                            else:
                                print(f"Unable to find {field_name}")

    def rebuild_field_options(self, j=None, d=None, field_name=None):
        """
        :param field_name: contains the name of our custom field
        :param j: stores the value of our fromString and toString we'll need this later
        but we only want the toString which is j[3]
        :param d: stores our issue key, so we can always call this later
        Below we ensure we extract our cf id and the values in j.
        """
        s = j[1]
        seq3 = s.strip("customfield_")
        if str(j[3]):
            print(str(j[3]))
            self.sort_options(j=j, seq3=seq3, d=d, field_name=field_name)

    # we store all the values of j where it's not duplicated
    def sort_options(self, j=None, seq3=None, d=None, field_name=None):
        try:
            self.create_back_cf_options(j=j, seq3=seq3, d=d, field_name=field_name)
        except ValueError:
            print("Something went wrong: {}".format(sys.exc_info()[1]))

    # below method is to create back the options for the custom-field, since we can identify it
    @staticmethod
    def create_back_cf_options(j=None, seq3=None, d=None, field_name=None):
        print("*" * 90)
        webURL = ("https://{}/rest/api/3/customField/{}/option".format(baseurl, seq3))
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
        if data.status_code != 201:
            print("Error: Unable to Post the Data to the Issue...", data.status_code, sep="*")
        else:
            print("Creating {} field option for {}".format(j[3], j[0]))
            run = Field()
            run.rebuild_issue_custom_field_value(j=j, field_name=field_name, d=d)


class Field(IssueHistory):
    """
    `get_field` and `get_field_type`
    check if the field exist by looking at the endpoint /rest/api/3/field.
    if the field has context it should exist, we should search for that instead and see
    if our options exist therein. if it doesn't then we build it back
    """

    @staticmethod
    def get_field(field_name=None):
        webURL = ("https://" + baseurl + "/rest/api/3/field")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        fjson = json.loads(data.content)
        for c in list(fjson):
            if field_name in c["name"]:
                return c["name"]

    @staticmethod
    # a is already defined, passing any value to it will result in error, we used it to call the return expression
    def get_field_types(field_name=None):
        # TODO: to find the type of field_type used use this endpoint
        #  https://<your-instance>.atlassian.net/rest/api/3/field/search?type=custom
        #  values accepted "custom" or "system"
        webURL = ("https://{}/rest/api/3/field/search?type=custom"
                  .format(baseurl))
        data = requests.get(webURL, auth=auth_request, headers=headers)
        pjson = json.loads(data.content)
        for a in pjson["values"]:
            if a["name"] == field_name:
                return a["schema"]["custom"], a["schema"]["customId"], a["id"]

    # wrapping the field options in order to post to issue
    def get_field_option(self, g=None, field_name=None):
        webURL = ("https://" + baseurl + "/rest/api/3/customField/" + str(g) + "/option")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        pjson = json.loads(data.content)
        self.get_field_value(pjson=pjson, field_name=field_name)

    def get_field_value(self, pjson=None, field_name=None):
        if str(pjson["values"]) == "[]":
            print(f"The Context for {field_name} has no values, defaulting to build options...")
            if list(jql_data["issues"]) is not None:
                for d in list(jql_data["issues"]):
                    print("Reading Issues: {} ".format(d["key"]))
                    self.get_field_issue_history(d=d, field_name=field_name)
        else:
            print(f"{field_name} has values posting to issue...")
            for a in pjson["values"]:
                if a["value"] is not None:
                    pass
            self.post_field_data(field_name=field_name)

    def post_field_data(self, field_name=None):
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
                                        check = Field()
                                        if check.get_field_types(
                                                field_name) == "com.atlassian.jira.plugin.system.customfieldtypes" \
                                                               ":userpicker":
                                            self.rebuild_issue_custom_field_value((j["field"], j["fieldId"],
                                                                                   j["fromString"], j["toString"],
                                                                                   j["to"]),
                                                                                  field_name=field_name, d=d)
                                        else:
                                            self.rebuild_issue_custom_field_values((j["field"], j["fieldId"],
                                                                                    j["fromString"], j["toString"]),
                                                                                   field_name=field_name, d=d)

    @staticmethod
    def rebuild_issue_custom_field_value(j=None, field_name=None, d=None):
        webURL = ("https://{}/rest/api/3/issue/{}".format(baseurl, d["key"]))
        payload = (
            {
                "update": {
                    field_name:
                        {
                            "set": j[4]
                        }

                }
            }
        )
        response = requests.put(webURL, json=payload, auth=auth_request, headers=headers)
        if response.status_code != 204:
            print("Error: Unable to Post the Data to the Issue to {} with Status: {} \n"
                  .format(d["key"], response.status_code))
            print("*" * 90)
        else:
            print("Custom field Option Added to Issue {}".format(d["key"]))
            print("*" * 90)

    @staticmethod
    def rebuild_issue_custom_field_values(j=None, field_name=None, d=None):
        webURL = ("https://{}/rest/api/3/issue/{}".format(baseurl, d["key"]))
        check = Field()
        b = check.get_field_types(field_name=field_name)
        payload = \
            {
                "fields":
                    {
                        b.__getitem__(2):
                            {
                               "value": j[3]
                            }

                    }
            }
        response = requests.put(webURL, json=payload, auth=auth_request, headers=headers)
        if response.status_code != 204:
            print("Error: Unable to Post the Data to the Issue to {} with Status: {} \n"
                  .format(d["key"], response.status_code))
            print("*" * 90)
        else:
            print("Custom field Option Added to Issue {}".format(d["key"]))
            print("*" * 90)

    # bulk create custom fields
    @staticmethod
    def create_cf(field_name):
        field_type = []
        field_type_selected = ['com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:datepicker, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:datetime, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:float, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:grouppicker, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:importid, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:labels, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:multigrouppicker, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:multiselect, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:multiversion, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:project, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:select, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:textarea, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:textfield, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:url, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:userpicker, '
                               'com.atlassian.jira.plugin.system.customfieldtypes:version']
        field_search_key = []
        field_search_key_selected = ['com.atlassian.jira.plugin.system.customfieldtypes:cascadingselectsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:daterange, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:datetimerange, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:exactnumber, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:grouppickersearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:labelsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:numberrange, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:projectsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:textsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher, '
                                     'com.atlassian.jira.plugin.system.customfieldtypes:versionsearcher']

        print("These are the accepted values of field type \n {}".format(field_type_selected))
        select_fk = input("Enter the field type:  \n")
        if select_fk in field_type_selected:
            field_type.append(select_fk)
        print("These are the accepted values of Search key \n {}".format(field_search_key_selected))
        select_sk = input("Enter the Search type: \n")
        if select_sk in field_search_key_selected:
            field_search_key.append(select_sk)
        webURL = ("https://{}/rest/api/3/field".format(baseurl))
        payload = (
            {
                "searcherKey": field_search_key,
                "name": field_name,
                "description": "Custom field - you can always change later",
                "type": field_type
            }
        )
        response = requests.post(webURL, json=payload, auth=auth_request, headers=headers)
        if response.status_code != 201:
            print('Error: Unable to Create Custom Field...\n', response.status_code, sep="*")
            print("*" * 90)
        else:
            print("Custom field {} created...".format(field_name))
            print("*" * 90)


# running get request for authentication and request
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
    email = input("Enter your Email Address: \n")
    validate(email=email)
    token = input("Enter your API Token: \n")
    validate(token=token)
    baseurl = input("Enter your Instance Full URL: \n")
    validate(baseurl=baseurl)
    login(baseurl, email, token)


# authenticate user
def login(baseurl, email, token):
    if email and token is not None:
        make_session(email, token)
        webURL = ("https://" + baseurl + "/rest/api/3/search?jql=project%20in%20(T6,T5)&startAt=0&maxResults=1000")
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
