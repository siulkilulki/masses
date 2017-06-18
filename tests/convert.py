import pickle

parishes = []
with open('parishes.pickle', 'rb') as f:
    parishes = pickle.load(f)

tsv = ''
i = 0
for parish in parishes:
    t_tsv = parish['name'] + '\t' + parish['url'] + '\t' + parish['city'] + '\t' + parish['street'] + '\t' + parish['postal_code'] + '\t' + parish['meta_url'] + '\t' + parish['gps'] + '\n'
    tsv += t_tsv
    if parish['url']:
        i += 1
print(i)
with open('parishes.tsv', 'w') as f:
    f.write(tsv)
