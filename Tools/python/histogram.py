import ROOT

#
# Custom histogram class
#

class Histogram:
   
    #
    # Either make a histogram from scratch. I this case the args should be: name, var, var_tex and bins
    # Or load in an existing histogram and make properties more accessible. I this case: args = hist
    #    
 
    def __init__(self, *args, **overflow):

        if len(args) == 1 and (isinstance(args[0], ROOT.TH1) or isinstance(args[0], ROOT.TH2)):
            self.hist = args[0]
            self.name = self.hist.GetName()
            self.var = None             #Temporary, will not need it in this case yet and dont know how to deal with it yet
            self.var_tex = (self.hist.GetXaxis().GetTitle(), self.hist.GetYaxis().GetTitle())
            self.bins = None            #Temporary, will not need it in this case yet and dont know how to deal with it yet
            self.isTH2 = isinstance(self.hist, ROOT.TH2)
        elif len(args) == 4:
            self.name = args[0]
            self.var = args[1]
            self.var_tex = args[2]
            self.bins = args[3]
            self.isTH2 = isinstance(self.bins, (tuple,))
            self.hist = None      

            if self.isTH2:
                self.hist = ROOT.TH2D(self.name, self.name, len(self.bins[0])-1, self.bins[0], len(self.bins[1])-1, self.bins[1])
                self.hist.Sumw2()
            else:
                self.hist = ROOT.TH1D(self.name, self.name, len(self.bins)-1, self.bins)
                self.hist.Sumw2()
            self.hist.SetXTitle(self.var_tex[0])
            self.hist.SetYTitle(self.var_tex[1])
        else:
            print "Incorrect input for Histogram"
            exit(0)
        
        try:
            self.overflow = overflow['overflow']
        except:
            self.overflow = True

    def fill1D(self, chain, weight, index = None):
        if index is not None:
            var = self.var(chain, index)
        else:
            var = self.var(chain)
        if self.overflow: xval = min(max(self.hist.GetXaxis().GetBinCenter(1), var), self.hist.GetXaxis().GetBinCenter(self.hist.GetXaxis().GetLast()))
        else: xval = var
        self.hist.Fill(xval, weight)

    def fill2D(self, chain, weight):
        if self.overflow:
            xval = min(max(self.hist.GetXaxis().GetBinCenter(1), self.var(chain)[0]), self.hist.GetXaxis().GetBinCenter(self.hist.GetXaxis().GetLast()))
            yval = min(max(self.hist.GetYaxis().GetBinCenter(1), self.var(chain)[1]), self.hist.GetYaxis().GetBinCenter(self.hist.GetYaxis().GetLast()))
        else:
            xval = self.var(chain)[0]
            yval = self.var(chain)[1]

        self.hist.Fill(xval, yval, weight)

    def fill(self, chain, weight, index = None):
        if self.isTH2:
            self.fill2D(chain, weight)
        else:
            self.fill1D(chain, weight, index)

    def getXTitle(self):
        return self.var_tex[0]
    
    def getYTitle(self):
        return self.var_tex[1]

    def getHist(self):
        return self.hist
