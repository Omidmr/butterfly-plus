# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Load results for a field in probes.

-

    Args:
        _solution: Butterfly Solution, Case or fullpath to the case folder.
        _field: Probes' filed as a string (e.g. p, U).
        
    Returns:
        skippedPoints: List of points that are skipped during the solution.
        values: List of values for the last timestep.
"""

ghenv.Component.Name = "Butterfly_Load Probes Value"
ghenv.Component.NickName = "loadProbesValue"
ghenv.Component.Message = 'VER 0.0.04\nNOV_19_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "07::PostProcess"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from butterfly.utilities import load_probe_values_from_folder
    from butterfly_grasshopper.geometry import xyz_to_vector
except ImportError as e:
    msg = '\nFailed to import butterfly:'
    raise ImportError('{}\n{}'.format(msg, e))

import os


if _solution and _field:
    if isinstance(_solution, str):
        projectDir = _solution.replace('\\\\','/').replace('\\','/')
        probesDir = os.path.join(projectDir, 'postProcessing\\probes') 
        rawValues = load_probe_values_from_folder(probesDir, _field)
    else:
        assert hasattr(_solution, 'load_probe_values'), \
            'Invalid Input: <{}> is not a valid Butterfly Solution.'.format(_solution)
        try:
            rawValues = _solution.load_probe_values(_field)
        except Exception as e:
            raise ValueError('Failed to load values:\n\t{}'.format(e))
            
    try:
        values = tuple(xyz_to_vector(v) for v in rawValues)
    except:
        values = rawValues
