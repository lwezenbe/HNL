from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped
from HNL.EventSelection.eventCategorization import returnTexName, returnCategoryPtCuts

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--divideByCategory',   action='store_true', default=False,  help='Look at the efficiency per event category')
argParser.add_argument('--triggerTest',   action='store_true', default=False,  help='Use special format with multiple test cuts in loading efficiencies')
args = argParser.parse_args()

#Merges subfiles if needed
input_name  = os.getcwd()+'/data/calcSignalEfficiency/*'
if args.divideByCategory:       input_name += '/divideByCategory'
if args.triggerTest:                 input_name += '/triggerTest'
merge_files = glob.glob(input_name)
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)


inputFiles = glob.glob(input_name + '/*.root')
f_names = {f.split('/')[-1].split('.')[0] for f in inputFiles}

import ROOT
from HNL.Tools.helpers import rootFileContent, getObjFromFile
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat

def getCategory(name, trigger_test = False):
    if trigger_test: name = name.split('/')[1]
    split_name = name.split('_')
    try:       
        return (int(split_name[1]), int(split_name[2]))
    except:
        return None

def getCuts(name):
    try:
        name = name.split('/')[2]
    except:
        return
    split_name = name.split('_')
    output = []
    for x in [split_name[1], split_name[3], split_name[5]]:
        if x == 'None':
            output.append(None)
        else:
            output.append(int(x)) 
    try:
        return output
    except:
        return None

for f_name in f_names:
    if 'FO' in f_name: continue
    hists = {}
    keyNames = []
    sub_files = glob.glob(input_name + '/'+f_name+'.root')

    print 'plotting', f_name
    for f in sub_files:
        sample = f.split('/')[-3]
        output_dir = os.getcwd()+'/data/calcSignalEfficiency/Results/'+f_name +'/'+sample
        if args.divideByCategory:       output_dir += '/divideByCategory'
        if args.triggerTest:                 output_dir += '/triggerTest'
        output_dir = makePathTimeStamped(output_dir)
    
        rf = ROOT.TFile(f)
        if args.triggerTest:    get_nested = True
        else:                   get_nested = False

        keyNames = [k[0] for k in rootFileContent(rf, getNested=get_nested)]

        for k in keyNames:

            c = getCategory(k, args.triggerTest)
            if args.triggerTest:
                cuts = getCuts(k)
                obj_name = k +'/efficiency_'+str(c[0])+'_'+str(c[1])+'_l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2]) 
            else: 
                obj_name = k+k
               
            h = getObjFromFile(f, obj_name+'_num').Clone(obj_name.split('/')[2]+'_efficiency')
            h.Divide(getObjFromFile(f, obj_name+'_denom'))

            extra_text = [extraTextFormat(returnTexName(c), ypos = 0.83)] if c is not None else None

            if args.triggerTest: 
                cut_info = ''
                for i, l in enumerate(cuts):
                    if l is not None:
                        cut_info += 'p_{T}(l'+str(i+1)+') < '+str(l) +' GeV ; '
                if extra_text is not None:
                    extra_text.append(extraTextFormat(cut_info))
            
            elif args.divideByCategory:
                list_of_cuts = returnCategoryPtCuts(c)
                for j, cut in enumerate(list_of_cuts):
                    cut_info = ''
                    for i, l in enumerate(cut):
                        if l is not None:
                            cut_info += 'p_{T}(l'+str(i+1)+') < '+str(l) +' GeV ; '
                    if extra_text is not None:
                        extra_text.append(extraTextFormat(cut_info, textsize = 0.02))
                        if j < len(list_of_cuts) - 1: extra_text.append(extraTextFormat('OR', textsize=0.02))
            
            p = Plot(h, sample, obj_name.split('/')[2], h.GetXaxis().GetTitle(), h.GetYaxis().GetTitle(), extra_text=extra_text, y_log=True)
            if args.triggerTest:
                p.drawHist(output_dir = output_dir +'/'+obj_name.split('/')[1])
            else:
                p.drawHist(output_dir = output_dir, draw_option = 'EHistText')


