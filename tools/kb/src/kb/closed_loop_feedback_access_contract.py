"""Exact existing whole-feedback bytes, observer, frame and overlapping workspace."""

import hashlib
from pathlib import Path
import tomllib

from kb import test_contract

DESCRIPTOR='defs/JK08A.closed-loop-feedback-accesses.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
ENTRY=0x5CBEC
OBSERVER='tools/sh-elf-run/invoke-closed-loop-feedback.s'
LEGACY_CONTRACT='tools/sh-elf-run/closed-loop-feedback-contracts.json'
UNIT = {'assembly': 'tools/sh-elf-run/stock_jk08a_closed_loop_feedback.s',
 'code': [{'start': 379884, 'end': 380176},
          {'start': 138172, 'end': 138454},
          {'start': 156788, 'end': 156822},
          {'start': 156832, 'end': 156866},
          {'start': 157504, 'end': 157550},
          {'start': 158020, 'end': 158080},
          {'start': 158840, 'end': 158990},
          {'start': 379532, 'end': 379880},
          {'start': 380240, 'end': 380452},
          {'start': 380460, 'end': 380840},
          {'start': 380850, 'end': 380882},
          {'start': 380952, 'end': 381082},
          {'start': 381088, 'end': 381422},
          {'start': 381426, 'end': 381536},
          {'start': 381572, 'end': 381760},
          {'start': 381766, 'end': 382156},
          {'start': 382166, 'end': 382188},
          {'start': 382208, 'end': 382466},
          {'start': 382468, 'end': 382786},
          {'start': 382796, 'end': 382854},
          {'start': 382892, 'end': 383084},
          {'start': 383086, 'end': 383398},
          {'start': 383408, 'end': 383462},
          {'start': 383524, 'end': 383828},
          {'start': 383832, 'end': 384010},
          {'start': 384036, 'end': 384248},
          {'start': 384250, 'end': 384616},
          {'start': 384624, 'end': 384672},
          {'start': 384696, 'end': 384940},
          {'start': 384942, 'end': 385226},
          {'start': 385230, 'end': 385300},
          {'start': 385324, 'end': 385516}],
 'pools': [{'address': 32768, 'size': 57344},
           {'address': 138456, 'size': 8},
           {'address': 145220, 'size': 32},
           {'address': 156824, 'size': 8},
           {'address': 156868, 'size': 8},
           {'address': 158080, 'size': 4},
           {'address': 379880, 'size': 4},
           {'address': 380176, 'size': 10},
           {'address': 380188, 'size': 52},
           {'address': 380452, 'size': 8},
           {'address': 380840, 'size': 10},
           {'address': 380882, 'size': 4},
           {'address': 380888, 'size': 64},
           {'address': 381082, 'size': 6},
           {'address': 381422, 'size': 4},
           {'address': 381536, 'size': 36},
           {'address': 381760, 'size': 6},
           {'address': 382156, 'size': 10},
           {'address': 382188, 'size': 20},
           {'address': 382466, 'size': 2},
           {'address': 382786, 'size': 10},
           {'address': 382856, 'size': 36},
           {'address': 383084, 'size': 2},
           {'address': 383398, 'size': 10},
           {'address': 383462, 'size': 8},
           {'address': 383472, 'size': 52},
           {'address': 383828, 'size': 4},
           {'address': 384010, 'size': 26},
           {'address': 384248, 'size': 2},
           {'address': 384616, 'size': 8},
           {'address': 384672, 'size': 24},
           {'address': 384940, 'size': 2},
           {'address': 385226, 'size': 4},
           {'address': 385300, 'size': 24},
           {'address': 385644, 'size': 12}],
 'aliases': [{'address': 138456, 'width': 4, 'original': 4294940696, 'alias': 16816152},
             {'address': 380196, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 380212, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 380216, 'width': 4, 'original': 4294912152, 'alias': 16787608},
             {'address': 380220, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 380224, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 380228, 'width': 4, 'original': 4294911055, 'alias': 16786511},
             {'address': 380232, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 380236, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 380888, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 380892, 'width': 4, 'original': 4294918565, 'alias': 16794021},
             {'address': 380896, 'width': 4, 'original': 4294918569, 'alias': 16794025},
             {'address': 380900, 'width': 4, 'original': 4294911182, 'alias': 16786638},
             {'address': 380904, 'width': 4, 'original': 4294911064, 'alias': 16786520},
             {'address': 380908, 'width': 4, 'original': 4294918532, 'alias': 16793988},
             {'address': 380912, 'width': 4, 'original': 4294912152, 'alias': 16787608},
             {'address': 380916, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 380920, 'width': 4, 'original': 4294905892, 'alias': 16781348},
             {'address': 380924, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 380928, 'width': 4, 'original': 4294905962, 'alias': 16781418},
             {'address': 380932, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 380936, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 380940, 'width': 4, 'original': 4294918320, 'alias': 16793776},
             {'address': 381540, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 381552, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 381556, 'width': 4, 'original': 4294906004, 'alias': 16781460},
             {'address': 381560, 'width': 4, 'original': 4294912152, 'alias': 16787608},
             {'address': 381568, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 382188, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 382192, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 382196, 'width': 4, 'original': 4294910712, 'alias': 16786168},
             {'address': 382200, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 382204, 'width': 4, 'original': 4294912152, 'alias': 16787608},
             {'address': 382864, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 382868, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 382872, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 382876, 'width': 4, 'original': 4294918316, 'alias': 16793772},
             {'address': 383472, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 384024, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 384680, 'width': 4, 'original': 4294918324, 'alias': 16793780},
             {'address': 384684, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 385308, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 385644, 'width': 4, 'original': 4294918324, 'alias': 16793780},
             {'address': 379880, 'width': 2, 'original': 4294936756, 'alias': 24576, 'size': 298},
             {'address': 379882, 'width': 2, 'original': 4294937048, 'alias': 24868, 'size': 6},
             {'address': 380176, 'width': 2, 'original': 4294936752, 'alias': 24572, 'size': 302},
             {'address': 380456, 'width': 2, 'original': 4294937050, 'alias': 24870, 'size': 4},
             {'address': 380840, 'width': 2, 'original': 4294937050, 'alias': 24870, 'size': 4},
             {'address': 382158, 'width': 2, 'original': 4294937050, 'alias': 24870, 'size': 4},
             {'address': 382788, 'width': 2, 'original': 4294937036, 'alias': 24856, 'size': 18},
             {'address': 382790, 'width': 2, 'original': 4294936768, 'alias': 24588, 'size': 286},
             {'address': 382792, 'width': 2, 'original': 4294936764, 'alias': 24584, 'size': 290},
             {'address': 383398, 'width': 2, 'original': 4294936780, 'alias': 24600, 'size': 274},
             {'address': 383400, 'width': 2, 'original': 4294936808, 'alias': 24628, 'size': 246},
             {'address': 383464, 'width': 2, 'original': 4294936780, 'alias': 24600, 'size': 274},
             {'address': 383828, 'width': 2, 'original': 4294936820, 'alias': 24640, 'size': 234},
             {'address': 384248, 'width': 2, 'original': 4294936980, 'alias': 24800, 'size': 74},
             {'address': 384616, 'width': 2, 'original': 4294936836, 'alias': 24656, 'size': 218},
             {'address': 384622, 'width': 2, 'original': 4294936836, 'alias': 24656, 'size': 218},
             {'address': 384940, 'width': 2, 'original': 4294936824, 'alias': 24644, 'size': 230}]}
