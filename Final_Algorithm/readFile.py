def readinFile():
    with open("ListOfDomains2.csv") as f:
        stocks = f.read().splitlines()
        return stocks

readinFile()

def main():
    # history = get_top_visited(get_history(), 10)
    # history = ["ask.com", "tumblr.com"]
    # controller.authenticate()
    # experiment_smartor(history)
    readinFile()
    # experiment_tor(history)