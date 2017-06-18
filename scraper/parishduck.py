from duckduckgo import DuckDuckGo


class ParishDuck():
    def __init__(self):
        ""
        pass

    def urls(self, parish, duck):
        query = parish['name'] + ' ' + parish['street'] + ' ' + parish['postal_code']
        links = duck.links(query)
        #sleep_time = random.randint(0, 1)
        #time.sleep(sleep_time)
        while not links:
            sleep_time = random.randint(1, 3)
            print('retry, sleeping ' + str(sleep_time) + 's')
            time.sleep(sleep_time)
            links = duck.links(query)
        return links
