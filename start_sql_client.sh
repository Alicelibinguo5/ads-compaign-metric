#!/bin/bash

# Start Flink SQL Client with Iceberg and S3 JARs

echo "Starting Flink SQL Client with Iceberg support..."

# Set the classpath to include our JARs
export FLINK_CLASSPATH="lib/iceberg-flink-runtime-1.17-1.4.2.jar:lib/flink-s3-fs-hadoop-1.17.0.jar:lib/hadoop-aws-3.3.4.jar:lib/hadoop-common-3.3.4.jar:lib/hadoop-client-3.3.4.jar:lib/hadoop-hdfs-3.3.4.jar:lib/hadoop-hdfs-client-3.3.4.jar:lib/aws-java-sdk-bundle-1.12.261.jar:lib/hive-metastore-3.1.3.jar:lib/hive-exec-3.1.3.jar:lib/hadoop-mapreduce-client-core-3.3.4.jar:lib/libthrift-0.16.0.jar"

# Start the SQL client
cd flink-1.17.0
./bin/sql-client.sh 