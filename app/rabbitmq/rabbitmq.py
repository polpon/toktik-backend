import pika, sys, json

class RabbitMQConnection:
    _instance = None

    def __new__(cls, host="localhost", port=5672):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host="localhost", port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.connect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port))
            print("Connected to Rabbit Mq")
        except:
            sys.exit("Could not connect to RabbitMq")

    def is_connected(self):
        return self.connection is not None and self.connection.is_open

    def close(self):
        if self.is_connected():
            self.connection.close()
            self.connection = None
            print("RabbitMQ connection closed")

    def get_channel(self):
        if self.is_connected():
            return self.connection.channel()
        else:
            self.connect();

        return None

    def send_data(self, queue_name, data):
        channel = self.get_channel()
        # print(channel)
        if (channel):
            channel.queue_declare(queue=queue_name)

            channel.basic_publish(exchange='',
                                routing_key=queue_name,
                                body=data)

            print(f" [x] Sent to '{queue_name}'")
            channel.close()
            return True
        return False

    def send_data_exchange(self, exchange_name="socketio", data=json.dumps({"socket_name": "", "data": ""})):
        channel = self.get_channel()
        # print(f"\n\n\n {channel} \n\n\n\n")
        if (channel):
            channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=False)

            channel.basic_publish(exchange=exchange_name,
                                routing_key='',
                                body=data)

            channel.close()
            return True
        return False
