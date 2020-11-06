from cockroachdb.client.config import TRANSACTION_DATA_PATH
from cockroachdb.client.handlers import SingleClientHandlerFactory

if __name__ == "__main__":
    Client = SingleClientHandlerFactory.generate_new_client(
        SingleClientHandlerFactory.COCKROACH_DB
    )
    cockroach = Client(
        client_number=1, num_servers=5, data_dir=TRANSACTION_DATA_PATH
    )
    cockroach.process_client_transactions()
