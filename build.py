#!/usr/bin/env python
# start up file
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
from cfrebuilder import __author__, __version__, jira_basic_auth
"""
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Supported Custom fields & Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. multiselect - W -OP
2. radiobuttons - COMPLETE 
3. select list (single line) - COMPLETE 
4. labels
5. cascadingselect list
6. multicheckboxes - W -OP

** Script can search Multiple Projects
** Limited to 1K Issues
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
Textarea, multiuserpicker, url, float, datepicker, datetime, grouppicker]
**************************************************************************
"""


# main function call
def main():
    a = __version__
    b = __author__
    print(
        "*" * 100 + "\n" +
        "*" * 3 + a.center(94) + "*" * 3 + "\n" +
        "*" * 3 + b.center(94) + "*" * 3 + "\n" +
        "*" * 100)
    jira_basic_auth()


# Main Program Initialization here
if __name__ == "__main__":
    main()
