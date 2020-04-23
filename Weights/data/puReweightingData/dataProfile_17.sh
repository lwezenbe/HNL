#!/bin/sh

PILEUP_LATEST=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt
JSON=Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt
LUMI=41500

# pileupCalc.py is broken in recent CMSSW releases, this is a sad workaround
# change the path to whatever old release you have available
pwd=$PWD
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /user/$USER/CMSSW_9_4_10/src/
eval `scram runtime -sh`
cd $pwd

if [ ! -f "$PILEUP_LATEST" ]; then
   echo "File $PILEUP_LATEST does not exist on this site, copying from lxplus"
   scp $USER@lxplus.cern.ch:$PILEUP_LATEST pileup_latest.txt
   PILEUP_LATEST=pileup_latest.txt
fi

pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 66017 --maxPileupBin 100 --numPileupBins 100 PU_2017_${LUMI}_XSecDown.root
pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 69200 --maxPileupBin 100 --numPileupBins 100 PU_2017_${LUMI}_XSecCentral.root
pileupCalc.py -i $JSON --inputLumiJSON $PILEUP_LATEST --calcMode true --minBiasXsec 72383 --maxPileupBin 100 --numPileupBins 100 PU_2017_${LUMI}_XSecUp.root

eval `scram runtime -sh`