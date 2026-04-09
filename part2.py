# Group #: B50
# Student names: Felipe Nunes and Nima Karimzadehshirazi

import threading
import queue
import time, random

def consumerWorker (queue: queue.Queue) -> None:
    """
    consumerWorker is the target function for the consumer threads. 
    It continuously consumes items from the queue until it receives a stop item, at which point it terminates gracefully. 
    The function simulates the time taken to consume an item by introducing a random sleep delay between consuming items.
    """
    def waitForItemToBeConsumed() -> None: #simulate the time taken to consume an item
        time.sleep(round(random.uniform(MIN_CONSUMER_SLEEP_TIME, MAX_CONSUMER_SLEEP_TIME), 2)) #a random delay (100 to 300 ms)
    
    # consume items from the queue until stop item is received
    while True:
        item = queue.get() #blocks until an item is available in the queue
        if item is STOP_ITEM: #check if the received item is the stop item, if so, break the loop and terminate the consumer thread gracefully
            break
        if DEBUG:
            print(f"Consumer {threading.current_thread().name} consumed item: {item}")
        waitForItemToBeConsumed() #simulate the time taken to consume the item

def producerWorker(queue: queue.Queue) -> None:
    """
    producerWorker is the target function for the producer threads.
    It continuously produces items and puts them in the queue until it has produced the specified number of items.
    The function simulates the time taken to produce an item by introducing a random sleep delay between producing items.
    """
    def waitForItemToBeProduced() -> int: #simulate the time taken to produce an item and return the produced item
        time.sleep(round(random.uniform(MIN_PRODUCER_SLEEP_TIME, MAX_PRODUCER_SLEEP_TIME), 2)) #a random delay (100 to 300 ms)
        return random.randint(1, 99)  #an item is produced
    # produce specified number of items and put them in the queue
    for _ in range(NUMBER_OF_ITEMS_TO_PRODUCE): #loop to produce specified number of items before terminating
        item = waitForItemToBeProduced()
        queue.put(item) #blocks until a free slot is available in the queue
        if DEBUG:
            print(f"Producer {threading.current_thread().name} produced item: {item}")
       

if __name__ == "__main__":
    buffer = queue.Queue()
    
    #for debugging purposes, set DEBUG to True to print the produced and consumed items along with the thread names, otherwise set it to False to suppress the debug prints
    DEBUG = True
    # consumer stop item
    STOP_ITEM = None
    # max and min consumer and producer sleep times in seconds
    MAX_PRODUCER_SLEEP_TIME = 0.3
    MIN_PRODUCER_SLEEP_TIME = 0.1
    MAX_CONSUMER_SLEEP_TIME = 0.3
    MIN_CONSUMER_SLEEP_TIME = 0.1
    # number of items to be produced by each producer thread before terminating
    NUMBER_OF_ITEMS_TO_PRODUCE = 10
    # creating 4 producer threads and 5 consumer threads as per the assignment instructions
    NUMBER_OF_PRODUCERS = 4
    NUMBER_OF_CONSUMERS = 5

    producers = [threading.Thread(target=producerWorker, args=(buffer,)) for _ in range(NUMBER_OF_PRODUCERS)]
    consumers = [threading.Thread(target=consumerWorker, args=(buffer,)) for _ in range(NUMBER_OF_CONSUMERS)]
    # starting all producer and consumer threads
    for producer in producers:
        producer.start()
    for consumer in consumers:
        consumer.start()

    # wait for all producer threads to finish producing items
    for producer in producers:
        producer.join()
    # producers have finished, now we need to signal the consumer threads to terminate gracefully by putting a stop item in the queue for each consumer thread
    for consumer in consumers:
        buffer.put(STOP_ITEM) #note that no consumer thread will consume more than one stop item since they terminate immediately after consuming the first stop
    for consumer in consumers:
        consumer.join() #wait for all consumer threads to finish consuming items and terminate gracefully before terminating the main thread

    if DEBUG:
        print("All producer and consumer threads have terminated gracefully.")
        
    # if the consumer threads were daemon threads, they would automatically terminate when the main thread terminates after all producer threads have finished producing items. 
    # However, assignment asks for graceful termination
    # Current solution:producers finish
        # main thread inserts one stop item per consumer
        # because the queue is FIFO, those stop items come after all real items already produced
        # each consumer eventually gets a stop item and exits
        # main thread joins all consumers