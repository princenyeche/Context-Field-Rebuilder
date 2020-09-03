#!/usr/bin/env python
# start up file
"""
Script   : Context Field Rebuilder for Custom field
Author   : Prince Nyeche
Platform : Atlassian Jira Cloud
Version  : 1.0
Function : Script helps to build back deleted custom field context.
**************************************************************************
Required libraries : requests, tqdm
Install via        : requirements.txt file
License            : MIT License Copyright (c) 2020 Prince Nyeche
API Token can be generated from https://id.atlassian.com/manage/api-tokens
**************************************************************************
"""
from cfx.cfrebuilder import __author__, __version__, jira_basic_auth, IssueHistory, \
    field_name

"""
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Supported Custom fields & Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. multiselect - COMPLETE
2. radiobuttons - COMPLETE 
3. select list (single line) - COMPLETE 
4. cascadingselect COMPLETE
5. multicheckboxes - COMPLETE

** Script can search Multiple Projects
** No Limit to Issues per runtime.

__________________________________________________________________________
All Fields Supported :[url, userpicker (single user), select, textfield, labels, 
cascadingselect, datepicker, datetime, float, grouppicker,  multicheckboxes, 
multigrouppicker,  multiselect, multiuserpicker, radiobuttons, textarea]
**************************************************************************
The above fields  are supported with this script 
***********************************************
_______________________________________________

Fields without options which are self rebuilt by JIRA
**************************************************************************
[User Picker (single user), Textfield (single line), multigrouppicker,
Textarea, multiuserpicker, labels, url, float, datepicker, datetime, grouppicker]
**************************************************************************
"""


# main function call
def main():
    a = __version__
    b = __author__
    c = IssueHistory()
    # I don't know why I added it, just for fun
    print(
        "*" * 100 + "\n" +
        "*" * 3 + a.center(94) + "*" * 3 + "\n" +
        "*" * 3 + b.center(94) + "*" * 3 + "\n" +
        "*" * 100)
    jira_basic_auth()
    print("*" * 90)
    print("Let's Post the Option values to Jira Issue Fields \n"
          "If you do not want to proceed, Press Ctrl + C to Terminate at any time")
    print("*" * 90)
    c.sub_filter(q=field_name)


# Main Program Initialization here
if __name__ == "__main__":
    main()
