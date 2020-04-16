import requests


class CreateField:

    def __init__(self):
        self.field_type_selected = None
        self.field_search_key_selected = None
        self.field_type = []
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
        self.field_search_key = []
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

    # bulk create custom fields
    def create_cf(self, field_name=None, baseurl=None, auth_request=None, headers=None):
        print("These are the accepted values of field type \n {}".format(self.field_type_selected))
        select_fk = input("Enter the field type:  \n")
        if select_fk in self.field_type_selected:
            self.field_type.append(select_fk)
        print("These are the accepted values of Search key \n {}".format(self.field_search_key_selected))
        select_sk = input("Enter the Search type: \n")
        if select_sk in self.field_search_key_selected:
            self.field_search_key.append(select_sk)
        webURL = ("https://{}/rest/api/3/field".format(baseurl))
        payload = (
            {
                "searcherKey": self.field_search_key,
                "name": field_name,
                "description": "Custom field - you can always change later",
                "type": self.field_type
            }
        )
        response = requests.post(webURL, json=payload, auth=auth_request, headers=headers)
        if response.status_code != 201:
            print("Error: Unable to Create Custom Field...{}".format(response.status_code))
            print("*" * 90)
        else:
            print("Custom field {} created...".format(field_name))
            print("*" * 90)
