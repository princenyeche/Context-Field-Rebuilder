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


# we need to find all the Issues where the customfield existed before
class IssueHistory:
    """
    In order to get the custom-field, we need to know in the changelog
    history that it has existed there before at least at one point in time.

    if we can find it, then we can iterate through all the various issue keys.
    so for now, we store all our issue key to d which we unpack as d["key"]
    then we can call it later since we passed it as position parameter or kwargs
    """
    @staticmethod
    def filter_issue_keys(data):
        global fjson
        fjson = json.loads(data.content)
        print("Filtering Issue Keys, {} Issues returned...".format(str(fjson["total"])))
        field_name = input("Enter the Name of the Custom Field: \n")
        if field_name is not None:
            check = Field()
            check.get_field(field_name)

    def sub_filter(self, v):
        if list(fjson["issues"]) is not None:
            for d in list(fjson["issues"]):
                field_name = v
                print("Reading Issues: {} ".format(d["key"]))
                self.get_field_issue_history(d, field_name)

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
                                # print("Found Field: {}, From: {}, Changed To: {} "
                                #     .format(j["field"], j["fromString"], j["toString"]))
                                self.rebuild_field_options((j["field"], j["fieldId"],
                                                            j["fromString"], j["toString"]), d, field_name=field_name)
                            else:
                                print(f"Unable to find {field_name}")

    def rebuild_field_options(self, j, d, field_name=None):
        """
        :param field_name: contains the name of our custom field
        :param j: stores the value of our fromString and toString we'll need this later
        :param d: stores our issue key, so we can always call this later
        :return: get the options that is not "None", we can post this as a String.
        Below we ensure we extract our cf id and the values in j.
        """
        s = j[1]
        seq3 = s.strip("customfield_")
        # seq = []
        #
        #         for k in str(j[3]):
        #             seq.append(k)
        #             if seq.sort():
        #                 output = open('output.txt', 'a+')
        #                 output.write(k)
        #                 output.close()
        #         for v in str(j[2]):
        #             seq.append(v)
        #             if v == str('None'):
        #                 pass
        #             else:
        #                 output = open('output.txt', 'a+')
        #                 output.write(v)
        #                 output.close()
        if 'None' in str(j[2]) not in str(j[3]) or 'None' in str(j[3]) not in str(j[2]):
            print(str(j[3]) or str(j[2]))
            print(j[1])
            self.sort_options(j, seq3, d, field_name=field_name)

    # we store all the values of j where it's not duplicated
    def sort_options(self, j, seq3, d, field_name=None):
        try:
            # if field_type == field_name:
            self.create_back_cf_options(j, seq3, d=d, field_name=field_name)
            # else:
            # {"errorMessages":["Field customfield_10034 of type Text Field (single line) does not support
            #  options."],"errors":{}}
            # run = Field()
            # run.rebuild_issue_custom_field_value(value, c, field_name=None, d=d)
        except ValueError:
            print("Something went wrong: {}".format(sys.exc_info()[1]))

    # below method is to create back the options for the custom-field, since we can identify it
    @staticmethod
    def create_back_cf_options(j, seq3, d=None, field_name=None):
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
            run.rebuild_issue_custom_field_value(j, c=None, field_name=field_name, d=d)


class Field(IssueHistory):
    """
    `get_field`:
    check if the field exist by looking at the endpoint /rest/api/3/field
    if the field has context, we should search for that instead and see
    if our options exist therein. if it doesn't then we build it back
    """
    def get_field(self, field_name):
        webURL = ("https://" + baseurl + "/rest/api/3/field")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        fjson = json.loads(data.content)
        for c in list(fjson):
            if field_name == c["name"]:
                print("Finding Custom field...")
                print("Found: {}, CustomId: {}".format(c["name"], c["schema"]["customId"]))
                # if options are present do below
                self.get_field_option(c["schema"]["customId"], field_name)
            # elif field_name not in c["name"]:
            # self.create_cf(field_name)
            else:
                # in the event the option doesn't exist do below
                self.sub_filter(v=field_name)

    # wrapping the field options in order to post to issue
    def get_field_option(self, c, field_name):
        webURL = ("https://" + baseurl + "/rest/api/3/customField/" + str(c["schema"]["customId"]) + "/context")
        data = requests.get(webURL, auth=auth_request, headers=headers)
        fjson = json.loads(data.content)
        self.get_field_value(fjson, c, field_name)

    def get_field_value(self, fjson, c, field_name):
        for a in fjson["values"]:
            if a["value"] is not None:
                j = a["value"]
                print(j)
                self.post_field_data(j, c, field_name)

    def post_field_data(self, j, c, field_name, d=None):
        # TODO: to find the type of field_type used use this endpoint
        # https://atlas-connect.atlassian.net/rest/api/3/field/search?type=custom
        # values accepted "custom" or "system"
        return self.rebuild_issue_custom_field_value(j, c=None, field_name=field_name, d=d)

    @staticmethod
    def rebuild_issue_custom_field_value(j, c=None, field_name=None, d=None):
        webURL = ("https://{}/rest/api/3/issue/{}".format(baseurl, d["key"]))
        payload = (
            {
                "update": {
                    field_name:
                        {
                            "set": j[3]
                        }

                }
            }
        )
        response = requests.put(webURL, json=payload, auth=auth_request, headers=headers)
        if response.status_code != 204:
            print("Error: Unable to Post the Data to the Issue...\n", response.status_code, sep="*")
            print("*" * 90)
        else:
            print("Custom field Option Added to {}".format(d["key"]))
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
        webURL = ("https://" + baseurl + "/rest/api/3/search?jql=project%20%3D%20T6")
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
