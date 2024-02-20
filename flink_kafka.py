from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.table import StreamTableEnvironment
from pyflink.table.udf import udf
import re
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--broker')
#args = vars(parser.parse_args())

args = parser.parse_args()

if args.broker == None:
    print("Enter the Kafka broker URL")
    exit(1)

BOOTSTRAP_SERVERS = args.broker

env = StreamExecutionEnvironment.get_execution_environment()
env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
env.enable_checkpointing(60000)

JAR_PATHS = tuple(
       [
           "file:///usr/lib/flink/plugins/pyflink-uber-jar/pyflink-uber-jar-1.0.0.jar"
       ]
    )
#print(JAR_PATHS)
env.add_jars(*JAR_PATHS)

table_env = StreamTableEnvironment.create(stream_execution_environment=env)
#table_env.create_temporary_function(
#    "add_source", udf(lambda: "NYCTAXI", result_type="STRING")
#)

def inject_security_opts(opts: dict, bootstrap_servers: str):
    if re.search("9098$", bootstrap_servers):
        opts = {
            **opts,
            **{
                "properties.security.protocol": "SASL_SSL",
                "properties.sasl.mechanism": "AWS_MSK_IAM",
                "properties.sasl.jaas.config": "software.amazon.msk.auth.iam.IAMLoginModule required;",
                "properties.sasl.client.callback.handler.class": "software.amazon.msk.auth.iam.IAMClientCallbackHandler",
            },
        }
    return ", ".join({f"'{k}' = '{v}'" for k, v in opts.items()})

def create_source_table(table_name: str, topic_name: str, bootstrap_servers: str):
    opts = {
        "connector": "kafka",
        "topic": topic_name,
        "properties.bootstrap.servers": bootstrap_servers,
        "properties.group.id": "source-group",
        "format": "json",
        "scan.startup.mode": "earliest-offset",
    }

    stmt = f"""
    CREATE TABLE {table_name} (
        event_time          VARCHAR,
        name                VARCHAR,
        address             VARCHAR,
        tel                 VARCHAR,
        ssn                 VARCHAR,
        bankaccount         VARCHAR,
        creditcardinfo      VARCHAR,
        datereceived        VARCHAR,
        r_year                INT,
        r_month               INT,
        r_day                 INT
    ) WITH (
        {inject_security_opts(opts, bootstrap_servers)}
    )
    """
    print(stmt)
    return stmt

def set_insert_sql(source_table_name: str, sink_table_name: str):
    stmt = f"""
    INSERT INTO {sink_table_name}
    SELECT
        name,
        address,
        tel,
        ssn,
        bankaccount,
        creditcardinfo,
        datereceived,
        r_year,
        r_month,
        r_day 
    FROM {source_table_name}
    """
    print(stmt)
    return stmt


def create_sink_table(table_name: str, file_path: str):
    stmt = f"""
    CREATE TABLE {table_name} (
        name                VARCHAR,
        address             VARCHAR,
        tel                 VARCHAR,
        ssn                 VARCHAR,
        bankaccount         VARCHAR,
        creditcardinfo      VARCHAR,
        datereceived        VARCHAR,
        r_year                INT,
        r_month               INT,
        r_day                 INT
    ) PARTITIONED BY (`r_year`, `r_month`, `r_day`) WITH (
        'connector'= 'filesystem',
        'path' = '{file_path}',
        'format' = 'parquet',
        'sink.partition-commit.delay'='1 h',
        'sink.partition-commit.policy.kind'='success-file'
    )
    """
    print(stmt)
    return stmt


def main():
    #### variables
    ## source
    
    source_table_name = "source_customer"
    source_topic_name = "test-topic"
    source_bootstrap_servers = BOOTSTRAP_SERVERS
    
    ## sink
    
    sink_table_name = "sink_customer"
    sink_file_path = "s3://{ S3 Bucket Name }/customer/sink/"
    
    #### create tables
    table_env.execute_sql(
        create_source_table(
            source_table_name, source_topic_name, source_bootstrap_servers
        )
    )
    
    table_env.execute_sql(create_sink_table(sink_table_name, sink_file_path))
    #table_env.execute_sql(create_print_table(print_table_name))

    #statement_set = table_env.create_statement_set()
    #statement_set.add_insert_sql(set_insert_sql(source_table_name, sink_table_name))
    ###statement_set.add_insert_sql(set_insert_sql(print_table_name, sink_table_name))
    #statement_set.execute().wait()

    table_result = table_env.execute_sql(
        set_insert_sql(source_table_name, sink_table_name)
    )
    print(table_result.get_job_client().get_job_status())

if __name__ == "__main__":
    main()
