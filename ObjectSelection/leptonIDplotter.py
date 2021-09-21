from HNL.Plotting.plot import Plot, makeList
from HNL.Plotting.plottingTools import extraTextFormat
import os

class LeptonIDplotter:

    def __init__(self, signal, background, flavor, in_path_base_function):
        self.signal = signal
        self.background = background
        self.flavor = flavor
        self.in_path_base_function = in_path_base_function

    def getPath(self, year, era, algo, process):
        return self.in_path_base_function(era, year, process) + '/' + '-'.join([algo, 'ROC', self.flavor])+'.root'

    def plotROC(self, list_of_years, list_of_eras, list_of_algos):
        list_of_years = makeList(list_of_years)
        list_of_eras = makeList(list_of_eras)

        from HNL.Tools.ROC import ROC
        curves = []
        ordered_f_names = []
        for year in list_of_years:
            for era in list_of_eras:
                for algo in list_of_algos:
                    curves.append(ROC(algo, self.getPath(year, era, algo, self.signal), misid_path =self.getPath(year, era, algo, self.background)).returnGraph())
                    ordered_f_names.append(algo +' ('+era+ ' ' +year+')')

        extra_text = [extraTextFormat('efficiency: '+self.signal, xpos = 0.2, ypos = 0.82, textsize = 1.2, align = 12)]  #Text to display event type in plot
        extra_text.append(extraTextFormat('misid: '+self.background, textsize = 1.2, align = 12))  #Text to display event type in plot

        p = Plot(curves, ordered_f_names, self.signal+'_'+self.flavor, 'efficiency', 'misid', y_log=True, extra_text=extra_text)
        p.drawGraph(output_dir = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'ObjectSelection', 'data', 'Results', 'compareLeptonId', 'ROC', self.signal+'-'+self.background)))

    def getAlgosAndWorkingPoints(self, file_name):
        from ROOT import TFile
        from HNL.Tools.helpers import rootFileContent

        algos = {}
        rf = TFile(file_name)
        key_names = [k[0] for k in rootFileContent(rf)]
        for kn in key_names:
            algo, wp = kn.split('/')[-1].rsplit('-', 1)
            if algo in algos.keys(): 
                algos[algo].append(wp)
            else:
                algos[algo] = [wp]

        return algos
    
    def plotEfficiencies(self, list_of_years, list_of_eras, list_of_algos, list_of_workingpoints = None):
        from HNL.Tools.efficiency import Efficiency
        var = ['pt', 'eta']
        list_of_years = makeList(list_of_years)
        list_of_eras = makeList(list_of_eras)

        get_working_points = list_of_workingpoints is None

        efficiencies = {'efficiency': {}, 'fakerate': {}}
        for eff_name in efficiencies.keys():
            for year in list_of_years:
                efficiencies[eff_name][year] = {}
                for era in list_of_eras:
                    efficiencies[eff_name][year][era] = {}
                    f = self.in_path_base_function(era, year, self.signal)+'/'+eff_name+'-'+str(self.flavor)+'.root'
                    if get_working_points: algos = self.getAlgosAndWorkingPoints(f)
                    for algo in list_of_algos:
                        efficiencies[eff_name][year][era][algo] = {}
                        if get_working_points: list_of_workingpoints = algos[algo]
                        for wp in list_of_workingpoints:
                            efficiencies[eff_name][year][era][algo][wp] = {}
                            for v in var:
                                efficiencies[eff_name][year][era][algo][wp][v] = Efficiency(eff_name+'_'+v, None, None, f, subdirs = [algo+'-'+wp, eff_name+'_'+v])

        if get_working_points:    
            all_wp = set()    
            for wps in algos.values():
                for wp in wps:
                    all_wp.add(wp)
            
            for eff_name in efficiencies.keys():
                for v in var:
                    for wp in all_wp:
                        all_hist = []
                        all_names = []
                        for year in list_of_years:
                            for era in list_of_eras:
                                for algo in list_of_algos:
                                    if wp not in algos[algo]:   continue
                                    all_hist.append(efficiencies[eff_name][year][era][algo][wp][v].getEfficiency())
                                    all_names.append(algo +' ('+era+ ' ' +year+')')

                        p = Plot(all_hist, all_names,  wp+'_'+eff_name+'_'+self.flavor+'_'+v)
                        p.drawHist(output_dir = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'ObjectSelection', 'data', 'Results', 'compareLeptonId', eff_name, self.signal+'-'+self.background)), draw_option = 'Hist')
        else:
            for eff_name in efficiencies.keys():
                for v in var:
                    all_hist = []
                    all_names = []
                    for year in list_of_years:
                        for era in list_of_eras:
                            for algo in list_of_algos:
                                for wp in algos[algo]:  
                                    all_hist.append(efficiencies[eff_name][year][era][algo][wp][v].getEfficiency())
                                    all_names.append(wp + ' ' + algo +' ('+era+ ' ' +year+')')

                p = Plot(all_hist, all_names,  eff_name+'_'+self.flavor+'_'+v)
                p.drawHist(output_dir = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'ObjectSelection', 'data', 'Results', 'compareLeptonId', eff_name, self.signal+'-'+self.background)), draw_option = 'Hist')



            # for fk in filtered_key_names: #algo
            #     for v in var:
            #         bkgr_hist = getObjFromFile(f, fk+'-'+k+'/'+eff_name+'_'+v+'/'+eff_name+'_'+v+'_denom')
            #         tmp_list = [list_of_eff[fk][i][v] for i in list_of_eff[fk].keys()]
            #         scale_factor = 0.25 if v == 'pt' else 1.
            #         bkgr_hist.Scale(scale_factor*tmp_list[0].getEfficiency().GetSumOfWeights()/bkgr_hist.GetSumOfWeights())
            #         p = Plot([efficiency.getEfficiency() for efficiency in tmp_list], [i+' '+fk for i in list_of_eff[fk].keys()]+['lepton distribution']
            #                 ,  eff_name+'_'+args.flavor+'_'+v, bkgr_hist = bkgr_hist)
            #         p.drawHist(output_dir = os.getcwd()+'/data/Results/compareLightLeptonId/'+fk+'/var/'+sample, draw_option = 'Hist')

if __name__ == '__main__':
    import os, argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--years',     action='store', nargs='*',     default=None,   help='Select year')
    argParser.add_argument('--eras',     action='store', nargs='*',      default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
    argParser.add_argument('--flavor', default=None,  help='flavor of lepton under consideration.', choices = ['e', 'mu', 'tau'])
    argParser.add_argument('--signal', action='store', default='DY',  help='signal to use in plots')
    argParser.add_argument('--bkgr', action='store', default='DY',  help='background to use in plots')
    args = argParser.parse_args()

    def getOutputBase(era, year, sample_name):
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'compareLeptonId', era+year, args.flavor)
        output_name = os.path.join(output_name, sample_name)
        return output_name

    lid = LeptonIDplotter(args.signal, args.bkgr, args.flavor, getOutputBase)

    lid.plotROC(args.years, args.eras, ['cutbased', 'HNL'])
    # lid.plotEfficiencies(args.years, args.eras, ['cutbased', 'HNL'])
    lid.plotEfficiencies(args.years, args.eras, ['leptonMVAtop'])


