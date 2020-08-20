import numpy as np

def DistJ(ds, r, dt, DT):
    eDist = np.sqrt((ds/r)**2 + (dt/DT)**2)
    return eDist