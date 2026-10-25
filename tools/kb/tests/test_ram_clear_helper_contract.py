"""Natural ROM-pointer clear helper retains all previous claims and shared owner facts."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import repo,test_contract
from kb import ram_initialization_contract as contract,ram_initialization_matrix as matrix
from kb import ram_initialization_capture_evidence as proof,ram_clear_access_contract as owning

RETAINED_CLAIMS={'00027c50-ffff107e-writer': '69372d2f92a7b08d36bc3f97c0584514e62335eacd700255570e93121d0ab6c1', '0002fc24-ffff107e-writer': '7e321864796ccbcd8821b1f61cddb05aed32e515cf11503a45e1d099d8d2278a', '00034b70-ffff107e-writer': 'ca56daf84e810835c1240a28368ef70b88796bdd37f2ed73fcefd0345fc68769', '00027c50-ffff107f-writer': '4c58f0a40badb6688f696ca71c0708f7250af470855b825405e026b173515421', '0002fc24-ffff107f-writer': 'fcda04f3860f3592ce9c02504e40f0f801c4f6cd632a9acf838547b5e7d5284c', '00034b70-ffff107f-writer': '2da9b50c8c79bce2d60a35a3bb6a8a21cab5d561716b4e816a4db77a5dfa4718', '00027c50-ffff1080-writer': 'd0916cfd146cb958c66577fdcd8909916e66d5e96da3a5af3ab61fb7a5c8586d', '0002fc24-ffff1080-writer': 'ec38f1caa341e212b24044ab83a30c5b442a26f56fb773c073cc044f63c3240a', '00034b70-ffff1080-writer': 'b5e3ed354dce6baa9c47d17e386e69dcbcca42261eaa823e6d2aecf39e395940', '00027c50-ffff115a-writer': '394f3c7c8481b70dc696bb890cd29373e89bc505edaf54e901679994df5763ec', '00027c50-ffff162e-writer': 'f6bc741e08b735c7c7d2dc207e8675a0ce0ed6589d06fdc3abfdf4c6ac406a6a', '00027c50-ffff2368-writer': '0c2f1ca3b30636dcba70f13edc903b22d4f298a2cf547a997c7886f488864de0', '00027c50-ffff2494-writer': 'df71df5fc08a6c61c9aba362ac3145e655aeb8e90bb9151eee5cb3bb60433527', '0002fc24-ffff2494-writer': '3ea98af1272250f3afad48c14e83f8da2f7ee6750debe5bd62d93c3e8dcbf262', '00034b70-ffff2494-writer': 'd8508b73b1d12d7290508c79e8967de91ae23ed9497b6eb403fe165f4a983dd5', '00027ac0-ffff3f3e-writer': 'defb23a53a6e03f9b4d57c0885e3e5df378a1e84283912c4eecf4e77f044e26e', '0002fc24-ffff3f3e-writer': 'cff254f9c25033a54a1890dd06f6ac5e60dc051fd0ff44142592cd4d358c03c2', '00034b70-ffff3f3e-writer': '7596e1ccac0d3e47e7c74d277a27d54f0bd350665331b26c68370142799b7d4b', '00027ac0-ffff3f44-writer': 'b10fa87546cddedd1da05dea318d1dee705f03097721c50b242a8fdf94e0a8b7', '0002fc24-ffff3f44-writer': '8867399e2c517e3301c7879e5ad9398b4eb5b2b07745d2f5b67f5f22e9276f8c', '00034b70-ffff3f44-writer': '9fd0acb19ebf14ec1d93fc7167ef5bacdcd9b2819b267e5e2ff171f48087a4b8', '00027ac0-ffff3f4c-writer': '7a724e7b6b0c5e317854f97b7b859beb03e6f8486f4ce0705bcc2f1bb5591202', '0002fc24-ffff3f4c-writer': '51b19d6d3cf354096fc0c9814f49834286743f262e20326af9f59b258a5cebc5', '00034b70-ffff3f4c-writer': 'e7dd331db6ef3e6d85bd0b729aa8dcef0d2244ee10f6bcb658a4ff4557f26780', '00027ac0-ffff418c-writer': '6e8786fa3bcfd2d6131346fb5977685b4a687caa96ccc71f5239472e757b2dcc', '0002fc24-ffff418c-writer': '22b7778845f05d8a8533bddec7f748540177ad61e15ef34c4324edf3444672dd', '00034b70-ffff418c-writer': '934a496f846d6299440b2578dbd742cfa145c59e244c310b64ddfcfaf87da4ea', '00027ac0-ffff418f-writer': '4be487deb512d3ea57e8a39c73d66037d8aad946d590347344c8a11458e5f29c', '00027ac0-ffff41d2-writer': 'c8a23e1b51452c7aa67d9b49771f8e17ad0f4ffa34aaeae8ee114018ded790b1', '0002fc24-ffff41d2-writer': 'a16ab7b2b12bf60efc22544b189ff96e9f6fb886fad90e8e4b6ac9e2ce7410ff', '00034b70-ffff41d2-writer': '146b7d70142447d79fff29295d04aac629a2b5232a94637cbda073c4f35f2b5a', '00027ac0-ffff41ea-writer': 'a7cfd7973b9ac53e592f59e4fa99cfc2adda50c7c999f620990ed7adfd81ebdc', '0002fc24-ffff41ea-writer': '8e65b537c55ef98dd1248ec37008ca36a542c900610060ce99c5856baa57c7fe', '00034b70-ffff41ea-writer': 'acabd1d06ff72c48a49e1f99d39b289392a02e7c71ac2fe64e9ed5377fc8d4c2', '00027ac0-ffff422d-writer': '1ca37d3c3c731f402f0d053e2f9eaee8f35153ce27f87374722b6c545230bd96', '0002fc24-ffff422d-writer': 'e8ecd538e97658396784b835480010c318648357679c95ccbf64552b265b5427', '00034b70-ffff422d-writer': '95c637f78e6c8a62c69f442cce5cb819c799531323b45affb25a3867549c3944', '00027ac0-ffff42a8-writer': 'b76147439131382bb0e628693b4fb572d633e0139b78eacb3b2571ea8f17aa5a', '0002fc24-ffff42a8-writer': 'f8af880ec3522ac1f814af1a536198068cfb8381d7efcd3ad0ef089c72b00ec6', '00034b70-ffff42a8-writer': '034fdaba24cd55ccd25e343e440950f26ec008b90be56b081059397f19691bd5', '0002fc24-ffff5b2c-writer': 'c93119a0e823eafae017dcf7ff1e78c26c0ddc842edacf1bac15428f2b783c86', '00034b70-ffff5b2c-writer': 'ff13ef7382c1d774247254bef07d01c9ad20b0145f6597112a19547cfaf620b8'}
ORIGINAL='393b30717fb2893a08ebc8b6448874c0234f6623a0c4e1b3eb700ca5579c90b1'
RETAINED_POSTIMAGES={'00027c50-ffff107e-writer': '7318a4b498d8e133b402e82b65a59a8552a77bc981023c64e32284888682bfc3', '0002fc24-ffff107e-writer': '7318a4b498d8e133b402e82b65a59a8552a77bc981023c64e32284888682bfc3', '00034b70-ffff107e-writer': '7318a4b498d8e133b402e82b65a59a8552a77bc981023c64e32284888682bfc3', '00027c50-ffff107f-writer': 'ffd8a46c154fee85b71ffce903c35cb5e349b7593ea47453fb0fe3acb4b70bef', '0002fc24-ffff107f-writer': 'ffd8a46c154fee85b71ffce903c35cb5e349b7593ea47453fb0fe3acb4b70bef', '00034b70-ffff107f-writer': 'ffd8a46c154fee85b71ffce903c35cb5e349b7593ea47453fb0fe3acb4b70bef', '00027c50-ffff1080-writer': 'a6d55530276e0c76d08dd79d4b9c2eab18c1297605ef25d2e0606a5930759845', '0002fc24-ffff1080-writer': 'a6d55530276e0c76d08dd79d4b9c2eab18c1297605ef25d2e0606a5930759845', '00034b70-ffff1080-writer': 'a6d55530276e0c76d08dd79d4b9c2eab18c1297605ef25d2e0606a5930759845', '00027c50-ffff115a-writer': '6c842e96bcc74aadf8b82765b2e13cd2c3b4b916b58da5518153244988213a50', '00027c50-ffff162e-writer': 'b52d73a83c0397cd706b146d6b661640e0f4f9c80ab750bcb1ad8ca6ef4b4aa1', '00027c50-ffff2368-writer': '7f99fb595af8ae23a06b703806e2183689ede4a79e2d4268a4a5ce49e37989a7', '00027c50-ffff2494-writer': '9cc73e1700113b6110e3967ce24ced3c2d1d34b29e3a6c3ff4eb3a72a6129cad', '0002fc24-ffff2494-writer': '9cc73e1700113b6110e3967ce24ced3c2d1d34b29e3a6c3ff4eb3a72a6129cad', '00034b70-ffff2494-writer': '9cc73e1700113b6110e3967ce24ced3c2d1d34b29e3a6c3ff4eb3a72a6129cad', '00027ac0-ffff3f3e-writer': '696dd7d46b16404e0bdb13266a5cbd0b4c2b6c22aacbbe9701917bb8e22dd994', '0002fc24-ffff3f3e-writer': '696dd7d46b16404e0bdb13266a5cbd0b4c2b6c22aacbbe9701917bb8e22dd994', '00034b70-ffff3f3e-writer': '696dd7d46b16404e0bdb13266a5cbd0b4c2b6c22aacbbe9701917bb8e22dd994', '00027ac0-ffff3f44-writer': '9970aca01197fad4ed77bb7177f7c33e59e321893ebb4bbf22f960fe7db0e0e0', '0002fc24-ffff3f44-writer': '9970aca01197fad4ed77bb7177f7c33e59e321893ebb4bbf22f960fe7db0e0e0', '00034b70-ffff3f44-writer': '9970aca01197fad4ed77bb7177f7c33e59e321893ebb4bbf22f960fe7db0e0e0', '00027ac0-ffff3f4c-writer': '60625d3b17e001d5bfa665d026d2f60b775dfcb61b20ce2ad7539382a77498d1', '0002fc24-ffff3f4c-writer': '60625d3b17e001d5bfa665d026d2f60b775dfcb61b20ce2ad7539382a77498d1', '00034b70-ffff3f4c-writer': '60625d3b17e001d5bfa665d026d2f60b775dfcb61b20ce2ad7539382a77498d1', '00027ac0-ffff418c-writer': '07bae41dca35cfe85e68c1b0f76155835bc352fd4693d5dae5a862a0a02bb413', '0002fc24-ffff418c-writer': '07bae41dca35cfe85e68c1b0f76155835bc352fd4693d5dae5a862a0a02bb413', '00034b70-ffff418c-writer': '07bae41dca35cfe85e68c1b0f76155835bc352fd4693d5dae5a862a0a02bb413', '00027ac0-ffff418f-writer': 'e965248612d3191d2f58c4243cc277f0f4d2fe1f24c0ac2f9be15afccfbaa1ea', '00027ac0-ffff41d2-writer': '98d8d9a5e6f5a4039fb07fe48b000b9e37d08b9ccb2a1739396ad1c222ae049d', '0002fc24-ffff41d2-writer': '98d8d9a5e6f5a4039fb07fe48b000b9e37d08b9ccb2a1739396ad1c222ae049d', '00034b70-ffff41d2-writer': '98d8d9a5e6f5a4039fb07fe48b000b9e37d08b9ccb2a1739396ad1c222ae049d', '00027ac0-ffff41ea-writer': '4cc0fcc7b71dfbcb48a7109b72587742e825ab9bccb255115df16e470243a7ea', '0002fc24-ffff41ea-writer': '4cc0fcc7b71dfbcb48a7109b72587742e825ab9bccb255115df16e470243a7ea', '00034b70-ffff41ea-writer': '4cc0fcc7b71dfbcb48a7109b72587742e825ab9bccb255115df16e470243a7ea', '00027ac0-ffff422d-writer': 'f3c00011618d73da69370abf0a5c869bd8d24869fdc1a8604867d6c6eb885b6b', '0002fc24-ffff422d-writer': 'f3c00011618d73da69370abf0a5c869bd8d24869fdc1a8604867d6c6eb885b6b', '00034b70-ffff422d-writer': 'f3c00011618d73da69370abf0a5c869bd8d24869fdc1a8604867d6c6eb885b6b', '00027ac0-ffff42a8-writer': 'd8b3a771f544d8c59f4b368a936d90aaba63e4cb5e8acde551a92f0e68171f31', '0002fc24-ffff42a8-writer': 'd8b3a771f544d8c59f4b368a936d90aaba63e4cb5e8acde551a92f0e68171f31', '00034b70-ffff42a8-writer': 'd8b3a771f544d8c59f4b368a936d90aaba63e4cb5e8acde551a92f0e68171f31', '0002fc24-ffff5b2c-writer': 'f83684cfb16086a3f8ad43b58427bc3aec7bd4e2578ff848665df93fe45d5a3a', '00034b70-ffff5b2c-writer': 'f83684cfb16086a3f8ad43b58427bc3aec7bd4e2578ff848665df93fe45d5a3a'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_previous42_full_claims_and_complete_native_preimages_retain_their_exact_pins():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==43
    retained={row['id']:digest({key:value for key,value in row.items()
        if key not in ('proposed_native_json','proposed_native_sha256')}) for row in rows[:42]}
    assert retained==RETAINED_CLAIMS
    row=rows[-1]
    assert (row['original_claim_sha256'],row['owner'],row['function'],row['sites'],row['direction'])==(
        ORIGINAL,'defiant-tiger/ram',0x26F30,[0x26F3E],'writer')
    assert row['declared_width']==row['declared_signed']=='unset' and row['width_bytes']==4
    new_item=owning.item(row)
    for old in rows[:42]:
        postimage=json.loads(old['proposed_native_json'])
        if old['owner']=='defiant-tiger/ram':
            link=next(link for link in postimage['link'] if link['type']=='writer' and link['to']=='mellow-crane/fn')
            original=json.loads(old['original_native_json'])
            previous=next(link for link in original['link'] if link['type']=='writer' and link['to']=='mellow-crane/fn')
            assert link.get('evidence')==[*previous.get('evidence',[]),new_item]
            if 'evidence' in previous:link['evidence']=deepcopy(previous['evidence'])
            else:link.pop('evidence')
        assert digest(postimage)==RETAINED_POSTIMAGES[old['id']]
    shared=[entry for entry in rows if entry['owner']=='defiant-tiger/ram']
    assert len(shared)==3 and len({entry['original_native_json'] for entry in shared})==1
    assert len({entry['proposed_native_json'] for entry in shared})==1
    before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
    expected=deepcopy(before)
    for entry in shared:
        old=json.loads(entry['original_claim_json'])
        link=next(link for link in expected['link'] if link['type']==old['type'] and link['to']==old['to'])
        link.setdefault('evidence',[]).append(owning.item(entry))
    assert test_contract.exact(expected,after)
    assert before['symbol']==after['symbol'] and before['ledger']==after['ledger']


def test_natural_helper_uses_exact_ROM_descriptors_and_stock_RTS_without_an_observing_return():
    source=contract.descriptor(repo.ROOT);window=source['window'][-1]
    assert window==dict(parent=0x26F30,start=0x26F30,end=0x26F4C,gbr=0x12344321,
        first=0xFFFF4514,limit=0xFFFF5CF2,store=0x26F3E,initial_branch=0x26F3A,
        loop_branch=0x26F46,prefix_steps=7,loop_steps=5,natural_return=0x26F48,range_pointer=0x22624)
    assert len(contract.RETURNS)==4 and all(row['address']!=0x26F4C for row in contract.RETURNS)
    image=repo.images()['JK08A'].path.read_bytes();fixture,_=contract.independent_fixture(source,image)
    assert fixture[0x26F30:0x26F4C]==image[0x26F30:0x26F4C]
    assert fixture[0x26F48:0x26F4C]==bytes.fromhex('000b0009')
    assert int.from_bytes(fixture[0x26F9C:0x26FA0],'big')==0x22624
    assert int.from_bytes(fixture[0x22624:0x22628],'big')==0x01004514
    assert int.from_bytes(fixture[0x22628:0x2262C],'big')==0x01005CF2
    assert contract.steps(window)==7649


def test_old_four_windows_and_input_prefix_retain_their_exact_context_seed_rules():
    source=contract.descriptor(repo.ROOT);old=dict(source,window=source['window'][:4])
    assert matrix.cases(source,b'')[:12]==matrix.cases(old,b'')
    for case in matrix.cases(old,b''):
        assert matrix.context(source,case)==matrix.context(old,case)
        assert matrix.memory(case)==bytes([case['seed']])*65536
    assert list(contract.POOLS)[:6]==[0x22604,0x22608,0x22614,0x22618,0x22628,0x34DA0]


@pytest.mark.parametrize('field',('first','limit','natural_return','range_pointer','store','loop_steps'))
def test_descriptor_refuses_changed_natural_helper_limits_entry_store_return_or_budget(tmp_path,field):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();before,after=text.rsplit('[[window]]',1)
    original=next(line for line in after.splitlines() if line.startswith(field+' = '))
    after=after.replace(original,field+' = 0',1);path.write_text(before+'[[window]]'+after)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_current_document_counts_and_nonempty_range_premise_follow_executed_contracts():
    text=(repo.ROOT/'defs/JK08A.ram-initialization.md').read_text()
    assert '43 existing writer' in text and len(owning.descriptor(repo.ROOT)['reference'])==43
    assert 'five exact clear paths' in text and len(contract.WINDOWS)==5
    assert 'four observing returns' in text and len(contract.RETURNS)==4
    assert 'six declared RAM pointers' in text and len(contract.ALIASES)==6
    assert '15 explicit complete-RAM inputs' in text and len(matrix.cases(contract.descriptor(repo.ROOT),b''))==15
    for value in ('00026F30','00026F3E','00026F48','00022624','00022628','FFFF4514','FFFF5CF2','FFFF5CF4'):
        assert value in text
    assert 'fixed nonempty stock range' in text and 'boot' in text
    snippet=(repo.ROOT/'tools/sh-elf-run/README.md').read_text().split('`jk08a-ram-initialization-paths` observes',1)[1].split('`jk08a-counter-array-paths`',1)[0]
    assert 'five exact' in snippet and '43 owning' in snippet
    assert 'six pointer aliases' in snippet and 'four observation returns' in snippet
