from cockroachdb.modules.transactions import (
    NewOrderTransaction,
    PaymentTransaction,
    DeliveryTransaction,
    OrderStatusTransaction,
    StockLevelTransaction,
    PopularItemsTransaction,
    TopBalanceTransaction,
    RelatedCustomerTransaction,
)

from cockroachdb.modules.experiments.client_handler import ClientHandler

from cockroachdb.modules.experiments.experiment_handler import ExperimentHandler


experiment = ExperimentHandler(5)

experiment.perform_experiment()

clients = experiment.get_experiment_client_transactions()

db_state = experiment.get_database_state()
