# AWS-Automation


cross-account-role-audit.py

**About** <br>
_cross-account-role-audit.py_ script helps automate auditing roles for cross account access. The script first assumes a role in the management account (Parent account) to get the list of AWS accounts. After getting the account list it assumes a role in each account one by one and lists out all the roles present in the account along with the policies attached to the role and  trust relationship. The final output is an excel file containig the list of role presnt across various AWS accounts and other details.

**Sample Output** <br>

Account ID  |	Account Name | Role Name | Policy | Trust Relationship
----------- |----------------|-----------|--------|-------------------
*********266|    Dev         |     role1 |[policy1'] | [{'Effect': 'Allow', 'Principal': {'AWS': 'arn:aws:iam::*********371:root'}, 'Action': 'sts:AssumeRole', 'Condition': {}}]
*********371|    Test         |     role2 |['policy2'] | [{'Effect': 'Allow', 'Principal': {'AWS': 'arn:aws:iam::*********257:root'}, 'Action': 'sts:AssumeRole', 'Condition': {}}]
*********468|    QA         |     role3 |['policy3, policy2'] | [{'Effect': 'Allow', 'Principal': {'AWS': 'arn:aws:iam::*********862:root'}, 'Action': 'sts:AssumeRole', 'Condition': {}}]

<br>

**Installation** <br>
Clone the repo and install the following dependencies - boto3, pandas and openpyxl

**Required Configuration** <br>
LIST_ACCOUNTS_X_ROLE = "list-accounts-role" //role in the management account to get accout list with trust relationship to your Infra or some other account <br>
READ_ONLY_X_ROLE = "read-only-role" // read-only role deployed in member accounts (child accounts) with trust relationship to your Infra or some other account<br>
MANAGEMENT_ACCOUNT_ID = "000000000000" // Account number of management account <br>
ROLE_SESSION_NAME = "cross-account-role-audit" //role session name <br>
