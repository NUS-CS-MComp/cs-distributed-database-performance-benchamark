import pathlib
import sys
import time

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

DATA_PATH = (
    pathlib.Path(__file__).parent.parent.parent.parent / "data/test-xact-files"
)


class ClientHandler():
    """
    Client transactions
    
    Read transactions for a client from input file, process transactions and output database and transaction measurements
    """

    def __init__(
        self,
        client_number: int,
    ):
        self.client_number = client_number
        self.num_of_transactions = 0
        self.elapsed_time = 0
        self.throughput = float("inf")
        self.avg_latency = float("inf")
        self.median_latency = float("inf")
        self.latency_95_pct = float("inf")
        self.latency_99_pct = float("inf")
    
    
    def get_transaction(self, transaction_type, inputs):
        """
        Get transaction instance with transaction type and relevant inputs
        """
        if transaction_type == "N":
            return NewOrderTransaction(*inputs)
        elif transaction_type == "P":
            return PaymentTransaction(tuple(inputs[:3]), float(inputs[-1]))
        elif transaction_type == "D":
            return DeliveryTransaction(*inputs)
        elif transaction_type == "O":
            return OrderStatusTransaction(tuple(inputs[:3]))
        elif transaction_type == "S":
            return StockLevelTransaction(*inputs)
        elif transaction_type == "I":
            return PopularItemsTransaction(*inputs)
        elif transaction_type == "R":
            return RelatedCustomerTransaction(tuple(inputs[:3]))
        elif transaction_type == "T":
            return TopBalanceTransaction()
        else:
            return None
        

    def read_and_execute_transactions(self):
        input_file_name = DATA_PATH / (str(self.client_number) + ".txt")
        
        user_inputs = open( input_file_name, "r")
        
        while True:
            try:
                line = user_inputs.readline()
                
                if not line:  #EOF
                    break
                
                transaction_type = line[0]
                
                if transaction_type != "N":
                    transaction_inputs = line.split(",")[1:]
                    
                else:
                    # get new order item details in following lines
                    num_of_items = int(line.split(",")[-1])
                    item_number_list = []
                    supplier_warehouse_list = [] 
                    quantity_list = []
                    
                    for item in range(num_of_items):  
                        detail = user_inputs.readline().split(",")
                        item_number_list.append(int(detail[0]))
                        supplier_warehouse_list.append(int(detail[1]))
                        quantity_list.append(int(detail[2]))
                        
                    transaction_inputs = [ tuple(line.split(",")[2:4]) + (line.split(",")[1],), num_of_items, 
                                          item_number_list, supplier_warehouse_list, quantity_list ]
                    
                transaction = self.get_transaction(transaction_type, transaction_inputs)
                
                if transaction is not None:
                    self.num_of_transactions += 1
                    transaction.run()
            except:
                print("error handling transaction")
                            
    
    def process_client_transactions(self):
        """
        Process client transactions
        """
        start_time = time.time()
        self.read_and_execute_transactions()
        end_time = time.time()
        self.elapsed_time = end_time - start_time
        self.throughput = self.num_of_transactions / self.elapsed_time
        # TODO: other measurements
        
        #self.print_measurements()
        
        
    def print_measurements(self):
        """
        Output performance measurements for transactions
        """
        print(f"Total number of transactions processed: {self.num_of_transactions}", file=sys.stderr)
        print(f"Total elapsed time: {self.elapsed_time}s", file=sys.stderr)
        print(f"Transaction throughput: {self.throughput}", file=sys.stderr)
        print(f"Average transaction latency: {self.avg_latency}", file=sys.stderr)
        print(f"Median transaction latency: {self.median_latency}", file=sys.stderr)
        print(f"95th percentile transaction latency: {self.latency_95_pct}", file=sys.stderr)
        print(f"99th percentile transaction latency: {self.latency_99_pct}", file=sys.stderr)
        
    
    def get_client_transaction_summary(self):
        ''''
        Get summary for transactions for a client
        To be used together with experiment information and stored in clients.csv
        '''
        return ((self.client_number, self.num_of_transactions, self.elapsed_time, self.throughput, self.avg_latency,
                 self.median_latency, self.latency_95_pct, self.latency_99_pct))
        
        
        
        
        
        
        
        
                