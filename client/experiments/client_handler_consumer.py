import multiprocessing

from client.handlers.base import BaseSingleClientHandler


class ClientHandlerConsumer(multiprocessing.Process):
    def __init__(self, handler_queue, result_queue):
        """
        Initiate a client handler consumer for parallel processing
        :param handler_queue: queue of client handlers
        :param result_queue: queue of client results
        """
        super(ClientHandlerConsumer, self).__init__()
        self.handler_queue = handler_queue
        self.result_queue = result_queue

    def run(self):
        """
        Override multiprocessing run method
        :return: None
        """
        while True:
            next_handler: BaseSingleClientHandler = self.handler_queue.get()
            if next_handler is None:
                self.handler_queue.task_done()
                break
            next_handler.process_client_transactions()
            self.handler_queue.task_done()
            self.result_queue.put(next_handler)
