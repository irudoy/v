"""Exact natural scalar RAM leaves, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.scalar-ram-leaves.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(154046, 234888, 235636, 288944, 306068, 307000, 310122, 311606, 319762, 349358, 462210, 677168)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s',
 'code': [{'start': 154046, 'end': 154064},
          {'start': 234888, 'end': 234926},
          {'start': 235636, 'end': 235670},
          {'start': 288944, 'end': 289048},
          {'start': 306068, 'end': 306132},
          {'start': 307000, 'end': 307082},
          {'start': 310122, 'end': 310178},
          {'start': 311606, 'end': 311680},
          {'start': 319762, 'end': 319842},
          {'start': 349358, 'end': 349424},
          {'start': 462210, 'end': 462274},
          {'start': 677168, 'end': 677216}],
 'pools': [{'address': 33856, 'size': 1, 'stock_hex': '0a'},
           {'address': 34572, 'size': 1, 'stock_hex': '44'},
           {'address': 35647, 'size': 1, 'stock_hex': '18'},
           {'address': 235252, 'size': 4, 'stock_hex': 'ffff1114'},
           {'address': 235272, 'size': 4, 'stock_hex': 'ffff107a'},
           {'address': 235764, 'size': 2, 'stock_hex': '0129'},
           {'address': 235948, 'size': 4, 'stock_hex': 'ffff1e60'},
           {'address': 235972, 'size': 4, 'stock_hex': 'ffff107a'},
           {'address': 289048, 'size': 2, 'stock_hex': '04c6'},
           {'address': 289050, 'size': 2, 'stock_hex': '04d9'},
           {'address': 289052, 'size': 2, 'stock_hex': '04bc'},
           {'address': 289054, 'size': 2, 'stock_hex': '0320'},
           {'address': 289056, 'size': 2, 'stock_hex': '016b'},
           {'address': 289058, 'size': 2, 'stock_hex': '047e'},
           {'address': 289060, 'size': 2, 'stock_hex': '0102'},
           {'address': 289062, 'size': 2, 'stock_hex': '04ae'},
           {'address': 289064, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 289068, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 289072, 'size': 4, 'stock_hex': '0000870c'},
           {'address': 289076, 'size': 4, 'stock_hex': 'ffff1e60'},
           {'address': 306134, 'size': 2, 'stock_hex': '0656'},
           {'address': 306428, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 306432, 'size': 4, 'stock_hex': 'ffff22dc'},
           {'address': 307082, 'size': 2, 'stock_hex': '0383'},
           {'address': 307084, 'size': 2, 'stock_hex': '0384'},
           {'address': 307092, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 307140, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 307156, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 307160, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 310182, 'size': 2, 'stock_hex': '03cb'},
           {'address': 310340, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 310376, 'size': 4, 'stock_hex': 'ffff22f8'},
           {'address': 310392, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 311682, 'size': 2, 'stock_hex': '05a5'},
           {'address': 311684, 'size': 2, 'stock_hex': '05a4'},
           {'address': 311712, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 311720, 'size': 4, 'stock_hex': 'ffff4184'},
           {'address': 311768, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 311772, 'size': 4, 'stock_hex': 'ffff24ce'},
           {'address': 311776, 'size': 4, 'stock_hex': 'ffff120e'},
           {'address': 319868, 'size': 2, 'stock_hex': '0287'},
           {'address': 319920, 'size': 4, 'stock_hex': 'ffff25fb'},
           {'address': 319924, 'size': 4, 'stock_hex': 'ffff2470'},
           {'address': 319928, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 319932, 'size': 4, 'stock_hex': '00008440'},
           {'address': 349428, 'size': 2, 'stock_hex': '034e'},
           {'address': 349430, 'size': 2, 'stock_hex': '036c'},
           {'address': 349640, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 349676, 'size': 4, 'stock_hex': 'ffff22f8'},
           {'address': 462370, 'size': 2, 'stock_hex': '0734'},
           {'address': 462372, 'size': 2, 'stock_hex': '0736'},
           {'address': 462380, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 462384, 'size': 4, 'stock_hex': 'ffff23bc'},
           {'address': 462388, 'size': 4, 'stock_hex': 'ffff256a'},
           {'address': 677456, 'size': 2, 'stock_hex': '0a3c'},
           {'address': 677458, 'size': 2, 'stock_hex': '09f6'},
           {'address': 677744, 'size': 4, 'stock_hex': 'ffff41a9'},
           {'address': 677748, 'size': 4, 'stock_hex': 'ffff244f'},
           {'address': 677752, 'size': 4, 'stock_hex': 'ffff28f8'}],
 'aliases': [{'address': 235252, 'width': 4, 'original': 4294906132, 'alias': 16781588},
             {'address': 235272, 'width': 4, 'original': 4294905978, 'alias': 16781434},
             {'address': 235948, 'width': 4, 'original': 4294909536, 'alias': 16784992},
             {'address': 235972, 'width': 4, 'original': 4294905978, 'alias': 16781434},
             {'address': 289064, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 289068, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 289076, 'width': 4, 'original': 4294909536, 'alias': 16784992},
             {'address': 306428, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 306432, 'width': 4, 'original': 4294910684, 'alias': 16786140},
             {'address': 307092, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 307140, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 307156, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 310340, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 310376, 'width': 4, 'original': 4294910712, 'alias': 16786168},
             {'address': 310392, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 311712, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 311720, 'width': 4, 'original': 4294918532, 'alias': 16793988},
             {'address': 311768, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 311772, 'width': 4, 'original': 4294911182, 'alias': 16786638},
             {'address': 311776, 'width': 4, 'original': 4294906382, 'alias': 16781838},
             {'address': 319920, 'width': 4, 'original': 4294911483, 'alias': 16786939},
             {'address': 319924, 'width': 4, 'original': 4294911088, 'alias': 16786544},
             {'address': 319928, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 349640, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 349676, 'width': 4, 'original': 4294910712, 'alias': 16786168},
             {'address': 462380, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 462384, 'width': 4, 'original': 4294910908, 'alias': 16786364},
             {'address': 462388, 'width': 4, 'original': 4294911338, 'alias': 16786794},
             {'address': 677744, 'width': 4, 'original': 4294918569, 'alias': 16794025},
             {'address': 677748, 'width': 4, 'original': 4294911055, 'alias': 16786511},
             {'address': 677752, 'width': 4, 'original': 4294912248, 'alias': 16787704}]}
CONTROLLED_CALIBRATION=[{'address': 33856, 'size': 1},
 {'address': 34572, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 235252, 'size': 4},
 {'address': 235272, 'size': 4},
 {'address': 235764, 'size': 2},
 {'address': 235948, 'size': 4},
 {'address': 235972, 'size': 4},
 {'address': 289048, 'size': 2},
 {'address': 289050, 'size': 2},
 {'address': 289052, 'size': 2},
 {'address': 289054, 'size': 2},
 {'address': 289056, 'size': 2},
 {'address': 289058, 'size': 2},
 {'address': 289060, 'size': 2},
 {'address': 289062, 'size': 2},
 {'address': 289064, 'size': 4},
 {'address': 289068, 'size': 4},
 {'address': 289072, 'size': 4},
 {'address': 289076, 'size': 4},
 {'address': 306134, 'size': 2},
 {'address': 306428, 'size': 4},
 {'address': 306432, 'size': 4},
 {'address': 307082, 'size': 2},
 {'address': 307084, 'size': 2},
 {'address': 307092, 'size': 4},
 {'address': 307140, 'size': 4},
 {'address': 307156, 'size': 4},
 {'address': 307160, 'size': 4},
 {'address': 310182, 'size': 2},
 {'address': 310340, 'size': 4},
 {'address': 310376, 'size': 4},
 {'address': 310392, 'size': 4},
 {'address': 311682, 'size': 2},
 {'address': 311684, 'size': 2},
 {'address': 311712, 'size': 4},
 {'address': 311720, 'size': 4},
 {'address': 311768, 'size': 4},
 {'address': 311772, 'size': 4},
 {'address': 311776, 'size': 4},
 {'address': 319868, 'size': 2},
 {'address': 319920, 'size': 4},
 {'address': 319924, 'size': 4},
 {'address': 319928, 'size': 4},
 {'address': 319932, 'size': 4},
 {'address': 349428, 'size': 2},
 {'address': 349430, 'size': 2},
 {'address': 349640, 'size': 4},
 {'address': 349676, 'size': 4},
 {'address': 462370, 'size': 2},
 {'address': 462372, 'size': 2},
 {'address': 462380, 'size': 4},
 {'address': 462384, 'size': 4},
 {'address': 462388, 'size': 4},
 {'address': 677456, 'size': 2},
 {'address': 677458, 'size': 2},
 {'address': 677744, 'size': 4},
 {'address': 677748, 'size': 4},
 {'address': 677752, 'size': 4}]
BOUND_SPANS=({'address': 154046, 'size': 18},
 {'address': 234888, 'size': 38},
 {'address': 235636, 'size': 34},
 {'address': 288944, 'size': 104},
 {'address': 306068, 'size': 64},
 {'address': 307000, 'size': 82},
 {'address': 310122, 'size': 56},
 {'address': 311606, 'size': 74},
 {'address': 319762, 'size': 80},
 {'address': 349358, 'size': 66},
 {'address': 462210, 'size': 64},
 {'address': 677168, 'size': 48},
 {'address': 33856, 'size': 1},
 {'address': 34572, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 235252, 'size': 4},
 {'address': 235272, 'size': 4},
 {'address': 235764, 'size': 2},
 {'address': 235948, 'size': 4},
 {'address': 235972, 'size': 4},
 {'address': 289048, 'size': 2},
 {'address': 289050, 'size': 2},
 {'address': 289052, 'size': 2},
 {'address': 289054, 'size': 2},
 {'address': 289056, 'size': 2},
 {'address': 289058, 'size': 2},
 {'address': 289060, 'size': 2},
 {'address': 289062, 'size': 2},
 {'address': 289064, 'size': 4},
 {'address': 289068, 'size': 4},
 {'address': 289072, 'size': 4},
 {'address': 289076, 'size': 4},
 {'address': 306134, 'size': 2},
 {'address': 306428, 'size': 4},
 {'address': 306432, 'size': 4},
 {'address': 307082, 'size': 2},
 {'address': 307084, 'size': 2},
 {'address': 307092, 'size': 4},
 {'address': 307140, 'size': 4},
 {'address': 307156, 'size': 4},
 {'address': 307160, 'size': 4},
 {'address': 310182, 'size': 2},
 {'address': 310340, 'size': 4},
 {'address': 310376, 'size': 4},
 {'address': 310392, 'size': 4},
 {'address': 311682, 'size': 2},
 {'address': 311684, 'size': 2},
 {'address': 311712, 'size': 4},
 {'address': 311720, 'size': 4},
 {'address': 311768, 'size': 4},
 {'address': 311772, 'size': 4},
 {'address': 311776, 'size': 4},
 {'address': 319868, 'size': 2},
 {'address': 319920, 'size': 4},
 {'address': 319924, 'size': 4},
 {'address': 319928, 'size': 4},
 {'address': 319932, 'size': 4},
 {'address': 349428, 'size': 2},
 {'address': 349430, 'size': 2},
 {'address': 349640, 'size': 4},
 {'address': 349676, 'size': 4},
 {'address': 462370, 'size': 2},
 {'address': 462372, 'size': 2},
 {'address': 462380, 'size': 4},
 {'address': 462384, 'size': 4},
 {'address': 462388, 'size': 4},
 {'address': 677456, 'size': 2},
 {'address': 677458, 'size': 2},
 {'address': 677744, 'size': 4},
 {'address': 677748, 'size': 4},
 {'address': 677752, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34572, 'field': 'sum_configuration'},
 {'address': 35647, 'field': 'timing_configuration'},
 {'address': 33856, 'field': 'decay_configuration'}]
ADAPTER_SHA256='8d5ab56f87f11d852068314cde04071f8a83d51b582ebde549ef940b344b10bb'
FUNCTIONS=ENTRIES
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-scalar-ram-leaves'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the scalar RAM leaves change an exact natural entry, code/pool byte, alias or complete observer premise')
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the scalar RAM leaves change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the scalar RAM leaves change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the scalar RAM leaves relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import scalar_ram_leaf_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:fixture[row['address']]=case[row['field']]
    return bytes(fixture),aliases
