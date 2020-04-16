from cfrebuilder import __author__, __version__, jira_basic_auth
"""
**************************************************************************
Supported Custom fields
Fields :[Select List , User Picker, Cascading Select list, Labels, Components]
The above fields  are supported with this script 
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
