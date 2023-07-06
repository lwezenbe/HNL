from HNL.Tools.helpers import getObjFromFile
prompt = getObjFromFile('../Stat/data/shapes/default-lowMassSRloose/UL2018/mu/HNL-mu-m30-Vsq2.5em06-prompt/Majorana/A-MuMuMu-E-lowestmassmu.shapes.root', 'A-MuMuMu-E/HNL-mu-m30-Vsq2.5em06-prompt')
displaced = getObjFromFile('../Stat/data/shapes/default-lowMassSRloose/UL2018/mu/HNL-mu-m30-Vsq2.5em06-displaced/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m30-Vsq2.5em06-displaced')


print prompt.GetSumOfWeights(), prompt.GetEntries()
print displaced.GetSumOfWeights(), displaced.GetEntries()
