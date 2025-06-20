# Start container
```shell
docker run -d --name broker apache/kafka:3.8.0
```

# Start container with docker compose
```shell
docker compose up -d
```

# open shell
```shell
docker exec --workdir /opt/kafka/bin/ -it broker sh
```

# For manual launch of kafka server
## Generate a cluster UUID that will uniquely identify the Kafka cluster.

```shell
KAFKA_CLUSTER_ID="$(./kafka-storage.sh random-uuid)"
```
This cluster id will be used by the KRaft controller.

## KRaft requires the log directories to be configured. Run the following command to configure the log directories passing the cluster ID.
```shell
./kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c ../config/kraft/server.properties
```

## Now that KRaft is configured, you can start the Kafka server by running the following command.
```shell
./kafka-server-start.sh ../config/kraft/server.properties
```

# Exercise 1 - Topics, produce and consume

## To create a topic named news, run the command below.
```shell
./kafka-topics.sh --create --topic news --bootstrap-server localhost:9092
```

## You need a producer to send messages to Kafka. Run the command below to start a producer.
```shell
./kafka-console-producer.sh   --bootstrap-server localhost:9092   --topic news
```

## Run the command below to listen to the messages in the topic news.
```shell
./kafka-console-consumer.sh   --bootstrap-server localhost:9092   --topic news   --from-beginning
```
## Notice there is a tmp directory. The kraft-combine-logs inside the tmp directory contains all the logs. To check the logs generated for the topic news run the following command:

```shell
cd ..
ls /tmp/kraft-combined-logs
```

# Exercise 2 - Message Keys and offset
## Create a topic and producer for processing bank ATM transactions
### Create a new topic called bankbranch
To simplify the topic configuration and better explain how message key and consumer offset work, you specify the --partitions 2 argument to create two partitions for this topic. 
To compare the differences, you may try other partitions settings for this topic.

```shell
./kafka-topics.sh --create --topic bankbranch --partitions 2 --bootstrap-server localhost:9092
```
### List all topics to check if bankbranch has been created successfully.
```shell
./kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### You can also use the --describe command to check the details of the topic bankbranch.
```shell
./kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic bankbranch
```
You can view the bankbranch as two partitions, Partition 0 and Partition 1. 
If no message keys are specified, messages will be published to these two partitions in an alternating sequence like this:
Partition 0 -> Partition 1 -> Partition 0 -> Partition 1 

### Create a producer for the topic bankbranch.
```shell
./kafka-console-producer.sh --bootstrap-server localhost:9092 --topic bankbranch
```
add the following ATM messages after the icon >:
```json
{"atmid": 1, "transid": 100}
{"atmid": 1, "transid": 101}
{"atmid": 2, "transid": 200}
{"atmid": 1, "transid": 102}
{"atmid": 2, "transid": 201}
```

### Create a consumer in a new terminal window
```shell
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --from-beginning
```

You should be able to view the five new messages that you published. 
However, the messages may not be consumed in the same order as they were published. Typically, you will need to keep the consumed messages sorted in their original published order, especially for critical use cases, such as financial transactions.

## Produce and consume with message keys
In this step, you will use message keys to ensure that messages with the same key are consumed in the same order as they were published. 

In the back end, messages with the same key are published into the same partition and will always be consumed by the same consumer. As such, the original publication order is kept on the consumer side.

### You will now start a new producer and consumer using message keys. 
You can start a new producer with the following message key options:
`--property parse.key=true` to make the producer parse message keys
`--property key.separator=:` define the key separator to be the `:` character, so our message with key now looks like the following key-value pair example:
`1:{"atmid": 1, "transid": 102}`
Here, the message key is 1, which also corresponds to the ATM ID, and the value is the transaction JSON object, {"atmid": 1, "transid": 102}.

Start a new producer with the message key enabled.
```shell
./kafka-console-producer.sh --bootstrap-server localhost:9092 --topic bankbranch --property parse.key=true --property key.separator=:
```
Once you see the > symbol, you can start to produce the following messages, where you define each key to match the ATM ID for each message:
```json
1:{"atmid": 1, "transid": 103}
1:{"atmid": 1, "transid": 104}
2:{"atmid": 2, "transid": 202}
2:{"atmid": 2, "transid": 203}
1:{"atmid": 1, "transid": 105}
```

### Start a new consumer with --property print.key=true and --property key.separator=: arguments to print the keys.
```shell
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --from-beginning --property print.key=true --property key.separator=:
```
Now, you should see that messages with the same key are being consumed in the same order (for example: trans102 -> trans103 -> trans104) as they were published.

Each topic partition maintains its message queue, and new messages are enqueued (appended to the end of the queue) as they are published to the partition. Once consumed, the earliest messages are dequeued and no longer available for consumption.

Recall that with two partitions and no message keys specified, the transaction messages were published to the two partitions in rotation:

Partition 0: [{"atmid": 1, "transid": 100}, {"atmid": 2, "transid": 200}, {"atmid": 2, "transid": 201}]

Partition 1: [{"atmid": 1, "transid": 101}, {"atmid": 1, "transid": 102}]

As you can see, the transaction messages from atm1 and atm2 got scattered across both partitions. It would be difficult to unravel this and consume messages from one ATM in the same order as they were published.

However, with the message key specified as the atmid value, the messages from the two ATMs will look like the following:

Partition 0: [{"atmid": 1, "transid": 103}, {"atmid": 1, "transid": 104}, {"atmid": 1, "transid": 105}]

Partition 1: [{"atmid": 2, "transid": 202}, {"atmid": 2, "transid": 203}]

Messages with the same key will always be published to the same partition so that their published order will be preserved within the message queue of each partition.

As such, you can keep the states or orders of the transactions for each ATM.

## Consumer offset
Topic partitions keep published messages in a sequence, such as a list. Message offset indicates a message's position in the sequence. For example, the offset of an empty Partition 0 of bankbranch is 0, and if you publish the first message to the partition, its offset will be 1.

Using offsets in the consumer, you can specify the starting position for message consumption, such as from the beginning to retrieve all messages or from some later point to retrieve only the latest messages.

### Consumer group
In addition, you normally group related consumers together as a consumer group.
For example, you may want to create a consumer for each ATM in the bank and manage all ATM-related consumers
together in a group.

So let's see how to create a consumer group, which is actually very easy with the --group argument.
In the consumer terminal, stop the previous consumer if it is still running.
Run the following command to create a new consumer within a consumer group called atm-app:
```shell
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

