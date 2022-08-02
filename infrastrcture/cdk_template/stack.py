from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as api_gw,
    aws_apigatewayv2 as api_gw2,
    aws_dynamodb as dynamo_db,
    Stack,
    CfnOutput,
    Fn
)

# Allow only specified IPs to access the API gw
white_listed_ips = ["192.3.32.0/22", "127.0.0.1", "0.0.0.0/32"]   


class CdkTemplateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


##################### Define the DynamoDb tables #####################

        # Table to hold users
        users_table = dynamo_db.Table(self, "UsersTable",
                          partition_key=dynamo_db.Attribute(name="UserID",  type=dynamo_db.AttributeType.NUMBER),
                          sort_key=dynamo_db.Attribute(name="UserName", type=dynamo_db.AttributeType.STRING,
                          read_capacity=2, write_capacity=2)
                      )
        weights_table = dynamo_db.Table(self, "WeightsTable",
                          partition_key=dynamo_db.Attribute(name="UserID",  type=dynamo_db.AttributeType.NUMBER),
                          sort_key=dynamo_db.Attribute(name="UtcDate", type=dynamo_db.AttributeType.NUMBER,
                          read_capacity=2, write_capacity=2)
                      )

##################### Define the Lambda function #####################

        # defines an AWS Lambda resource that is triggered by the API-gw and accesses the DynamoDb tables
        with open("../../lambda_functions/handle_url_lambda.py", encoding="utf8") as fp:
            handler_code = fp.read()
        handle_url_lambda = _lambda.Function(self, "lambdaHandler",
                          code=_lambda.InlineCode(handler_code),
                          runtime=_lambda.Runtime.PYTHON_3_8,    # execution environment
                          handler="index.events_handler",            # file.entry-point=function name 
                          environment=    { 'USERS_TABLE_NAME': users_table.table_name }
                              )
                          #code=_lambda.Code.from_asset("../../lambda_functions"),   # Location of lambda source files
                          #timeout=Duration.seconds(300),

        # grant lambda role read/write permissions to both tables
        users_table.grant_read_write_data(handle_url_lambda)
        weights_table.grant_read_write_data(handle_url_lambda)

##################### Define the API GW and related policies #####################


#       # First stage of the API Gateway REST API IAM policy definition
        api_policy_document = iam.PolicyDocument()

#       # defines an API Gateway REST API resource
        api_policy_document = iam.PolicyDocument()
        api = api_gw.LambdaRestApi(self, 'matchToTheWeight-api',
              handler=handle_url_lambda,
              rest_api_name='matchToTheWeight',
              policy=api_policy_document,
              proxy=False
        )

        # Define the URL paths and related method recognized by the gateway
        mttw = api.root.add_resource("MttW")      # Mandatory start on all URLs of our API. 'Santiy' API key

        users = mttw.add_resource("users")
        users.add_method("GET")                     # Get the list of users
        
        add_user = users.add_resource("{userName}")
        add_user.add_method("POST")                 # Add a new user. 
        
        u = mttw.add_resource("user")
        user = u.add_resource("{userId}")
        weight = user.add_resource("weight")
        set_weight = weight.add_resource("{weight}") 
        set_weight.add_method("POST")               # Set today's weight for the specified user

        status = mttw.add_resource("status") 
        status.add_method("GET")                    # Get status (typically for display) 
        
#       # Second and final stage of the API Gateway REST API IAM policy definition
        api_policy_document.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["execute-api:Invoke"],
                resources=[Fn.join('', ['execute-api:/', '*'])]
            )
        )
        api_policy_document.add_statements(
            iam.PolicyStatement(
                effect=iam.Effect.DENY,
                actions=["execute-api:Invoke"],
                conditions={
                    "NotIpAddress": { "aws:SourceIp": white_listed_ips }
                },
                principals=[iam.AnyPrincipal()],
                resources=[Fn.join('', ['execute-api:/', '*'])]
            )
        )

##################### Define output #####################
        CfnOutput(self, 'restApiUrl', value=api.url);
        CfnOutput(self, 'usersTableName', value=users_table.table_name);
        CfnOutput(self, 'usersTableArn', value=users_table.table_arn);
        CfnOutput(self, 'handleUrlTableName', value=handle_url_lambda.function_name);
