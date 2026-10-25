"""Source and case-shape controls, without GNU execution or native admission."""
import ast
import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest

from kb import coherent_copy_matrix as matrix, coherent_copy_evidence as proof, repo
BASE=repo.ROOT/'tools/sh-elf-run'
HEADER=(BASE/'coherent-copy-cases.h').read_text()
BINDINGS=proof.descriptor(repo.ROOT)

def array(name):
    body,=re.findall(r'\b'+re.escape(name)+r'\[\] = (\{.*?\});',HEADER,re.S)
    body=re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    return ast.literal_eval(body.replace('{','[').replace('}',']'))

def test_all_rendered_case_inputs_match_independent_ordered_matrix():
    actual=array('coherent_cases')
    expected=[]
    for window in matrix.WINDOWS:
        for case in matrix.cases(window):
            expected.append([case['index'],case['seed'],case['variant'],case['t'],
                0xffffffff if case['isolated'] is None else case['isolated'],int(case['carry'])])
    assert actual==expected and len(actual)==17228

def test_windows_bind_each_complete_context_and_exact_source_pool_set():
    windows=array('coherent_windows')
    reads=array('coherent_read_addresses');pools=array('coherent_pool_addresses')
    assert len(windows)==len(matrix.WINDOWS)==15
    for values,window,binding in zip(windows,matrix.WINDOWS,BINDINGS['window']):
        entry,call,helper,source,destination,length,mask,context,read_start,read_count,pool_start,pool_count,case_start,case_count,early_start,early_count=values
        assert [entry,call,helper,source,destination,length]==[
            window.entry,window.call,window.helper,window.source,window.destination,window.length]
        assert mask==sum(1<<r for r,_ in window.context)
        assert len(context)==15 and {(r,value) for r,value in enumerate(context) if mask&(1<<r)}==set(window.context)
        assert all(value==0 for r,value in enumerate(context) if not mask&(1<<r))
        assert reads[read_start:read_start+read_count]==list(matrix.read_addresses(window))
        assert pools[pool_start:pool_start+pool_count]==[row['address'] for row in binding['pool']]
        assert len(matrix.cases(window))==case_count
        assert 0<=case_start<=17228-case_count and 0<=early_start<=109-early_count

def test_feedback_selection_keeps_successive_predecessors_and_read_ahead():
    windows=array('coherent_windows');early=array('coherent_early_indices')
    assert len(early)==109
    for values,window in zip(windows,matrix.WINDOWS):
        rows=matrix.cases(window)
        start,count=values[-2:]
        chosen=early[start:start+count]
        assert chosen==sorted(set(chosen))
        assert 0 in chosen and 1023 in chosen
        for index in chosen:
            if rows[index]['carry']:assert index-1 in chosen
        addresses={rows[index]['isolated'] for index in chosen if rows[index]['isolated'] is not None}
        if window.helper==0x22038:assert window.source+window.length in addresses
        if window.call==0x20f56:assert {0xffff1083,0xffff1087}<=addresses

def test_source_driver_records_full_state_and_every_external_ram_byte():
    source=(BASE/'harness-coherent-copy-capture.c').read_text()
    for field in ('incoming','incoming_after','exit','sp','continuation','sr_before',
        'abi_before','abi_after','frame_before','frame_after','read_before','read_after',
        'destination_before','destination_after','pools_before','pools_after','outside_changes'):
        assert '\\"'+field+'\\"' in source
    assert 'for(i=0;i<65536U;++i)' in source
    assert 'stock_invoke_injection_start_delay(window->entry,&context,&out);' in source
    assert 'VQ_SH_ELF_COHERENT_COPY_CAPTURE' in source
    assert 'complete=true' not in source and 'kb-copy-candidate' not in source
