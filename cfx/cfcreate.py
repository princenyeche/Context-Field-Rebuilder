#!/usr/bin/env python
# create field module
"""
Script   : Context Field Rebuilder for Custom field
Author   : Prince Nyeche
Platform : Atlassian Jira Cloud
Version  : 0.4
Function : Script helps to build back deleted custom field context.
**************************************************************************
Required libraries : requests, tqdm
Install via        : requirements.txt file
License            : MIT License Copyright (c) 2020 Prince Nyeche
API Token can be generated from https://id.atlassian.com/manage/api-tokens
**************************************************************************
"""
import requests
import sys
"""
Usage (field_type) <left> : <right>(searcher_key)
_______________________________________________
* cascadingselect: cascadingselectsearcher
* datepicker: daterange
* datetime: datetimerange
* float: exactnumber or numberrange
* grouppicker: grouppickersearcher
* importid: exactnumber or numberrange
* labels: labelsearcher
* multicheckboxes: multiselectsearcher
* multigrouppicker: multiselectsearcher
* multiselect: multiselectsearcher
* multiuserpicker: userpickergroupsearcher
* multiversion: versionsearcher
* project: projectsearcher
* radiobuttons: multiselectsearcher
* readonlyfield: textsearcher
* select: multiselectsearcher
* textarea: textsearcher
* textfield: textsearcher
* url: exacttextsearcher
* userpicker: userpickergroupsearcher
* version: versionsearcher
_______________________________________________
"""


class CreateField:
    """
    *****************************************
             field type listing
    *****************************************
     """
    cascadingselect = "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect"
    datepicker = "com.atlassian.jira.plugin.system.customfieldtypes:datepicker"
    datetime = "com.atlassian.jira.plugin.system.customfieldtypes:datetime"
    float = "com.atlassian.jira.plugin.system.customfieldtypes:float"
    grouppicker = "com.atlassian.jira.plugin.system.customfieldtypes:grouppicker"
    importid = "com.atlassian.jira.plugin.system.customfieldtypes:importid"
    labels = "com.atlassian.jira.plugin.system.customfieldtypes:labels"
    multicheckboxes = "com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes"
    multigrouppicker = "com.atlassian.jira.plugin.system.customfieldtypes:multigrouppicker"
    multiselect = "com.atlassian.jira.plugin.system.customfieldtypes:multiselect"
    multiuserpicker = "com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker"
    multiversion = "com.atlassian.jira.plugin.system.customfieldtypes:multiversion"
    project = "com.atlassian.jira.plugin.system.customfieldtypes:project"
    radiobuttons = "com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons"
    readonlyfield = "com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield"
    select = "com.atlassian.jira.plugin.system.customfieldtypes:select"
    textarea = "com.atlassian.jira.plugin.system.customfieldtypes:textarea"
    textfield = "com.atlassian.jira.plugin.system.customfieldtypes:textfield"
    url = "com.atlassian.jira.plugin.system.customfieldtypes:url"
    userpicker = "com.atlassian.jira.plugin.system.customfieldtypes:userpicker"
    version = "com.atlassian.jira.plugin.system.customfieldtypes:version"

    """
    *****************************************
            field search key listing
    *****************************************
    """
    cascadingselectsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselectsearcher"
    daterange = "com.atlassian.jira.plugin.system.customfieldtypes:daterange"
    datetimerange = "com.atlassian.jira.plugin.system.customfieldtypes:datetimerange"
    exactnumber = "com.atlassian.jira.plugin.system.customfieldtypes:exactnumber"
    exacttextsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher"
    grouppickersearcher = "com.atlassian.jira.plugin.system.customfieldtypes:grouppickersearcher"
    labelsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:labelsearcher"
    multiselectsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher"
    numberrange = "com.atlassian.jira.plugin.system.customfieldtypes:numberrange"
    projectsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:projectsearcher"
    textsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher"
    userpickergroupsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher"
    versionsearcher = "com.atlassian.jira.plugin.system.customfieldtypes:versionsearcher"

    def __init__(self):
        self.field_type_selected = ["url", "userpicker", "select", "textfield", "labels", "cascadingselect",
                                    "datepicker", "datetime", "float", "grouppicker", "importid",
                                    "multicheckboxes", "multigrouppicker", "multiselect", "multiuserpicker",
                                    "radiobuttons", "textarea"]
        self.field_search_key_selected = ["textsearcher", "numberrange", "labelsearcher", "multiselectsearcher",
                                          "cascadingselectsearcher", "daterange", "datetimerange", "exactnumber",
                                          "exacttextsearcher", "userpickergroupsearcher", "projectsearcher",
                                          "versionsearcher"]
        self.field_type = None
        self.field_search_key = None

    # create custom field, if it is not created.
    def create_cf(self, field_name=None, baseurl=None, auth_request=None, headers=None):
        select_f = "com.atlassian.jira.plugin.system.customfieldtypes:"
        print("These are the accepted values of field type:  {} \n".format(self.field_type_selected))
        select_fk = input("Enter the field type:  \n")
        if select_fk in self.field_type_selected:
            self.field_type = "{}{}".format(select_f, select_fk)
        else:
            print(f"Field type \"{select_fk}\" not in list")
        print("These are the accepted values of Search key: {} \n".format(self.field_search_key_selected))
        select_sk = input("Enter the Search type: \n")
        if select_sk in self.field_search_key_selected:
            self.field_search_key = "{}{}".format(select_f, select_sk)
        else:
            print(f"Field Searcher \"{select_sk}\" not in list")
        webURL = ("https://{}/rest/api/3/field".format(baseurl))
        payload = (
            {
                "searcherKey": self.field_search_key,
                "name": field_name,
                "description": "Custom field created through cfrebuilder - you can always change this later",
                "type": self.field_type

            }
        )
        response = requests.post(webURL, json=payload, auth=auth_request, headers=headers)
        if response.status_code != 201:
            print("Error: Unable to Create \"{}\" Custom Field...{}".format(field_name, response.status_code))
            print("*" * 90)
            sys.exit(1)
        else:
            print("Custom field \"{}\" created...".format(field_name))
            print("*" * 90)
            sys.exit(0)
