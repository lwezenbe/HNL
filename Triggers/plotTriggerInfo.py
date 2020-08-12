from HNL.Tools.mergeFiles import merge
import os
import glob
import time
from HNL.Tools.helpers import makePathTimeStamped, makeDirIfNeeded

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--ignoreCategories', action='store_true', default=False,  help='do not split the events in different categories')
argParser.add_argument('--separateTriggers', action='store', default=None,  
    help='Look at each trigger separately for each category. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
argParser.add_argument('--signalMass', action='store', default=None,  help='Only look at sample with specific mass')
args = argParser.parse_args()

if args.separateTriggers is None:       args.separateTriggers = ''

#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/calcTriggerEff/*/'+args.separateTriggers)
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)

input_files = glob.glob(os.getcwd()+'/data/calcTriggerEff/*/'+args.separateTriggers+'/*.root')
sample_names = {in_file_name.split('/')[-3] for in_file_name in input_files}
print sample_names
f_names = {f.split('/')[-1].split('.')[0] for f in input_files}

#Prepare output dir
timestamp = time.strftime("%Y%m%d_%H%M%S")
for f_name in f_names:
    out_dir = os.getcwd()+'/data/Results/'+args.separateTriggers+'/'+f_name+'/'+timestamp
    makeDirIfNeeded(out_dir+'/x')



# def isUniqueElement(l, item):
#     list_of_truths = [e == item for e in l]
#     return not any(list_of_truths)

import ROOT
from HNL.Tools.helpers import rootFileContent, getObjFromFile
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat
from HNL.EventSelection.eventCategorization import CATEGORIES, CATEGORY_TEX_NAMES, returnCategoryTriggerNames, TRIGGER_CATEGORIES
from HNL.Tools.efficiency import Efficiency

# #TODO: Can this be made general?
# def makeNameCompList(name_list):
    
#     comp_list = {}

#     for n in name_list:
#         name = n.split('/')[1]
#         comp_list[name] = {}
#         for n2 in name_list:
#             if name not in n2: continue
#             name_2 = n2.split('/')[2]
#             comp_list[name][name_2] = {}
#             for n3 in name_list:
#                 if name not in n3: continue
#                 if name_2 not in n3: continue
#                 name_3 = n3.split('/')[3]
#                 comp_list[name][name_2][name_3] = n3.split('/')[4]
    
#     return comp_list      

# def getCategory(name, trigger_test = False, super_cat = False):
#     split_name = name.split('_')
#     try:
#         if super_cat: 
#             return int(split_name[1])
#         else:
#             return (int(split_name[1].split(',')[0].split('(')[1]), int(split_name[1].split(',')[0].split('(')[1]))
#     except:
#         return None


def mergeEfficiencies(input_eff, out_name):
    #
    # Check if they all have the same var and triggers
    #

    #
    # merge
    #
    new_eff_list = {}
    for v in input_eff[0].keys():
        new_eff_list[v] = [eff.clone(out_name) for eff in input_eff[0][v]]
        for rem in xrange(1, len(input_eff)):
            for i in xrange(len(new_eff_list[v])):
                new_eff_list[v][i].add(input_eff[rem][v][i])
    return new_eff_list

if args.ignoreCategories:
    cat_names = ['inclusive']
else:
    cat_names = CATEGORIES