After the consumer within the atm-app consumer group is started, you should not expect any messages to be consumed. This is because the offsets for both partitions have already reached the end. In other words, previous consumers have already consumed all messages and therefore queued them.

You can verify that by checking consumer group details.

### Show the details of the consumer group atm-app:

```shell
./kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group atm-app
```

Now you should see the offset information for the topic bankbranch:

Recall that you have published `10` messages in total, and you can see the `CURRENT-OFFSET` column of partition 1 and partition 0 add up to 10 messages.

The `LOG-END-OFFSET` column indicates the last offset or the end of the sequence. Thus, both partitions have reached the end of their queues and no more messages are available for consumption.

Meanwhile, you can check the `LAG` column which represents the number of unconsumed messages for each partition.

Currently, it is `0` for all partitions, as expected.

### Next, let's produce more messages and see how the offsets change.
Switch to the previous producer terminal and publish two more messages:
```json
1:{"atmid": 1, "transid": 106}
2:{"atmid": 2, "transid": 204}
```

Switch back to the consumer terminal and check the consumer group details again.
```shell
./kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group atm-app
```

You should see that both offsets have been increased by 1, and the `LAG` columns for both partitions have become `1`. It means you have one new message for each partition to be consumed.

### Start the consumer again and see whether the two new messages will be consumed.
```shell
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

Both partitions have reached the end once again.

## Reset offset
Next, let's look at how you can set the partitions to consume the messages again from the beginning through resetting offset.

You can reset the index with the `--reset-offsets` argument.

First, let's try resetting the offset to the earliest position (beginning) using `--reset-offsets --to-earliest`.

### Stop the previous consumer if it is still running, and run the following command to reset the offset.

```shell
./kafka-consumer-groups.sh --bootstrap-server localhost:9092  --topic bankbranch --group atm-app --reset-offsets --to-earliest --execute
```
Now, the offsets have been set to 0 (the beginning).

### Start the consumer again:
```shell
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```
You should see that all 12 messages are consumed and that all offsets have reached the partition ends again.

You can reset the offset to any position. For example, let's reset the offset so that you only consume the last two messages.

### Stop the previous consumer.

### Shift the offset to the left by two using --reset-offsets --shift-by -2:

```shell
./kafka-consumer-groups.sh --bootstrap-server localhost:9092  --topic bankbranch --group atm-app --reset-offsets --shift-by -2 --execute
```

### If you run the consumer again, you should see that you consumed four messages, 2 for each partition:
```shell
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

Stop your producer, consumer and the Kafka server.