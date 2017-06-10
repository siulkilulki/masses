import dill
from google import search


def check(parish):
    if parish.url in search(query, lang='pl', stop=10, pause=3.0):
        return true


def find_url(parish):
    pass


def stem_url(url):


def main():
    parishes = []
    with open('./parishes.dill', 'rb') as f:
        parishes = dill.load(f)

    for parish in parishes:
        if parish.url:
            check(parish)
        else:
            find_url(parish)

    import ipdb
    ipdb.set_trace()


if __name__ == "__main__":
    main()