WORKSPACE = {'start': 24572, 'size': 302, 'logical_offset': 34992, 'observed_start': 24540, 'observed_size': 366}
CONTROLLED_CALIBRATION = [{'address': 74514, 'size': 16}, {'address': 33682, 'size': 1}, {'address': 36052, 'size': 1}]
FLAGS = ('automatic_resolution',
 'native_geometry_inference',
 'physical_callee_reader_inference',
 'scale_admission',
 'units_admission',
 'natural_scheduling_inference',
 'hardware_qualification')
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])
BOUND_SPANS=tuple(dict(address=first,size=last-first) for first,last in SPANS)+tuple(UNIT['pools'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entry_point','observer',
            'context_bytes','frame_bytes','frame_prefix','workspace','unit','controlled_calibration',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-closed-loop-feedback-accesses'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or any(value[key] is not False for key in FLAGS)
            or not test_contract.exact((value['entry_point'],value['observer'],value['context_bytes'],value['frame_bytes'],value['frame_prefix']),
                (ENTRY,OBSERVER,76,352,320))
            or not test_contract.exact(value['workspace'],WORKSPACE)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)):
        raise ValueError('the feedback argument/store source changes its exact old closure, frame, workspace or scope')
    return dict(value,entry=[dict(start=start,end=end) for start,end in SPANS])


def require_image(declared,image):
    if type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256:
        raise ValueError('the feedback source changes its exact owned stock image')
    for row in UNIT['aliases']:
        if int.from_bytes(image[row['address']:row['address']+row['width']],'big')!=row['original']&((1<<(8*row['width']))-1):
            raise ValueError('the feedback source changes a stock long or word pointer literal')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at,width=row['address'],row['width']
        if any(first<at+width and at<last for first,last in SPANS):
            raise ValueError('a feedback alias overlaps a tested instruction')
        fixture[at:at+width]=row['alias'].to_bytes(width,'big');aliases.append(dict(row))
    for first,last in SPANS:
        if fixture[first:last]!=image[first:last]:raise ValueError('the feedback fixture changes a tested instruction')
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case,root):
    from kb import closed_loop_feedback_matrix as matrix
    fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for at,data in matrix.calibrations(declared,image,case).items():
        if (any(first<at+len(data) and at<last for first,last in SPANS)
                or any(row['address']<at+len(data) and at<row['address']+row['width'] for row in UNIT['aliases'])):
            raise ValueError('a feedback controlled calibration overlaps tested instructions or pointer literals')
        fixture[at:at+len(data)]=data
    return bytes(fixture),aliases


def state_storage_premise(declared):
    return (declared.get('id')=='jk08a-closed-loop-feedback-accesses'
        and declared.get('layout')=='7mfk' and declared.get('rom')=='JK08A'
        and declared.get('image_sha256')==IMAGE_SHA256
        and test_contract.exact((declared.get('entry_point'),declared.get('observer'),
            declared.get('context_bytes'),declared.get('frame_bytes'),declared.get('frame_prefix')),
            (ENTRY,OBSERVER,76,352,320))
        and test_contract.exact(declared.get('workspace'),WORKSPACE)
        and test_contract.exact(declared.get('unit'),UNIT)
        and test_contract.exact(declared.get('entry'),[dict(start=start,end=end) for start,end in SPANS])
        and all(declared.get(key) is False for key in FLAGS))
