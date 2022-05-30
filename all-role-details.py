import logging
import boto3
from botocore.exceptions import ClientError
import pandas

MANAGEMENT_ORG_ROLE = "list-accounts-role"
READ_ONLY_ROLE = "read-only-role"
MANAGEMENT_ACCOUNT_ID = "000000000000"
ROLE_SESSION_NAME = "all-iam-roles"

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_role_arn(account_id, role_name):
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    return role_arn


def get_client(role_arn, service_name):
    sts_client = boto3.client("sts")
    response = sts_client.assume_role(
        RoleArn=role_arn, RoleSessionName=ROLE_SESSION_NAME
    )
    temp_creds = response["Credentials"]

    client = boto3.client(
        service_name,
        aws_access_key_id=temp_creds["AccessKeyId"],
        aws_secret_access_key=temp_creds["SecretAccessKey"],
        aws_session_token=temp_creds["SessionToken"],
    )
    return client


def get_resource(role_arn, service_name):
    client = boto3.client("sts")
    response = client.assume_role(RoleArn=role_arn, RoleSessionName=ROLE_SESSION_NAME)
    temp_creds = response["Credentials"]

    resource = boto3.resource(
        service_name,
        aws_access_key_id=temp_creds["AccessKeyId"],
        aws_secret_access_key=temp_creds["SecretAccessKey"],
        aws_session_token=temp_creds["SessionToken"],
    )
    return resource


def get_aws_accounts(organizations):
    accounts_list = []
    paginator = organizations.get_paginator("list_accounts")
    pages = paginator.paginate()

    for page in pages:
        for account in page["Accounts"]:
            accounts_list.append({"name": account["Name"], "id": account["Id"]})

    return accounts_list


def get_roles_list(iam):
    roles_list = []
    for role in iam.roles.all():
        roles_list.append(role)
    return roles_list


def get_role_details(role):
    role_details = {}
    role_details["name"] = role.name
    role_details["trust_relationship"] = role.assume_role_policy_document["Statement"]

    policy_names = []
    attached_policies = role.attached_policies.all()
    for policy in attached_policies:
        policy_names.append(policy.policy_name)

    role_details["policy_names"] = policy_names
    return role_details


def get_data_frame():
    table = []
    columns = [
        "Account ID",
        "Account Name",
        "Role Name",
        "Policy Name",
        "Trust Relationship",
    ]
    data_frame = pandas.DataFrame(table, columns=columns)
    return data_frame


def create_table(data_frame, role_details, account_id, account_name):
    data_frame = pandas.concat(
        [
            data_frame,
            pandas.DataFrame.from_records(
                [
                    {
                        "Account ID": account_id,
                        "Account Name": account_name,
                        "Role Name": role_details["name"],
                        "Policy Name": role_details["policy_names"],
                        "Trust Relationship": role_details["trust_relationship"],
                    }
                ]
            ),
        ]
    )
    return data_frame


def write_to_excel(table):
    file_name = "all-role-details.xlsx"
    table.to_excel(file_name)


def main():
    try:
        role_arn = get_role_arn(MANAGEMENT_ACCOUNT_ID, MANAGEMENT_ORG_ROLE)
        client = get_client(role_arn, "organizations")
        accounts_list = get_aws_accounts(client)
        data_frame = get_data_frame()

        for account in accounts_list:
            role_arn = get_role_arn(account["id"], READ_ONLY_ROLE)
            try:
                resource = get_resource(role_arn, "iam")
                roles_list = get_roles_list(resource)
                for role in roles_list:
                    role_details = get_role_details(role)
                    data_frame = create_table(
                        data_frame, role_details, account["id"], account["name"]
                    )
            except ClientError as error:
                logger.error(f"Failed to assume role: {role_arn} " + str(error))
        write_to_excel(data_frame)

    except Exception as exception:
        logger.error("****** An error occured ****** \n" + str(exception))
        quit()


if __name__ == "__main__":
    main()
