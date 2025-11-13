import threading
import math

# Function to divide the list into 5 parts
def divide_list(lst, n=5):
    """Divide the list into n roughly equal parts."""
    length = len(lst)
    chunk_size = math.ceil(length / n)
    return [lst[i:i + chunk_size] for i in range(0, length, chunk_size)]

# Function to be executed in each thread
def process_list_in_thread(thread_name, sublist):
    print(f"{thread_name} started with list: {sublist}")
    for item in sublist:
        print(f"{thread_name} processing: {item}")
    print(f"{thread_name} finished.")


def assign_lists_to_threads(data, lst):
    """
    Divide the list into 2 parts, create a thread for each, and return the threads.
    """
    def divide_list(lst, n=2):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    divided_lists = divide_list(lst, 2)
    threads = []

    for i, sublist in enumerate(divided_lists):
        thread = threading.Thread(target=data.data_scrapping, args=(sublist,))
        threads.append(thread)
        thread.start()

    return threads  # important: return the list of threads