for sample in sample_names:
    if sample != 'HNLmass': continue
    base_dir = os.getcwd()+'/data/calcTriggerEff/'+sample+'/'+args.separateTriggers
    sub_files = glob.glob(base_dir +'/*.root')
    for sub_f in sub_files:
        f_name = sub_f.split('/')[-1].split('.')[0]
        rf = ROOT.TFile(sub_f)
        eff_lists = {}
        for cat in cat_names:
            eff_lists[cat] = {}
            extra_text = [extraTextFormat(CATEGORY_TEX_NAMES[cat], ypos = 0.83)] if cat is not None else None
            var = [k[0].split('/')[-1] for k in rootFileContent(rf, starting_dir = 'efficiency_'+str(cat))]
            for v in var:
                if args.separateTriggers is None or args.separateTriggers == 'full':
                    trigger_list = ['allTriggers']
                else:
                    trigger_list = returnCategoryTriggerNames(cat)
                eff_lists[cat][v] = [Efficiency('_'.join([str(cat), v, 'integral', str(i)]), None, None, sub_f, subdirs = ['efficiency_'+str(cat), v, t]) for i, t in enumerate(trigger_list)]
        rf.Close()

        if not args.ignoreCategories:
            for trigger_cat_name in sorted(TRIGGER_CATEGORIES.keys()):
                to_merge = [eff_lists[c] for c in TRIGGER_CATEGORIES[trigger_cat_name]]
                eff_lists[trigger_cat_name] = mergeEfficiencies(to_merge, trigger_cat_name)

                for v in eff_lists[trigger_cat_name].keys():
                    eff_list = [eff.getEfficiency() for eff in eff_lists[trigger_cat_name][v]]
                    if args.separateTriggers is None or args.separateTriggers == 'full':
                        trigger_list = ['allTriggers']
                    else:
                        trigger_list = returnCategoryTriggerNames(TRIGGER_CATEGORIES[trigger_cat_name][0])

                    if args.separateTriggers == 'cumulative':
                        out_dir = os.getcwd()+'/data/Results/'+args.separateTriggers+'/'+f_name+'/'+timestamp
                        p = Plot(eff_list, trigger_list, trigger_cat_name+'_'+v, eff_list[0].GetXaxis().GetTitle(), eff_list[0].GetYaxis().GetTitle(), extra_text=extra_text)
                        names = [trigger_cat_name+'_'+v+'_'+k for k in trigger_list]
                        if '2D' in v:
                            p.draw2D(output_dir = out_dir+'/'+sample, names = names) 
                        else:          
                            p.drawHist(output_dir = out_dir+'/'+sample) 
        else:
            to_merge = [eff_list[c] for c in CATEGORIES]
            eff_lists['all'] = mergeEfficiencies(to_merge, 'all')

            for v in eff_lists['all'].keys():
                eff_list = [eff.getEfficiency() for eff in eff_lists['all'][v]]
                out_dir = os.getcwd()+'/data/Results/'+str(args.separateTriggers)+'/'+f_name+'/'+timestamp
                p = Plot(eff_list, trigger_list, v, eff_list[0].GetXaxis().GetTitle(), eff_list[0].GetYaxis().GetTitle(), extra_text=extra_text)
                if '2D' in v:
                    p.draw2D(output_dir = out_dir+'/'+sample) 
                else:          
                    p.drawHist(output_dir = out_dir+'/'+sample)            

            

exit(0)

for f_name in f_names:

    output_dir = makePathTimeStamped(os.getcwd()+'/data/Results/'+args.separateTriggers+'/'+f_name)
    hists = {}
    keyNames = []
    sub_files = glob.glob(os.getcwd()+'/data/calcTriggerEff/*/'+args.separateTriggers +'/' +f_name+'.root')

    hists = {}
    file_name_comp = {}
    print 'plotting', f_name
    for f in sub_files:
        split_f = f.split('/')
        sample = split_f[split_f.index('calcTriggerEff')+1]
        if args.signalMass and not args.signalMass in sample: continue       
 
#        if sample != 'HNLmass': continue
        rf = ROOT.TFile(f)
        
        get_nested = False
        if args.separateTriggers == 'single' or args.separateTriggers == 'cumulative': 
            get_nested = True

        keyNames = [k[0] for k in rootFileContent(rf, getNested = get_nested)]
        filtered_names = {k.rsplit('_', 1)[0] for k in keyNames}
        
        file_name_comp[sample] = makeNameCompList([x for x in filtered_names])

        hists[sample] = {}

        for c in file_name_comp[sample].keys():
            hists[sample][c] = {}
            for v in file_name_comp[sample][c].keys():
                hists[sample][c][v] = {}
                if args.separateTriggers is None:
                    obj_name = file_name_comp[sample][c][v]['allTriggers']
                    hists[sample][c][v]['allTriggers'] = getObjFromFile(f, '/'+c+'/'+v+'/'+obj_name+'_num').Clone(c+'/'+v+'/'+obj_name+'_efficiency')
                    hists[sample][c][v]['allTriggers'].Divide(getObjFromFile(f, c+'/'+v+'/'+obj_names[0]+'_denom'))
                else:
                    for t in file_name_comp[sample][c][v]:
                        eff = Efficiency(file_name_comp[sample][c][v][t], None, None, f, subdirs = [c, v, t])
                        if not '2D' in v:
                            hists[sample][c][v][t] = eff.getEfficiency()
                        else:
                            hists[sample][c][v][t] = eff.getEfficiency()

                        #hists[sample][c][v][t] = getObjFromFile(f, c+'/'+v+'/'+t+'/'+ file_name_comp[sample][c][v][t]+'_num').Clone(c+'/'+v+'/'+t+'_efficiency')            
                        #hists[sample][c][v][t].Divide(getObjFromFile(f, c+'/'+v+'/'+t+'/'+ file_name_comp[sample][c][v][t]+'_denom'))  

        #After getting all hists, start plotting
        # HNL mass
