import numpy as np
import matplotlib.pyplot as plt

def plot_hist(fileName, label):
    stats = np.load(fileName)

    plt.hist(stats[:,1]-stats[:,0], label=label, alpha=0.5)

plot_hist('vis/item_stats_b_979_116_1_1_1_10000_20000.txt_latest_iid.npy', 'latest')
plot_hist('vis/item_stats_b_979_116_1_1_1_10000_20000.txt_min-per-item_iid.npy', 'min-per-item')
plt.legend()
plt.show()