# Butterfly: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Butterfly.
#
# You should have received a copy of the GNU General Public License
# along with Butterfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
snappyHexMesh

-

    Args:
        _case: Butterfly case.
        _locationInMesh_: A point 3d to locate the volume that should be meshed.
            By default center of the boundingbox will be used.
        _globRefineLevel_: A tuple of (min, max) values for global refinment.
            This value updates globalRefinementLevel in snappyHexMeshDict.
        _snappyHexMeshDict_: optional modified snappyHexMeshDict.
        decomposeParDict_: decomposeParDict for running snappyHexMesh in parallel.
        _write: Write changes to folder.        
        run_: run snappyHexMesh.
    Returns:
        readMe!: Reports, errors, warnings, etc.
        case: Butterfly case.
"""

ghenv.Component.Name = "Butterfly_snappyHexMesh"
ghenv.Component.NickName = "snappyHexMesh"
ghenv.Component.Message = 'VER 0.0.04\nDEC_10_2017'
ghenv.Component.Category = "Butterfly"
ghenv.Component.SubCategory = "03::Mesh"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


try:
    from butterfly.surfaceFeatureExtractDict import SurfaceFeatureExtractDict
except ImportError as e:
    msg = '\nFailed to import butterfly:'
    raise ImportError('{}\n{}'.format(msg, e))

if _case and _write:
    
    hasChanged = False
    
    if _snappyHexMeshDict_:
        assert hasattr(_snappyHexMeshDict_, 'isSolutionParameter'), \
            TypeError(
                '_snappyHexMeshDict_ input is {} and not a SolutionParameter.'
                .format(type(_snappyHexMeshDict_)))
        assert _snappyHexMeshDict_.filename == 'snappyHexMeshDict', \
            TypeError(
                '_snappyHexMeshDict_ input is prepared for {} and not snappyHexMeshDict'
                .format(_snappyHexMeshDict_.filename))
                
        # update values for snappyHexMeshDict
        hasChanged = _case.snappyHexMeshDict.update_values(_snappyHexMeshDict_.values)
        
        if 'snapControls' in _snappyHexMeshDict_.values:
            if _case.snappyHexMeshDict.extractFeaturesRefineLevel is not None :
                print 'updating snappyHexMeshDict for Explicit Edge Refinement.'
                # change to explicit mode
                _case.snappyHexMeshDict.set_featureEdgeRefinement_to_explicit(
                    _case.project_name,
                    _case.snappyHexMeshDict.extractFeaturesRefineLevel)
                hasChanged = True
        elif _case.snappyHexMeshDict.extractFeaturesRefineLevel is not None:
                print 'updating snappyHexMeshDict for Implicit Edge Refinement.'
                _case.snappyHexMeshDict.set_featureEdgeRefinement_to_implicit()
                hasChanged = True

    if _locationInMesh_:
        print('Updating locaionInMesh to {}.'.format(tuple(_locationInMesh_)))
        _case.snappyHexMeshDict.locationInMesh = tuple(_locationInMesh_)
    elif not _case.snappyHexMeshDict.locationInMesh:
        _case.snappyHexMeshDict.locationInMesh = _case.blockMeshDict.center    
        _case.snappyHexMeshDict.save(_case.project_dir)

    if _globRefineLevel_:
        print('Updating global refinement level to {}.'.format(
            tuple(int(v) for v in _globRefineLevel_)))
        _case.snappyHexMeshDict.globRefineLevel = tuple(_globRefineLevel_)
    else:
        # set refinement level back to (0, 0)
        if not _case.snappyHexMeshDict.globRefineLevel == (0, 0):
            print('Setting global refinement level back to (0 0).')
            _case.snappyHexMeshDict.globRefineLevel = (0, 0)
            _case.snappyHexMeshDict.save(_case.project_dir)
    
    # save snappyHexMeshDict if any change
    if hasChanged or _locationInMesh_ or _globRefineLevel_:
        print('saving the new snappyHexMeshDict.')
        _case.snappyHexMeshDict.save(_case.project_dir)

    # remove result folders if any
    _case.remove_result_folders()

    if decomposeParDict_:
        _case.decomposeParDict = decomposeParDict_
        _case.decomposeParDict.save(_case.project_dir)
    
    if not _case.snappyHexMeshDict.is_featureEdgeRefinement_implicit:
        sfe = SurfaceFeatureExtractDict.from_stl_file(_case.project_name,
                                                      includedAngle=150)
        sfe.save(_case.project_dir)
        if run_:
            log = _case.surfaceFeatureExtract()
            if not log.success:
                raise Exception("\n --> surfaceFeatureExtract Failed!\n%s" % log.error)
        else:
            print('TODO: add surfaceFeatureExtract to case command list.')

    if run_:
        if _case.is_polyMesh_snappyHexMesh:
            # check if meshBlock has been replaced by sHM
            # remove current snappyHexMesh and re-run block mesh
            _case.remove_snappyHexMesh_folders()
            # run blockMesh
            log = _case.blockMesh(overwrite=True)
        
            if not log.success:
                raise Exception("\n --> blockMesh Failed!\n%s" % log.error)     
        
        log = _case.snappyHexMesh()
        _case.remove_processor_folders()
        
        if log.success:
            if _case.get_snappyHexMesh_folders():
                _case.copy_snappyHexMesh()
            case = _case
        else:
            raise Exception("\n --> snappyHexMesh Failed!\n%s" % log.error)        
    else:
        # output case for setting up the solution.
        case = _case