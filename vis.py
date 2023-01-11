import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def ShowAnimation(states, updateIntervalMs, outputFileName = None, frameRate = 30):
        def update(frameNum, img, ax):
            c = states.shape[0] 
            i = frameNum % c # frameNum should never be larger than c. so this line is not necessary
            ax.set_title('frame ' + str(frameNum+1)+' of '+str(c))
            img.set_data(states[i])
           
            return img,

        fig, ax = plt.subplots()
        img = ax.imshow(states[0], vmin = 0, vmax = 3, aspect='auto', cmap='viridis')
        ani = animation.FuncAnimation(fig, update, fargs=(img,ax,),
                                    frames = states.shape[0],
                                    interval=updateIntervalMs,
                                    save_count=50)
    
        if outputFileName is not None:
            ani.save(outputFileName, fps=frameRate, extra_args=['-vcodec', 'libx264'])
    
        plt.show()


fullState = np.load('vis/full_state_rl_best_iid.npy')


frameid = 16
# 0     10     11    12   22    23    24     25   26    27    28    38    39    40    41    42    43 
# 'c1', 'c2', 'd1', 's1', 'p1', 'p2', 'p3', 'p4', 'p5', 'd2', 's2', 'q1', 'q2', 'q3', 'q4', 'q5', 'c3'
comp_map = [
    {'ty':18, 'tx':0,  'sx': 0,  'w':10, 'r':False }, #c1
    {'ty':18, 'tx':10, 'sx': 10, 'w':10, 'r':False  }, #c2
    {'ty':18, 'tx':20, 'sx': 11, 'w':1, 'r':False  },  #d1
    {'ty':16, 'tx':20, 'sx': 12, 'w':10, 'r':True  }, #s1
    {'ty':14, 'tx':12, 'sx': 22, 'w':1, 'r':False  }, #p1    
    {'ty':14, 'tx':13, 'sx': 23, 'w':1, 'r':False  }, #p2    
    {'ty':14, 'tx':14, 'sx': 24, 'w':1, 'r':False  }, #p3    
    {'ty':14, 'tx':15, 'sx': 25, 'w':1, 'r':False  }, #p4    
    {'ty':14, 'tx':16, 'sx': 26, 'w':1, 'r':False  }, #p5    
    {'ty':18, 'tx':21, 'sx': 27, 'w':1, 'r':False  }, #d2
    {'ty':20, 'tx':21, 'sx': 28, 'w':10, 'r':True  }, #s2
    {'ty':22, 'tx':13, 'sx': 38, 'w':1, 'r':False  }, #q1    
    {'ty':22, 'tx':14, 'sx': 39, 'w':1, 'r':False  }, #q2    
    {'ty':22, 'tx':15, 'sx': 40, 'w':1, 'r':False  }, #q3    
    {'ty':22, 'tx':16, 'sx': 41, 'w':1, 'r':False  }, #q4    
    {'ty':22, 'tx':17, 'sx': 42, 'w':1, 'r':False  }, #q5    
    {'ty':18, 'tx':22, 'sx': 43, 'w':10, 'r':False  }, #c3
 
]



frames = np.zeros(shape=(fullState.shape[0], 32, 32))

print(frames.shape)

for frameid in range(fullState.shape[0]):
    for c in comp_map:
        if c['r']:
            frames[frameid, c['ty'],  c['tx']-c['w']+1:(c['tx']+1 )] =  fullState[frameid,  c['sx']:(c['sx']+c['w'])][::-1]
        else:
            frames[frameid, c['ty'],  c['tx']:(c['tx'] + c['w'])] = fullState[frameid,  c['sx']:(c['sx']+c['w'])]
    
ShowAnimation(frames, 250)


