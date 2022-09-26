import os
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
# Current values allow all IP-v4 addresses - replace with real IPs/ranges for real use
white_listed_ips = ["0.0.0.0/1","128.0.0.0/1" ]   


class CdkTemplateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        use_localstack = False
        if "USE_LOCALSTACK" in os.environ.keys():
            if os.environ["USE_LOCALSTACK"].lower()=="true":
                use_localstack = True

        ##################### Define the DynamoDb tables #####################

        # Table to hold users
        users_table = dynamo_db.Table(self, "UsersTable",
                          partition_key=dynamo_db.Attribute(name="UserID",  type=dynamo_db.AttributeType.NUMBER),
                          read_capacity=2, write_capacity=2
                      )
        # Table to hold the daily weight of each user
        weights_table = dynamo_db.Table(self, "WeightsTable",
                          partition_key=dynamo_db.Attribute(name="UtcDate",  type=dynamo_db.AttributeType.STRING),
                          sort_key=dynamo_db.Attribute(name="UserID", type=dynamo_db.AttributeType.NUMBER),
                          read_capacity=7, write_capacity=7
                      )


        ##################### Define the Lambda functions #####################

        # Additional Lambdas should be added to the list below
        list_of_lambda_file_names = ["handle_url_lambda"]


        # lambdas holds all the instances of the defined Lamndas
        lambdas = {}

        # Intially we will load dummy code, to prevent dependencies=related failueres
        # Later in the create-stack script we will load the full/real code as zip
        dummy_code = ''' \
def events_handler(events, context):
    msg = 'ERROR: dummy code for Lambda "NAME" - please run "update_lambdas"'
    print(msg)
    return { 'statusCode': 400, 'message': msg }
'''

        env= { 'usersTableName': users_table.table_name,
               'weightsTableName': weights_table.table_name,
               'USE_LOCALSTACK': f'{use_localstack}'
             }

        for name in list_of_lambda_file_names:
            lambdas[name] = _lambda.Function(self, name,
                  code=_lambda.InlineCode(dummy_code.replace("NAME", name)),
                  runtime=_lambda.Runtime.PYTHON_3_8,       # execution environment
                  handler="index.events_handler",           # file.entry-point=function name 
                  environment=env,
                  #timeout=Duration.seconds(30),
            )

 # grant lambda role read/write permissions to both tables
        users_table.grant_read_write_data(lambdas["handle_url_lambda"])
        weights_table.grant_read_write_data(lambdas["handle_url_lambda"])


        ##################### Define the API GW and related policies #####################

#       # First stage of the API Gateway REST API IAM policy definition
        api_policy_document = iam.PolicyDocument()

#       # defines an API Gateway REST API resource
        api_policy_document = iam.PolicyDocument()
        api = api_gw.LambdaRestApi(self, 'matchToTheWeight-api',
              handler=lambdas["handle_url_lambda"],
              rest_api_name='matchToTheWeight',
              policy=api_policy_document,
              proxy=False
        )

        # Define the URL paths and related method recognized by the gateway
        # See the script 'test' for example of the API calls defined below
        mttw = api.root.add_resource("MttW")      # Mandatory start on all URLs of our API. 'Santiy' API key

        users = mttw.add_resource("users")
        users.add_method("GET")                     # Get the list of users
        
        #add_user = users.add_resource("{userName}")
        #add_user.add_method("POST")                 # Add a new user. 
        
        u = mttw.add_resource("user")
        user = u.add_resource("{userID}")
        weight = user.add_resource("weight")
        set_weight = weight.add_resource("{weight}") 
        set_weight.add_method("POST")               # Set today's weight 
                                                    # for the specified user

        status = mttw.add_resource("fullStats") 
        status.add_method("GET")                    # Get all stats

        status = mttw.add_resource("threeDaysStats") 
        status.add_method("GET")                    # Get all stats

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

        ##################### Define outputs #####################

        CfnOutput(self, 'restApiUrl', value=api.url)
        CfnOutput(self, 'restApiId', value=api.rest_api_id)
        CfnOutput(self, 'usersTableName', value=users_table.table_name)
        CfnOutput(self, 'weightsTableName', value=weights_table.table_name)
        for file_name in list_of_lambda_file_names:
            function_name = lambdas[file_name].function_name
            # Example: converts aaa_bbb_ccc to aaaBbbCccFunctionName
            env_var_name = "".join([ w.capitalize() for w in file_name.split("_") ])
            env_var_name = env_var_name[0].lower() + env_var_name[1:] +"FunctionName"
            CfnOutput(self, env_var_name, value=function_name)
           
