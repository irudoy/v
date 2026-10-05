"""Bind the main fuel-compensation surface and bounded bypass selection."""

import hashlib
import importlib.util
from pathlib import Path

import pytest

from kb import compile,derive,repo,sh2
from kb.model import SymbolKey
from tools.kb.tests.stock_corruption import byte_span_ids, byte_span_samples


SPANS=(
    (0x261f0,0x26222,'2176f4225ad3356f24c52d11e5da14b2cdd5935f1970a667bd0d89a732bf81c3'),
    (0x26740,0x2676e,'e5ebb39cde98cd32ad8cbf753572029a70a828ea592d112b2d4d5cef40cd2cb0'),
    (0x26770,0x267c6,'1080f7521938bfb38cf65e93944bf7f76a518a2e6124cbfebbe7d25aec4ca0bf'),
    (0x26944,0x26980,'09442fdef5df6bb92df8a4afc9a4a3ec724ff6d0102256710a3a52014f9a3d4e'),
    (0x269c4,0x26a06,'a21348c3f059ed1c254dc8594efeab2ea70c1f3a24c4e45c0afe173982aa3d35'),
    (0x26c78,0x26d0e,'d280566761efb42c1ca0d5f80c451d1de214aae45441e6bcd43f9d0f31fdbcb8'),
    (0x3c1c0,0x3c236,'ca0fdb1c54d43f777fb697daa6991c3a8bfba48511a21fc5d6eaab8c9c467a95'),
    (0x3c284,0x3c29e,'ae44e3eecb1e833832ebfde8deec80632aecae511c87b9961cc319b294fc7e68'),
    (0x851a,0x851b,'76be8b528d0075f7aae98d6fa57a6d3c83ae480a8469e668d7b0af968995ac71'),
    (0x86f9,0x86fa,'fb95aa98d6e6c5827a57ec17b978d647fcc01d98c357b7e64989af57339e9ac3'),
    (0x8b34,0x8b35,'591b7cc95037822dec5a4d593a2e2e8b19c07ddd2570e5699003d17f14c440a6'),
    (0x8b42,0x8b43,'7d8c5da7fd418379048e430b33dc8ffcda739e44326b8a5d647dc0ad81ed2157'),
    (0xa29a,0xa39a,'72d629803aae03d4c3f025d92b4f06498718030d6eee0cf9b868700556eb0f3e'),
    (0x11cf0,0x11d00,'a4ca9c731bf7cb87107d25fba7c2efe4500788c8dd109a55daea26fa555ef8f8'),
    (0x11d4c,0x11d5c,'c35b2f2dfd33a0c4bf3c83aefa46239924cd27ac8106957583d235b68b18a906'),
    (0x26224,0x26230,'dabfd26554b2253777dbf53a7f18015d18254080dd023ed4f2a88bae070f1f67'),
    (0x267c8,0x267cc,'cfc4959a72f2784595ed1bfa65612a0fdc2966ab3dbd24318f13a22dfce67f8d'),
    (0x26980,0x26984,'f48d18c3250763b996e2c2d4e34fec4761199c6d4cef0f0b18ae23f2aa0fa35c'),
    (0x26a08,0x26a0c,'f48d18c3250763b996e2c2d4e34fec4761199c6d4cef0f0b18ae23f2aa0fa35c'),
    (0x3c26c,0x3c284,'db69e8c2e09b934d98135d7c470478494207802818d4bc850424790971b77d69'),
    (0x3c37c,0x3c390,'3354afcdc9d2784f11b410fa2a86443618c68d22dceb6b26c3f8679fdcc63545'),
    (0x3bf28,0x3bf2e,'be8a3d2865599abdaca9cee50f285c65ff08b5dc00c388dd7863332a701ee849'),
    (0x3bfbc,0x3bfbe,'2a75f90124036492ee9437fc55adea1d85578a6027b23c1de131ac3970d0f6e1'),
    (0x3c092,0x3c094,'9b777ee8b1e7b2c0cd73e8a070bdecdd5656ba0859ef16b480d6b0841d27d674'),
    (0x3c0c4,0x3c0d0,'c1b2b6ae089de7a44d8d7c9bc37024d4f41bc5a4a1d01c0bea8e7780fdcb9d90'),
    (0x3c020,0x3c024,'9fb5dc466d8f9a48731e0b949648179140d08a44981958b15dcd437029e243e8'),
    (0x3c03c,0x3c040,'20cd895c4c1549090441989a67c192c8f146c0ce518df06934cea4991f5897e5'),
    (0x3c248,0x3c24c,'9fb5dc466d8f9a48731e0b949648179140d08a44981958b15dcd437029e243e8'),
)


