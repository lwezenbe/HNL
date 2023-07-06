from HNL.Tools.outputTree import OutputTree
import numpy as np
import time


time_zero  = time.time()
#in_tree = OutputTree('events_nominal', '../Analysis/data/runAnalysis/HNL/cutbased-default-ZZCR-reco/UL-2016post/bkgr/ZZ-H/variables.root')
in_tree = OutputTree('events_nominal', '../Analysis/data/runAnalysis/HNL/cutbased-default-ZZCR-reco/UL-2016post/bkgr/WZ/variables.root')
hist = in_tree.getHistFromTree('MllZ2', 'hname', np.arange(70., 112., 2.), '((category==11||category==12||category==13||category==14||category==15||category==16)&&isprompt&&!issideband)')
time_one = time.time()

from rootpy.io.pickler import dump
dump(hist, 'test_hist.root')

from rootpy.io.pickler import load
in_hist  = load('test_hist.root')

time_two = time.time()


print time_one - time_zero, time_two - time_one
