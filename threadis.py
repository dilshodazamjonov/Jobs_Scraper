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
    def divide_list(lst, n=2):  # Changed from n=6 to n=2 to split the list into two parts
        """Divide the list into n sublists as evenly as possible."""
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]  # Divide into 2 parts

    divided_lists = divide_list(lst, 2)  # Use 2 sublists now
    threads = []

    for i, sublist in enumerate(divided_lists):
        print(len(sublist))  # Print the length of each sublist
        thread = threading.Thread(target=data.data_scrapping, args=(sublist,))  # Assuming data.data_scrapping method
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Wait for all threads to finish

