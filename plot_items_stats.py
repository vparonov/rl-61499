import numpy as np
import matplotlib.pyplot as plt

#fileName = 'vis/item_stats_latest_robust_iid.npy'
#fileName = 'vis/item_stats_b_801_816_1_1_1_10000_20000.txt_C1C20.4_iid.npy'
fileName = 'vis/item_stats_b_801_816_1_1_1_10000_20000.txt_latest_robust_iid.npy'

def plot_hist(fileName, label):
    stats = np.load(fileName)

    plt.hist(stats[:,1]-stats[:,0], label=label)

plot_hist('vis/item_stats_b_801_816_1_1_1_10000_20000.txt_C1C20.4_iid.npy', 'c1c20.4')
plot_hist('vis/item_stats_b_801_816_1_1_1_10000_20000.txt_latest_robust_iid.npy', 'robust')
plt.legend()
plt.show()