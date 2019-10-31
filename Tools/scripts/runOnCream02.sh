#!/bin/bash
log(){
python -c "import logging;logging.basicConfig(level = logging.INFO);logging.info('$1')"
}

PYTHONUNBUFFERED=TRUE
cd $dir
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scram runtime -sh`
export X509_USER_PROXY=/user/$USER/x509up_u$(id -u $USER) 
./$command