def verify_compensation(data):
    for start,end,digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest()==digest,f'{start:08x}'

    def word(address,size=2):
        return int.from_bytes(data[address:address+size],'big')

    def instruction(address):
        return sh2.decode(word(address),address)

    assert [word(address,4) for address in (0x26224,0x26228,0x2622c)]==[0x26770,0x26944,0x269c4]
    assert word(0x267c8,4)==0x26740
    assert word(0x26980,4)==word(0x26a08,4)==0x26c78
    assert instruction(0x261f4).value==('extu',16,7)
    assert instruction(0x26206).access==sh2.Access(15,16,4,'load')
    assert instruction(0x26208).value==('extu',8,5)
    assert word(0x269ca)==0x4108 and word(0x269ee)==0x4008
    assert word(0x3c26c,4)==0x8b42 and word(0x3c270,4)==0x8b34
    assert [word(address) for address in (0x3c1c6,0x3c1d0,0x3c1d6,0x3c1e0,0x3c1ec)]==[
        0xc820,0xc810,0xc901,0xc802,0xc802]
    assert word(0x3c274,4)==0x86f9 and word(0x3c278,4)==0x851a
    assert word(0x3c27c,4)+0x69==0xffff5625
    assert word(0x3c280,4)+0xb8==0xffff2836
    assert [word(address,4) for address in range(0x3c37c,0x3c390,4)]==[
        0xa29a,0x11cf0,0x11d4c,0x261f0,0xffff1048]
    assert instruction(0x3c288).access==sh2.Access(10,0,1,'load',indexed=True)
    assert word(0x3c284)==0xe05c and word(0x3c29a)==0xe04c
    assert instruction(0x3c294).access==sh2.Access(15,3,1,'store')
    assert instruction(0x3c29c).access==sh2.Access(10,0,1,'store',indexed=True)
    assert word(0x3c03c,4)==0xffff1114 and word(0x3c248,4)==0xffff11d4
    assert instruction(0x3c0c8).access==sh2.Access(9,0,2,'load',indexed=True)
    assert word(0x3c0c4)==0xe020 and instruction(0x3c0ce).value==('extu',16,12)
    assert word(0x3c28a)==0x67c3


def test_fuel_compensation_axes_interpolation_selectors_bypass_and_store_match_stock():
    verify_compensation(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', byte_span_samples(SPANS), ids=byte_span_ids(SPANS))
def test_changed_fuel_compensation_axis_fraction_order_selector_source_or_byte_store_fails(address, jk08a_stock_bytes):
    data=bytearray(jk08a_stock_bytes)
    data[address]^=1
    with pytest.raises(AssertionError):
        verify_compensation(data)


def test_fuel_compensation_keeps_typed_inputs_conditions_axes_and_arithmetic_only_step():
    model=compile.cached(repo.ROOT)
    step=model.entities[('chain','airflow_load')].steps[21]
    assert step['note']==('ffff1160 = uint8(interpolate(ROM8[0x0000a29a],'
                          'uint16(ffff11f4),uint8(ffff1170)))')
    assert [ref.address for ref in step['via']]==[0x3bd74]
    output=model.meaning_of(SymbolKey('7mfk','ram',0xffff1160))
    assert {link.to.key for link in output.links if link.type=='input'}=={
        'fuel_compensation_main/tbl','authentic-wasp/ram','alpha_n_flow/ram','fuel_compensation_bypass_first/ram',
        'fuel_compensation_bypass_second/ram','fuel_compensation_bypass_scalar/tbl'}
    assert {(link.to.key,link.slot) for link in output.links if link.type=='selector'}=={
        ('fuel_compensation_mode_a/tbl','bit5'),('fuel_compensation_mode_a/tbl','bit0'),
        ('fuel_compensation_mode_b/tbl','bit4'),('fuel_compensation_mode_b/tbl','bit1'),
        ('fuel_compensation_source_mode/tbl','bit1')}
    table=model.meaning_of(SymbolKey('7mfk','tbl',0xa29a))
    assert {(link.to.key,link.slot) for link in table.links if link.type=='axis'}=={
        ('mellow-turtle/axis','x'),('fascinating-hog/axis','y')}
    assert table.props['scale']=='x*0.78125' and table.props['scale_level']=='candidate'
    for address,width in ((0xffff1160,8),(0xffff1170,8),(0xffff11f4,16),
                          (0xffff5625,8),(0xffff2836,8)):
        symbol=model.symbols[SymbolKey('7mfk','ram',address)]
        assert symbol.value('width')==width and symbol.value('signed') is False
    for key in ('fuel_compensation_bypass_first/ram','fuel_compensation_bypass_second/ram',
                'fuel_compensation_mode_a/tbl','fuel_compensation_mode_b/tbl',
                'fuel_compensation_source_mode/tbl','fuel_compensation_bypass_scalar/tbl'):
        meaning=next(item for item in model.meanings if item.key==key)
        assert meaning.props['block']=='airflow_load/block'


def test_fuel_compensation_published_counts_bind_the_registered_execution():
    path=repo.ROOT/'tools/sh-elf-run/verify_stock_code.py'
    spec=importlib.util.spec_from_file_location('fuel_compensation_count_verifier',path)
    module=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    region=next(item for item in module.REGIONS if item.key=='jk08a-fuel-compensation')
    instructions=sum((end-start)//2 for start,end in region.code_spans)
    bound=sum(end-start for start,end in region.code_spans)+sum(size for _,size in region.pools)
    section=(repo.ROOT/'tools/sh-elf-run/README.md').read_text().split('## Main fuel compensation',1)[1].split('\n## ',1)[0]
    section=' '.join(section.split())
    assert (instructions,bound,region.cases)==(301,962,3494)
    assert f'{instructions} instructions' in section and f'{bound} bound bytes' in section
    assert f'{region.cases} cases' in section
    static_bytes=sum(end-start for start,end,_ in SPANS)
    assert static_bytes==996 and f'{static_bytes} bytes' in section
    image=module.stock_image(region.rom)
    fixture=module.build_fixture(region,image)
    for start,end in region.code_spans:
        assert fixture[start:end]==image[start:end]
    assert region.ram_literals==(0x3c27c,0x3c280,0x3c38c)
    assert region.return_address_offset==4
