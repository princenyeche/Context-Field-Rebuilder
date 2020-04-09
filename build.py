from cfrebuilder import IssueHistory, Field, make_session, login


def write():
    getfield = Field()
    data = input("Enter the name")
    if data is not None:
        getfield.filter_issue_keys(data)


@login()
def find():
    v = 'Name'
    check = IssueHistory()
    check.sub_filter(v)
