def addCommonQualifiersTo(variable, lumi=True):
    variable.add_qualifier("SQRT(S)", 13, "TeV")
    if lumi:
        variable.add_qualifier("LUMINOSITY", 138, "fb$^{-1}$")

def addCommonKeywordsTo(table):
    table.keywords["reactions"] = ["P P --> LEPTON HNL --> LEPTON LEPTON LEPTON NU"]
    table.keywords["cmenergies"] = [13000.0]
    table.keywords["phrases"] = []

