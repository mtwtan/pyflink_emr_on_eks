# Building the Docker images

## Flink operator image

```
## Example variables
export REGION=us-east-1
export ACCOUNT=123456789012
export TAG=0.1

aws ecr get-login-password \
  --region ${REGION} | docker login \
  --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com

docker build -t flink-1.18.0-uber-jar:${TAG} -f Dockerfile_flink .

docker tag flink-1.18.0-uber-jar:${TAG} ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/flink-1.18.0-uber-jar:${TAG}

docker push ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/flink-1.18.0-uber-jar:${TAG}
```

## Fluentd image

```
## Example variables
export REGION=us-east-1
export ACCOUNT=123456789012
export TAG=0.1

aws ecr-public get-login-password --region $REGION | docker login \
  --username AWS --password-stdin public.ecr.aws

docker build -t emr-7.0.0-fluentd:${TAG} -f Dockerfile_fluentd .

docker tag emr-7.0.0-fluentd:${TAG} ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/emr-7.0.0-fluentd:${TAG}

aws ecr get-login-password --region ${REGION} | docker login \
  --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com

docker push ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/emr-7.0.0-fluentd:${TAG}
```
