from faker import Faker
import json
from random import seed
from random import randint
from datetime import date, datetime, timedelta
import sys
import boto3
import uuid

# Variables - modify as necessary
ACCOUNT = "123456789012"
REGION = "us-east-1"
PARTITION_KEY = "uuid"
STREAM_NAME = "coffee-stream"
STREAM_ARN = "arn:aws:kinesis:${REGION}:${ACCOUNT}:stream/${STREAM_NAME}"

fake = Faker()

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

    # Generate 100 records
    #records = []

    #for i in range(99):
    #    data = genFakeData()
    #    records.append(json.dumps(data))

    #print(records)

    records = genFakeData()

    client = boto3.client('kinesis', region_name=REGION)

    response = client.put_record(
        Data=json.dumps(records).encode('utf-8'),
        PartitionKey=PARTITION_KEY,
        StreamName=STREAM_NAME,
        StreamARN=STREAM_ARN
    )

    print(response)

if __name__ == "__main__":
    while 1 == 1:
        main()
