import boto3, os 
from datetime import datetime, date, timedelta

def to_dt(date):
    return datetime.strptime(date,"%Y-%m-%d")
def to_str(date):
    return datetime.strftime(date,"%Y-%m-%d")

class Aws(object):
    def __init__(self):
    
        self.use_localstack = False
        if "USE_LOCALSTACK" in os.environ.keys():
            if os.environ["USE_LOCALSTACK"].lower()=="true":
                self.use_localstack = True
        kwargs = {}
        if self.use_localstack:
            kwargs["endpoint_url"] = "http://localhost:4566"
        self.dynamodb_resource = boto3.resource('dynamodb', **kwargs)
        self.dynamodb_client = boto3.client('dynamodb', **kwargs)
        self.table_name = {}
        for table in ["users", "weights"]:
            self.table_name[table] = os.environ[table+"TableName"]
        self.users_table = self._get_users_table()
        self.user_ids = list(self.users_table.keys())
        self.epoch = None



    ######## Database related functions ##########    
    def _get_table_data(self, table):
        data = []
        table_name = self.table_name[table]
        t = self.dynamodb_resource.Table(table_name)
        response = t.scan()
        data.extend(response.get('Items', []))
        return data
    def _put_table_item(self, table, item):
        print(f'    _put_table_item: writting item {item} to table {table}')
        table_name = self.table_name[table]
        table = self.dynamodb_resource.Table(table_name)
        res = table.put_item(Item=item)
        return res

        print(f'    _put_table_item: writting item {item} to table {table}')
        table_name = self.table_name[table]
        res = self.dynamodb_client.put_item(TableName=table_name, Item=item)
        return res
    def is_ok_to_include_date(self, date, limit_data_to_last_3_days):
        if not limit_data_to_last_3_days:
            return True
        today = datetime.utcnow().date()
        return (today-datetime.fromisoformat(date).date())<timedelta(days=3)
    def _get_weights_table(self, limit_data_to_last_3_days=False):
        weights_raw = self._get_table_data("weights")
        weights = {}
        for wr in weights_raw:
            date =  str(wr["UtcDate"])
            user = str(wr["UserID"])
            weight = str(wr["Weight"])
            if self.is_ok_to_include_date(date, limit_data_to_last_3_days):
                if not date in weights.keys():
                    weights[date] = {}
                weights[date][user] = weight
        return weights  
    def _get_users_table(self):
        users_raw = self._get_table_data("users")
        users = {}
        for ur in users_raw:
            users[str(ur["UserID"])] = ur["UserName"]
        return users
    def _get_cash_table(self):
        cash_raw = self._get_table_data("cash")
        cash = {}
        for c in cash_raw:
            cash[str(c["UserID"])] = float(c["CashAmount"])
        return cash
    def _get_winners_table(self, limit_data_to_last_3_days=False):
        winners_raw = self._get_table_data("winners")
        winners = {}
        for wr in winners_raw:
            date =  str(wr["UtcDate"])
            if self.is_ok_to_include_date(date, limit_data_to_last_3_days):
                winners[date] = wr["winners"]
        return winners
    ######## Misc functions ##########   
    def add_cash(self, user_id, amount_to_add):
        print(f'    add_cash: adding {amount_to_add} to user {user_id}')
        user_id = str(user_id)
        cash = self._get_cash_table()
        current_amount = self.INITIAL_AMOUNT
        if user_id in list(cash.keys()):
            current_amount = cash[user_id]
        amount = current_amount + amount_to_add
        item = {'UserID': int(user_id), "CashAmount": str(amount)}
        self._put_table_item("cash", item)
    def get_multiple_keys_of_max_value(self, input_dict):
        max_value_keys=[]
        max_value = max(list(input_dict.values()))
        keys = list(input_dict.keys())
        for key in keys:
            val = input_dict[key]
            if val==max_value:
                max_value_keys.append(key)
        return max_value_keys
        
    ######## Date related functions ##########  
    def get_epoch_date(self):
        campaigns_raw = self._get_table_data("campaigns")
        campaign_id = 0   # Hard coded for now
        for campaign in campaigns_raw:
            if campaign["CampaignID"]==campaign_id:
               return campaign["EpochDate"]
        return None
    def get_today(self):
        return datetime.utcnow().date().isoformat() 
    def get_previous_date(self, date):
        return to_str(to_dt(date) - timedelta(days=1))
    def get_next_date(self, date):
        return to_str(to_dt(date) + timedelta(days=1))
    def is_a_valid_date(self, date):
        if self.epoch==None:
            self.epoch = self.get_epoch_date()     
        valid = True
        if to_dt(date)<to_dt(self.epoch):
            valid = False
        today = self.get_today()
        if to_dt(date)>to_dt(today):
            valid = False
        return valid



if __name__=="__main__":
   aws = Aws()
   #print(aws.is_a_valid_date("2000-01-01"))
   #print(aws.is_a_valid_date("2022-09-19"))
   #print(aws.is_a_valid_date("2022-09-18"))
   aws.add_cash(1, 0.1)
   exit()
   aws.get_today()
   aws._get_users_table()
   aws._get_weights_table(True)
   aws._get_weights_table(False)
   aws._get_cash_table(True)
   aws._get_cash_table(False)
   aws.add_cash(0, 0.1)

   
