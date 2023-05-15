#
# Code to make final hepdata record
#

out_path = '/user/lwezenbe/public_html/HEPData/EXO-22-011'
import os
os.system('rm -rf /user/lwezenbe/public_html/HEPData/EXO-22-011')
from HNL.Tools.helpers import makeDirIfNeeded
makeDirIfNeeded(out_path+'/submission')

from hepdata_lib import Submission
submission = Submission()

from HNL.HEPData.createLimits import addFiguresTo
addFiguresTo(submission)

from HNL.HEPData.createYields import addAllYieldTables
addAllYieldTables(submission)

submission.create_files(out_path+'/submission')
os.system('mv submission.tar.gz {0}/.'.format(out_path))
