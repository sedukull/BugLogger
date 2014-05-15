from jira.client import JIRA

URL =  "http://bugs-ccp.citrix.com/"
USER = "santhoshe"
PASSWD =  "asdf!@34"

__jira = JIRA(options={'server': URL},basic_auth=(USER,PASSWD))
__jira.session()
issue = __jira.create_issue(
                            project={"key": "CS"},
                            summary="Testing AutoLogging",
                            issuetype={
                                "name": "Bug"},
                            priority={
                                "name": "Major"},
                            environment="Test",
                            description="Testing Automation Bug Logging",
                            components=[
                                {'id': "Automation"}],
                            assignee={
                                'name': "santhoshe"},
                            reporter={'name': "santhoshe"})

