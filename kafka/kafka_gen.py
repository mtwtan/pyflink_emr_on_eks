from kafka import KafkaProducer
from kafka.errors import KafkaError
import socket
import time
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider
from faker import Faker
import json
from random import seed
from random import randint
from datetime import date, datetime, timedelta
import sys

n = len(sys.argv)
print("Total arguments found: ", n)

if n < 3:
    print("Needs at least 2 arguments: one for the MSK bootstrap server URL and the other for REGION")
    exit(1)


BOOTSTRAP_SERVERS = sys.argv[1]
REGION = sys.argv[2]
print("Using KAFKA servers: ", BOOTSTRAP_SERVERS)
fake = Faker()

class MSKTokenProvider():
    def token(self):
        token, _ = MSKAuthTokenProvider.generate_auth_token(REGION)
        return token
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def genFakeData():

    coffee = ('pour','latte','mocha')

    coffee_prod_price_dict = {
        'pour':2.50,
        'latte': 4.50,
        'mocha': 5.00,
    }
    
    myuuid = uuid.uuid4()
    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    name = fake.name()
    address = fake.address()
    tel = fake.phone_number()
    aba = fake.aba()
    bankaccount = fake.bban()
    ccdetail = fake.credit_card_full()
    
    product = fake.random_element(elements=coffee)
    pricedollar = coffee_prod_price_dict[product]
    number = fake.random_int(min=1, max=10)
    total_amount = pricedollar * number
        
    day_random_diff = randint(0,5)
    current_dateTime = datetime.now()
    dateTime_delta = timedelta(days = day_random_diff)
    dateTime = current_dateTime - dateTime_delta
    day_of_month = dateTime.day
    month = dateTime.month
    year = dateTime.year

    d = {
      "uuid": str(myuuid),
      "event_time": event_time,
      "name": name,
      "address": address,
      "tel": tel,
      "aba": aba,
      "bankaccount": bankaccount,
      "creditcardinfo": ccdetail,
      "datereceived": dateTime.strftime("%Y-%m-%d %H:%M:%S"),
      "r_year": year,
      "r_month": month,
      "r_day": day_of_month,
      "product": product,
      "number": number,
      "total_amount": total_amount
    }

    return d

def main():
    numloop = randint(50,100)
    
    tp = MSKTokenProvider()
    
    print("Bootstrap server for Kafka Producer: ", BOOTSTRAP_SERVERS)
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        security_protocol='SASL_SSL',
        sasl_mechanism='OAUTHBEARER',
        sasl_oauth_token_provider=tp,
        client_id=socket.gethostname(),
    )
    
    topic = "test-topic"
    counter = 0
    
    for i in range(numloop):
        try:
            key = str(counter).encode()
            each_msg = json.dumps(genFakeData(), default=json_serial).encode('utf-8')
    
            producer.send(topic,key=key,value=each_msg)
            producer.flush()
            print("Produced: ",key, "\n",each_msg)
        except Exception:
            print("Failed to send: ", key, "\n", each_msg, "\n")
    
        counter+=1

    time.sleep(5)
    producer.close()

### Start of code

if __name__ == "__main__":
    while 1 == 1:
        main()
