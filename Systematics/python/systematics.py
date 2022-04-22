


class Systematics:
    DICT_OF_FLATUNCERTAINTIES = {
        'nonprompt_tau' : 1.3,
        'nonprompt_lightlep' : 1.3,
        'luminosity' : 1.025
    }
    LIST_OF_WEIGHTSYSTEMATICS = ['puWeight', 'tauSFWeight', 'electronRecoWeight', 'btagWeight']
    LIST_OF_RERUNSYSTEMATICS = ['tauEnergyScale']
    LIST_OF_SYSTEMATICS = LIST_OF_WEIGHTSYSTEMATICS + LIST_OF_RERUNSYSTEMATICS + DICT_OF_FLATUNCERTAINTIES.keys()

    def __init__(self, sample, reweighter):
        self.sample = sample
        self.chain = self.sample.chain
        self.reweighter = reweighter

    def returnBranches(self):
        branches = []
        for syst in self.LIST_OF_SYSTEMATICS:
            branches.append('{0}Up/F'.format(syst))
            branches.append('{0}UpRaw/F'.format(syst))
            branches.append('{0}Down/F'.format(syst))
            branches.append('{0}DownRaw/F'.format(syst))
        return branches

    def getWeightSystematics(self, weight):
        weight_up = self.reweighter.returnWeight(weight, syst='up')
        weight_down = self.reweighter.returnWeight(weight, syst='down')
        return weight_up, weight_down

    def storeFullWeightSystematics(self, weight, output_tree):
        weight_up, weight_down = self.getWeightSystematics(weight)
        output_tree.setTreeVariable('{0}UpRaw'.format(weight), weight_up)
        output_tree.setTreeVariable('{0}DownRaw'.format(weight), weight_down)
        for original_weight in self.reweighter.WEIGHTS_TO_USE:
            if original_weight == weight: continue
            weight_up *= getattr(output_tree.tree, original_weight)
            weight_down *= getattr(output_tree.tree, original_weight)
        output_tree.setTreeVariable('{0}Up'.format(weight), weight_up)
        output_tree.setTreeVariable('{0}Down'.format(weight), weight_down)

    def storeAllSystematicsForShapes(self, output_tree):
        for syst in self.LIST_OF_SYSTEMATICS:
            if syst in self.reweighter.WEIGHTS_TO_USE:
                self.storeFullWeightSystematics(syst, output_tree)   

