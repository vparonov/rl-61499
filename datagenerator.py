import random

NFILES = 1000
DATA_FOLDER = 'data/train_100_350_to_500life'

SEED = 0

FROM_ITEMS = 100
TO_ITEMS = 100

FROM_DEADLINE = 350
TO_DEADLINE = 500

W_ONLY_D1 = 1
W_ONLY_D2 = 1
W_BOTH = 1


if SEED > 0:
    random.seed(SEED)


for f in range(NFILES):
    nitems = random.randint(FROM_ITEMS, TO_ITEMS)
    stations_mask = random.choices([1,2,3], weights= [W_ONLY_D1, W_ONLY_D2, W_BOTH], k = nitems)
    deadline = random.randint(FROM_DEADLINE, TO_DEADLINE)#= random.sample(range(FROM_DEADLINE, TO_DEADLINE), k = nitems)

    lines = [ ','.join([str(i+1), 'S', str(stations_mask[i]), str(deadline)]) for i in range(len(stations_mask))]
    with open(f'{DATA_FOLDER}/b_{f}_{nitems}_{W_ONLY_D1}_{W_ONLY_D2}_{W_BOTH}_{FROM_DEADLINE}_{TO_DEADLINE}.txt', 'w') as f:
        for line in lines:
            f.write(f"{line}\n")