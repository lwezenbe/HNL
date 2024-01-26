nuisances = {
    "luminosity"        :       "lumi",
    "theory"            :       "theo",
    "trigger"           :       "trig",
    "WZ_norm"           :       "WZ",
    "ZZ_norm"           :       "ZZ",
    "conv_norm"         :       "conv",
    "prompt_norm"        :      "promptother",
    "nonprompt_light"   :       "nonpromptlight",
    "nonprompt_tau"     :       "nonprompttau",
    "electron"          :       "e",
    "muon"              :       "mu",
    "tau"               :       "tau",
    "jets"              :       "jets",
}

order_of_nuisances= ['nonprompt_tau', 'tau', 'nonprompt_light', 'WZ_norm', 'ZZ_norm', 'conv_norm', 'prompt_norm', 'trigger', 'luminosity', 'theory', 'electron', 'muon', "jets"]

def printFunction():
    input_string = order_of_nuisances[0]
    name_string = nuisances[order_of_nuisances[0]]
    
    scan_command = lambda i, n : "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups {0} -n hnl.freeze_{1}; ".format(i, n)
    
    print 'command += "{0}"'.format(scan_command(input_string, name_string))
    for o in order_of_nuisances[1:]:
        input_string += ","+o
        name_string += "_"+nuisances[o]

        print 'command += "{0}"'.format(scan_command(input_string, name_string))

    print ''
    print "command += 'plot1DScan.py higgsCombineTest.MultiDimFit.mH120.root --main-label Total Uncert. --POI r --others'"

    name_string = nuisances[order_of_nuisances[0]]
    output_string = nuisances[order_of_nuisances[0]]
    print "command += ' higgsCombinehnl.freeze_{0}.MultiDimFit.mH120.root:freeze {0}:{1}'".format(name_string, len(order_of_nuisances))
    for i, o in enumerate(order_of_nuisances[1:]):
        name_string += "_"+nuisances[o]
        output_string += ","+nuisances[o]
        print "command += ' higgsCombinehnl.freeze_{0}.MultiDimFit.mH120.root:freeze {0}:{1}'".format(name_string, len(order_of_nuisances)-i-1)

    print "command += ' --output breakdown --y-max 10 --y-cut 40 --breakdown {0},stat'".format(output_string)

printFunction()
