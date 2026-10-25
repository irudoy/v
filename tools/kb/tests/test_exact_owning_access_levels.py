"""Controlled owning branch routing grants no native or executable admission."""

from copy import deepcopy
import json

import pytest

from kb import levels,repo,ordinary_access_registry as registry
from kb.model import Link,Meaning,Model,Symbol,SymbolKey


@pytest.mark.parametrize('family',[row for row in registry.FAMILIES if row.direct_owning],ids=lambda row:row.mode)
@pytest.mark.parametrize('failure',(None,'unqualified exact original'))
def test_exact_guarded_owning_namespaces_use_direct_identity_and_never_function_or_scale_donation(monkeypatch,family,failure):
    contract,proof=family.contract,family.evidence
    row=contract.descriptor(repo.ROOT)['reference'][0];claim=json.loads(row['proposed_claim_json'])
    owner=Meaning(contract.symbol_key(row).kind,name=row['owner'].rsplit('/',1)[0])
    function=Meaning('fn',name=claim['to'].rsplit('/',1)[0])
    symbol=Symbol(contract.symbol_key(row),meaning=owner)
    target=Symbol(SymbolKey('7mfk','fn',row['function']),meaning=function)
    owner.symbols['7mfk']=symbol;function.symbols['7mfk']=target
    props=deepcopy(claim['props'])
    # Exercise routing in isolation; exact native publication rejects these extra properties.
    props.update(supports=['identity','scale'],reverse_relies='structure',reverse_supports='identity')
    link=Link(owner,claim['type'],function,claim['slot'],claim['offset'],props,deepcopy(claim['evidence']),
        set(claim['stated']),set(claim['sources']),set(claim['roles']))
    owner.links=[link]
    model=Model({}, {}, {}, {}, [link]);model.root=repo.ROOT
    model.meanings=[owner,function];model.symbols={symbol.key:symbol,target.key:target}
    owning=levels.Claim('controlled','owner','identity','code')
    scale=levels.Claim('controlled','scale','scale','code')
    reverse=levels.Claim('controlled','function','identity','code')
    collector=object.__new__(levels._Collector)
    collector.model,collector.pointed,collector.symbols=model,set(),{}
    collector.meanings={(id(owner),'identity'):owning,(id(owner),'scale'):scale,(id(function),'identity'):reverse}
    monkeypatch.setattr(proof,'link_failure',lambda model,link:failure)
    collector._link(link)
    assert scale.items==scale.deps==reverse.items==reverse.deps==[]
    if failure is None:
        assert owning.deps==[] and owning.items==[(symbol,item) for item in link.evidence]
    else:
        assert owning.items==[] and len(owning.deps)==1 and owning.deps[0].lacks==failure
