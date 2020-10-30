import pathlib
import sys
import time
import peewee

from cockroachdb.modules.experiments.client_handler import ClientHandler
from cockroachdb.modules.models import Order, OrderLine, Customer, District, Warehouse, Stock
from cockroachdb.modules.transactions.base import BaseTransaction
from peewee import fn
from statistics import mean
from typing import List

class ExperimentHandler():
    """
    Client transactions
    
    Read transactions for a client from input file, process transactions and output database and transaction measurements
    """

    def __init__(
        self,
        experiment_number: int,
    ):
        self.experiment_number = experiment_number
        self.clients = List[ClientHandler]
        self.result = []
        

    def get_experiment_configurations(self):
        configurations = {
            5: (20, 4),
            6: (20, 5),
            7: (40, 4),
            8: (40, 5)
        }
    
        return configurations.get(self.experiment_number)

    def perform_experiment(self):
        configurations = self.get_experiment_configurations()
        num_of_clients = configurations[0]
        num_of_servers = configurations[1]
        
        self.clients = [ ClientHandler(i + 1) for i in range(num_of_clients) ]
        throughputs = []
        #TODO: change to distributed client transactions in different servers concurrently
        
        self.results = []
        for client in self.clients:
            client.process_client_transactions()
    
    def get_experiment_client_transactions(self):
        '''
        Get transaction details for all clients in the experiment
        To be stored in clients.csv
        '''
        for client in self.clients:
            self.result.append((self.experiment_number, ) + client.get_client_transaction_summary())

        return self.result     
        
    def get_database_state(self):
        '''
        Get database state
        Can be queried after an experienment finishes to get database status and store in db-state.csv
        '''
        sum_warehouse = Warehouse.select(fn.SUM(Warehouse.ytd)).scalar(as_tuple=True)
        sum_district = District.select(fn.SUM(District.ytd), 
                                       fn.SUM(District.next_order_id)
                                       ).scalar(as_tuple=True)
        sum_customer = Customer.select(fn.SUM(Customer.balance), 
                                       fn.SUM(Customer.ytd_payment),
                                       fn.SUM(Customer.payment_count),
                                       fn.SUM(Customer.delivery_count)
                                       ).scalar(as_tuple=True)
        sum_order = Order.select(fn.Max(Order.id),
                                 fn.SUM(Order.order_line_count)
                                 ).scalar(as_tuple=True)
        sum_order_line = OrderLine.select(fn.SUM(OrderLine.amount),
                                          fn.SUM(OrderLine.quantity)
                                          ).scalar(as_tuple=True)
        sum_stock = Stock.select(fn.SUM(Stock.quantity),
                                 fn.SUM(Stock.ytd),
                                 fn.SUM(Stock.order_count),
                                 fn.SUM(Stock.remote_count)
                                 ).scalar(as_tuple=True)
        
        summary = (self.experiment_number,) + sum_warehouse + sum_district + sum_customer + sum_order + sum_order_line + sum_stock
        
        return summary
    
    
    def get_experiment_throughput_detail(self):
        '''
        Get minimum, average and maximum transaction throughputs among all clients in the experiment
        To be stored in throughput.csv
        '''
        throughputs = [client.throughput for client in self.clients]
        
        return ((self.experiment_number, min(throughputs), mean(throughputs), max(throughputs)))
        