#        HNL_mass_hists = [hists[sample] for sample in file_name_comp.keys()  if sample == 'HNLmass']
#        for c in file_name_comp[sample].keys():
#            for v in file_name_comp[sample][c].keys():
#                p = Plot(HNL_mass_hists[c][v], [t for t in HNL_mass_hists[c][v].keys()], c+'_'+v, HNL_mass_hists[c][v].GetXaxis().GetTitle(), HNL_mass_hists[c][v].GetYaxis().GetTitle() )          
#                p.drawHist(output_dir = output_dir)

        #Variables        
        for c in file_name_comp[sample].keys():
            cat = getCategory(c, super_cat = True)
            extra_text = [extraTextFormat(returnTexName(cat), ypos = 0.83)] if cat is not None else None

            for v in file_name_comp[sample][c].keys():
                triggers = [t for t in hists[sample][c][v].keys()]
                if not '2D' in v:
                    p = Plot([hists[sample][c][v][t] for t in triggers], triggers, c+'_'+v, hists[sample][c][v][triggers[0]].GetXaxis().GetTitle(), 
                        hists[sample][c][v][triggers[0]].GetYaxis().GetTitle(), extra_text = extra_text)  
                    p.drawHist(output_dir = output_dir+'/'+sample, draw_option = "EHist")
                for t in triggers:
                    p = Plot(hists[sample][c][v][t], triggers, c+'_'+v+'_'+t, hists[sample][c][v][t].GetXaxis().GetTitle(), 
                        hists[sample][c][v][t].GetYaxis().GetTitle(), extra_text=extra_text)          
                    if '2D' in v:
                        p.draw2D(output_dir = output_dir+'/'+sample)
                    else:
                        p.drawHist(output_dir = output_dir+'/'+sample)

   
    if args.separateTriggers is None:
        sub_h = {}
        sub_h_names = [] 
        for s in file_name_comp.keys():
            sub_h_names.append(s)
            for c in file_name_comp[s].keys():
                sub_h[c] = {}
                for v in file_name_comp[s][c].keys():
                    if v not in sub_h[c].keys():
                        sub_h[c][v] = [hists[sample][c][v]['allTriggers']]
                    else:
                        sub_h[c][v].append(hists[sample][c][v]['allTriggers'])
        for c in sub_h.keys():
            cat = getCategory(c, super_cat = True)
            extra_text = [extraTextFormat(returnTexName(cat), ypos = 0.83)] if c is not None else None
            for v in sub_h[c].keys():
                p = Plot(sub_h[c][v], sub_h_names, c+'_'+v, sub_h[c][v].GetXaxis().GetTitle(), sub_h.GetYaxis().GetTitle(), extra_text=extra_text)          
                p.drawHist(output_dir = output_dir) 
        
    
#        samples.append(sample)
#        rf = ROOT.TFile(f)
#        
#        get_nested = False
#        if args.separateTriggers == 'single' or args.separateTriggers == 'cumulative': 
#            get_nested = True
#
#        keyNames = [k[0] for k in rootFileContent(rf, getNested = get_nested)]
#        filtered_names = {k.rsplit('_', 1)[0] for k in keyNames}
#        for k in filtered_names:
#
#            h = getObjFromFile(f, k+'_num').Clone(k.split('/')[1]+'_efficiency')
#            h.Divide(getObjFromFile(f, k+'_denom'))
#            if '2D' in k:
#                p = Plot(h, samples, k.split('/')[1], h.GetXaxis().GetTitle(), h.GetYaxis().GetTitle())
#                p.draw2D(output_dir = output_dir+'/'+sample)
#            else:
#                if 'HNLmass' in k: continue
#                try:
#                    hists[k].append(h)
#                except:
#                    hists[k] = [h]
#
#    for k in filtered_names:
#        if '2D' in k:       continue
#            
#        p = Plot(hists[k], samples, k.split('/')[1], hists[k][0].GetXaxis().GetTitle(), hists[k][0].GetYaxis().GetTitle() )
#        p.drawHist(output_dir = output_dir)
#        
