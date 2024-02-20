# Deploying Python Flink workoad into EMR on EKS using Flink Kubernetes operator

## Pre-requisites
1. Ensure that you have an EKS cluster and follow the pre-requisites as described in the [AWS documentation](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/jobruns-flink-kubernetes-operator-setup.html).

2. Follow the steps in the [AWS documentation](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/jobruns-flink-kubernetes-operator-getting-started.html) on getting started with Flink Kubernetes operator. Make sure that `flink` namespace is created (we are using `flink` as a namespace for this example, but you can choose a different namespace.

3. In step 4 of the above documentation, follow the steps outlined here:

## Start either a Kinesis or Kafka stream

4. To set up a Kinesis client, make sure that boto3 is installed. Otherwise:

```
python3 -m pip install boto3
```
Once that is installed, run the python script:

```
python3 kinesis_gen.py
```

5. To set up a Kafka client, follow the instructions in the [AWS documentation](https://docs.aws.amazon.com/msk/latest/developerguide/mkc-create-topic.html). Once that has been created, pip install kafka-python:

```
python3 -m pip install kafka-python
```
Once all the above has been installed, run the python script:
```
python3 kafka_gen.py
```

6. Once the streaming has started for a while, you can start to submit your Flink job.

7. Upload the relevant python script to S3. If you are streaming with Kinesis, choose `flink_kinesis.py` and if you are streaming with Kafka, choose `flink_kafka.py`.

8. Modify either `flink_deploy_kafka.yaml` or `flink_deploy_kinesis.yaml` to your needs. Then, run the following command:

```
# For Kinesis stream
kubectl apply -f flink_deploy_kinesis.yaml -n flink

# For Kafka stream
kubectl apply -f flink_deploy_kafka.yaml -n flink
```
9. To view the job runs on Flink UI, follow the instructions in step 3 of the [AWS documentation](https://docs.aws.amazon.com/emr/latest/EMR-on-EKS-DevelopmentGuide/jobruns-flink-kubernetes-operator-run-application.html):

```
# Using the example of the "python-example" deployment name and "flink" as namespace

kubectl port-forward deployments/python-example 8081 -n flink
``` 
On your local browser, go to `http://localhost:8081`.
