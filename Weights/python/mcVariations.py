base_path_hcounters = lambda era, year : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'hcounters', era+year))

class MCVariation(object):
    
    def __init__(self, var_name, branch_name, counter_name, indices, sample):
        self.branch_name = branch_name
        self.indices = indices
        self.var_name = var_name
        self.total_hcount = self.getRelevantCount('hCounter')
        self.total_newcount = self.getRelevantCount(counter_name)

    def returnBranches(self):
        return ['{0}[{1}]/F'.format(self.var_name, len(self.indices))]

    def getRelevantCount(counter_name, sample_name)
        counter = open(base_path_counters(era, year), counter_name+'.json')),)
        counter_weights = json.load(counter)
        total_count = counter_weights[sample_name]
        counter.close()
        return total_count

    def getCounterRatio(self, index):
        return self.total_hcount/self.total_newcount[index]
       
    def getVariedWeights(self, chain):
        out_weights = []
        for index in indices:
            out_weights.append(getattr(chain, self.branch_name)[index]*self.getCounterRatio(index))
        setattr(chain, var_name, out_weights)
       

class MEScaleVariation(MCVariation):
    
    #relativeWeight_MuR_1_MuF_1  === 0
    #relativeWeight_MuR_1_MuF_2  === 1          NEED
    #relativeWeight_MuR_1_MuF_0p5  === 2        NEED
    #relativeWeight_MuR_2_MuF_1  === 3          NEED
    #relativeWeight_MuR_2_MuF_2  === 4          NEED
    #relativeWeight_MuR_2_MuF_0p5  === 5
    #relativeWeight_MuR_0p5_MuF_1  === 6        NEED
    #relativeWeight_MuR_0p5_MuF_2  === 7
    #relativeWeight_MuR_0p5_MuF_0p5  === 8      NEED

    def __init__(self, sample):
        super(MEScaleVariation, self).__init__('MEscale', '_lheWeight', 'lheCounter', [1, 2, 3, 4, 6, 8], sample)

class PDFVariation(MCVariation):
    
    #relativeWeight_MuR_1_MuF_1  === 0
    #relativeWeight_MuR_1_MuF_2  === 1          NEED
    #relativeWeight_MuR_1_MuF_0p5  === 2        NEED
    #relativeWeight_MuR_2_MuF_1  === 3          NEED
    #relativeWeight_MuR_2_MuF_2  === 4          NEED
    #relativeWeight_MuR_2_MuF_0p5  === 5
    #relativeWeight_MuR_0p5_MuF_1  === 6        NEED
    #relativeWeight_MuR_0p5_MuF_2  === 7
    #relativeWeight_MuR_0p5_MuF_0p5  === 8      NEED

    def __init__(self, sample):
        super(MEScaleVariation, self).__init__('PDF', '_lheWeight', 'lheCounter', [], sample)

class PSVariation(MCVariation):
    
    #relativeWeight_MuR_1_MuF_1  === 0
    #relativeWeight_MuR_1_MuF_2  === 1          NEED
    #relativeWeight_MuR_1_MuF_0p5  === 2        NEED
    #relativeWeight_MuR_2_MuF_1  === 3          NEED
    #relativeWeight_MuR_2_MuF_2  === 4          NEED
    #relativeWeight_MuR_2_MuF_0p5  === 5
    #relativeWeight_MuR_0p5_MuF_1  === 6        NEED
    #relativeWeight_MuR_0p5_MuF_2  === 7
    #relativeWeight_MuR_0p5_MuF_0p5  === 8      NEED

    def __init__(self, sample):
        super(PSVariation, self).__init__('partonShower', '_psWeight', 'psCounter', [], sample)
