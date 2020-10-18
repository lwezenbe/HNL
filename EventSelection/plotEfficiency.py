import os
import glob
from HNL.Tools.helpers import makePathTimeStamped
from HNL.Tools.efficiency import Efficiency

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--FOcut',   action='store_true', default=False,  help='Perform baseline FO cut')
argParser.add_argument('--divideByCategory',   action='store_true', default=False,  help='Look at the efficiency per event category')
argParser.add_argument('--compareTriggerCuts', action='store', default=None, 
    help='Look at each trigger separately for each category. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--massRegion',   action='store', default=None,  help='apply the cuts of high or low mass regions', choices=['high', 'low'])
args = argParser.parse_args()


#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.year, 'noskim', 'signallist_'+str(args.year))


jobs = []
flavors = ['tau', 'e', 'mu', '2l'] if args.flavor is None else [args.flavor]
for sample_name in sample_manager.sample_names:
    for flavor in flavors:
        if not '-'+flavor+'-' in sample_name: continue
        sample = sample_manager.getSample(sample_name)
        for njob in xrange(sample.split_jobs): 
            jobs += [(sample.name, str(njob), flavor)]

#Merges subfiles if needed
category_split_str = 'allCategories' if not args.divideByCategory else 'divideByCategory'
trigger_str = args.compareTriggerCuts if args.compareTriggerCuts is not None else 'regularRun'
mass_str = args.massRegion+'MassCuts' if args.massRegion is not None else 'noMassCuts'
flavor_name = args.flavor if args.flavor else 'allFlavor'

input_name  = os.path.join(os.getcwd(), 'data', 'calcSignalEfficiency', category_split_str, trigger_str, mass_str, flavor_name, '*')
merge_files = glob.glob(input_name)
script = os.path.expandvars(os.path.join('$CMSSW', 'src', 'HNL', 'EventSelection', 'calcSignalEfficiency.py')
merge(merge_files, __file__, jobs, ('sample', 'subJob', 'flavor'))

input_name  = os.path.join(os.getcwd(), 'data', 'calcSignalEfficiency', category_split_str, trigger_str, mass_str, flavor_name)

inputFiles = glob.glob(input_name + '/*.root')
f_names = {f.split('/')[-1].split('.')[0] for f in inputFiles}

from HNL.Plotting.plot import Plot

def getCategory(name, trigger_test = False):
    if trigger_test or args.cumulativeCuts: name = name.split('/')[1]
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

    sub_files = glob.glob(input_name + '/'+f_name+'.root')


#
#   TODO: THIS CODE SEEMS VERY OUTDATED, PLEASE UPDATE
#

    print 'plotting', f_name
    for f in sub_files:
        output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'calcSignalEfficiency', f_name, category_split_str, trigger_str, mass_str, flavor_name)
        output_dir = makePathTimeStamped(output_dir)

        eff = Efficiency('efficiency_noCategories', None, None, f, subdirs = ['efficiency_noCategories', 'l1_r_l2_e_l3_g'])
        h = eff.getEfficiency()

        p = Plot(h, 'V_{'+args.flavor+'N} = 0.01', 'efficiency', h.GetXaxis().GetTitle(), h.GetYaxis().GetTitle(), x_log=True, color_palette = 'Black')
        p.drawHist(output_dir = output_dir, draw_option = 'EP')



#         dict_of_categories = {}
#         dict_of_names = {}
#         for category in CATEGORIES:
#             dict_of_categories[category] = []
#             dict_of_names[category] = []
    
#         rf = ROOT.TFile(f)
#         if args.triggerTest or args.cumulativeCuts:    get_nested = True
#         else:                   get_nested = False

#         keyNames = [k[0] for k in rootFileContent(rf, getNested=get_nested)]
#         used_names  = []

#         for k in keyNames:
#             k = k.rsplit('_', 1)[0]
#             if k in used_names: continue
#             used_names.append(k)

#             c = getCategory(k, args.triggerTest)
#             if args.triggerTest or args.cumulativeCuts:
#                 cuts = getCuts(k)
#                 #obj_name = k +'/efficiency_'+str(c[0])+'_'+str(c[1])+'_l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2]) 
#                 obj_name = k
#                 dict_of_names[c].append('l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2]))
#             else: 
#                 obj_name = k+k

#             eff = Efficiency(obj_name.split('/')[-1], None, None, f, subdirs = obj_name.split('/')[1:-1])
#             h = eff.getEfficiency()            
# #            h = getObjFromFile(f, obj_name+'_num').Clone(obj_name.split('/')[2]+'_efficiency')
# #            h.Divide(h, getObjFromFile(f, obj_name+'_denom'), 1, 1, 'B')

#             dict_of_categories[c].append(h.Clone('h'))

#             extra_text = [extraTextFormat(returnTexName(c), ypos = 0.83)] if c is not None else None

#             if args.triggerTest: 
#                 cut_info = ''
#                 for i, l in enumerate(cuts):
#                     if l is not None:
#                         cut_info += 'p_{T}(l'+str(i+1)+') < '+str(l) +' GeV ; '
#                 if extra_text is not None:
#                     extra_text.append(extraTextFormat(cut_info))
            
#             elif args.divideByCategory and not args.cumulativeCuts:
#                 list_of_cuts = returnCategoryPtCuts(c)
#                 for j, cut in enumerate(list_of_cuts):
#                     cut_info = ''
#                     for i, l in enumerate(cut):
#                         if l is not None:
#                             cut_info += 'p_{T}(l'+str(i+1)+') < '+str(l) +' GeV ; '
#                     if extra_text is not None:
#                         extra_text.append(extraTextFormat(cut_info, textsize = 0.02))
#                         if j < len(list_of_cuts) - 1: extra_text.append(extraTextFormat('OR', textsize=0.02))
            
#             if not args.cumulativeCuts:
#                 p = Plot(h, sample, obj_name.split('/')[2], h.GetXaxis().GetTitle(), h.GetYaxis().GetTitle(), extra_text=extra_text, y_log=True)
#                 if args.triggerTest:
#                     p.drawHist(output_dir = output_dir +'/'+obj_name.split('/')[1])
#                 else:
#                     p.drawHist(output_dir = output_dir, draw_option = 'EHistText')

#         if args.cumulativeCuts:
#             for cat in dict_of_categories.keys():
#                 extra_text = [extraTextFormat(returnTexName(cat), ypos = 0.83)] if c is not None else None
#                 p = Plot(dict_of_categories[cat], dict_of_names[cat], 'cat_'+str(cat[0]) + '_'+str(cat[1]), h.GetXaxis().GetTitle(), 'Efficiency', extra_text=extra_text)
#                 p.drawHist(output_dir = output_dir, draw_option = 'EHist')
            
                
