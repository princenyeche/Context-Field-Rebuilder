# Context Field Rebuilder
The below script is written in python and helps to rebuild deleted context options of custom fields and insert the correct values back to the Issue Key on Jira Cloud

## Supported Fields
* Multiselect 
* Radiobuttons  
* Select list (single line)  
* Cascading Select list 
* Multicheckboxes  

## What this Script does:
* It can be able to create back a custom field option → How this is done, is a loop through the entire issue key, if an option exist, it will be created
* It rebuilds back the option values on each Jira Issue, by checking the changelog history, identifying the right field and updating the issue with the field value
* If you have deleted the field, this script can also be used to create the custom field
* If you already know the options and have added it as a default value in the custom field context, the field is able to skip rebuilding the options and simply post back the correct value

# Read Me
Make sure Python is installed! Goto https://www.python.org/downloads/ any version from v3.x will do. You will also need to ensure you have PIP on your computer with the download. check by using `$: pip --version`

If you installed Python from source, with an installer from python.org, or via Homebrew you should already have pip. If you’re on Linux and installed using your OS package manager, you may have to install pip separately.

> Required Package → Requests can be gotten from http://python-requests.org
> You can also install a virtual environment to run commands as well. you can install as `$: pip install virtualenv` on  terminal (for MacOs users → use this guide on Pipenv ).To activate the virtual environment, use `$: source <location where venv is>/bin/activate` 

In order to download, Requests run your PIP by using `$: pip install requests` or `$: sudo pip install requests` if on linux.

Ensure you have the right permission on the Project before running the Script such as **BROWSE**, **CREATE** , **EDIT ISSUES Permission** & also Access to Jira Settings.

Get an API Token from here https://id.atlassian.com/manage/api-tokens if you haven’t.


# How to Use
* Go to your Terminal
* Run the script by using `$: python3 build.py` or `$: python build.py` if your machine is already on python 3.
* Just enter the project key, you would like rebuild. Please enter a valid Project key. example `NB` For multiple projects, please separate by comma. e.g `NB, NGT, TIS`.
