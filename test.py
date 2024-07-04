import threading
import time


results = {}

def get_list(results:dict[any,any]):
    time.sleep(2)
    results["test"] = ["a","b","c"]

t = threading.Thread(target=get_list, args=(results,))
t.start()
# in your game loop
while True:
    if not t.is_alive():
        result = results["test"]
        print(result)
        break
        

