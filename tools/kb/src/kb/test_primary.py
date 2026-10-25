"""Original shared GNU record consumed by independent TEST fact adapters."""

from dataclasses import dataclass
import json
import hashlib
from pathlib import Path

from kb import copy_evidence, local_paths, test_contract
from kb.model import SymbolKey

COPY_OPTION = '--kb-test-copy-primary'
SID22_OPTION = '--kb-test-sid22-primary'


def references(root, copy_path, sid22_path):
    root = Path(root).resolve()
    result = {}
    for key, path in (('COPY', copy_path), ('SID22', sid22_path)):
        physical = local_paths.owned(path, root).resolve()
        if not physical.is_relative_to(local_paths.results_root(root)):
            raise ValueError('the TEST primary preparation must live in tmp/local-results')
        relative = local_paths.relative(physical, root)
        data = copy_evidence.read_output(root, relative)
        result[key] = dict(path=relative, sha256=hashlib.sha256(data).hexdigest())
    return result


def load(root, declared):
    if type(declared) is not dict or set(declared) != {'COPY', 'SID22'}:
        raise ValueError('the common TEST run requires exact existing COPY and SID22 preparations')
    records = {}
    for key, value in declared.items():
        if type(value) is not dict or set(value) != {'path', 'sha256'}:
            raise ValueError('the common TEST primary reference has another schema')
        path = local_paths.owned(value['path'], root).resolve()
        if not path.is_relative_to(local_paths.results_root(root)):
            raise ValueError('the TEST primary reference escapes tmp/local-results')
        data = copy_evidence.read_output(root, value['path'])
        if hashlib.sha256(data).hexdigest() != value['sha256']:
            raise ValueError('the TEST primary prepared bytes changed')
        records[key] = json.loads(data)
    return Primary.from_record(records['COPY'], sid22=records['SID22'])


@dataclass(frozen=True)
class Primary:
    record_text: str
    sid22_text: str | None = None

    @classmethod
    def from_record(cls, record, *, sid22=None):
        return cls(test_contract.json_text(record),
                   None if sid22 is None else test_contract.json_text(sid22))

    def packet(self):
        value = json.loads(self.record_text)
        if type(value) is not dict:
            raise ValueError('TEST semantic execution requires its original shared GNU record')
        return value

    def sid22_packet(self):
        if self.sid22_text is None:
            raise ValueError('the TEST fact requires the original shared SID22 record')
        value = json.loads(self.sid22_text)
        if type(value) is not dict:
            raise ValueError('the TEST SID22 primary has another record schema')
        return value

    def require(self, model):
        """Revalidate original sources, full matrices, process and stream bytes."""
        record = self.packet()
        from kb import packed_transfer_capture_evidence
        supplemental = packed_transfer_capture_evidence.require_primary(model, record)
        from kb import width_view_capture_evidence
        supplemental['width_views'] = width_view_capture_evidence.require_primary(model, record)
        from kb import byte_surface_capture_evidence
        supplemental['byte_surface_paths'] = byte_surface_capture_evidence.require_primary(model, record)
        from kb import exhaust_target_capture_evidence
        supplemental['exhaust_target_paths'] = exhaust_target_capture_evidence.require_primary(model, record)
        from kb import bfs_path_capture_evidence
        supplemental['bfs_paths'] = bfs_path_capture_evidence.require_primary(model, record)
        from kb import ignition_diagnostic_capture_evidence
        supplemental['ignition_diagnostic_paths'] = ignition_diagnostic_capture_evidence.require_primary(model, record)
        from kb import publication_inhibit_capture_evidence
        supplemental['publication_inhibit_paths'] = publication_inhibit_capture_evidence.require_primary(model, record)
        from kb import division_callees_capture_evidence
        supplemental['division_callees_paths'] = division_callees_capture_evidence.require_primary(model, record)
        from kb import timing_division_capture_evidence
        supplemental['timing_division_paths'] = timing_division_capture_evidence.require_primary(model, record)
        from kb import timing_tail_capture_evidence
        supplemental['timing_tail_paths'] = timing_tail_capture_evidence.require_primary(model, record)
        from kb import calculation_dependency_evidence
        calculations = calculation_dependency_evidence.require_primary(model, record)
        supplemental.update(calculations['components'])
        supplemental['calculation_dependencies'] = calculations
        from kb import timing_argument_evidence
        supplemental['timing_arguments'] = timing_argument_evidence.require_primary(model, record)
        from kb import snapshot_rom_evidence
        supplemental['snapshot_ROM_dependency'] = snapshot_rom_evidence.require_primary(model, record)
        from kb import io_access_evidence
        io_accesses = io_access_evidence.require_primary(model, record)
        supplemental['io_access_paths'] = io_accesses['component']
        supplemental['io_accesses'] = io_accesses
        from kb import maf_access_evidence
        maf = maf_access_evidence.require_primary(model, record)
        supplemental.update(maf['components'])
        supplemental['maf_accesses'] = maf
        result = dict(process_path=record['process_path'], process_sha256=record['process_sha256'],
                    stdout_sha256=record['terminal']['stdout_sha256'],
                    stderr_sha256=record['terminal']['stderr_sha256'],
                    candidate_digest=test_contract.digest(record['candidate']))
        result.update(supplemental)
        if self.sid22_text is not None:
            from kb import sid22_evidence
            sid = self.sid22_packet()
            member = sid22_evidence.descriptor(model.root).members[0]
            symbol = model.symbols.get(SymbolKey('7mfk', 'ram', member.address))
            failure = sid22_evidence.failure(sid22_evidence.item(member.meaning),
                symbol, model, 'identity', record=sid)
            if failure:
                raise ValueError(failure)
            if (not test_contract.exact(sid['terminal'], record['terminal'])
                    or sid['process_path'] != record['process_path']
                    or sid['process_sha256'] != record['process_sha256']
                    or sid['native_model'] != record['native_model']):
                raise ValueError('the TEST semantic adapters name different original GNU executions')
            result['SID22_candidate_digest'] = test_contract.digest(sid['candidate'])
            result['diagnostic_width_views'] = width_view_capture_evidence.diagnostic_views(model, sid)
            from kb import diagnostic_rom_evidence
            result['diagnostic_ROM_dependencies'] = diagnostic_rom_evidence.require_primary(model,record,sid)
        return result

    def available_regions(self):
        """Keep existing witness protocols distinct from additional raw captures."""
        witness = self.packet()['candidate']['witness']
        regions = {witness['region'], witness['snapshot']['region']}
        regions.update(row['region'] for row in witness['coherent']['windows'])
        if 'ignition_literals' in witness:
            from kb import ignition_literal_evidence
            regions.add(ignition_literal_evidence.REGION)
        if 'packed_transfers' in witness:
            regions.update(row['declaration']['region'] for row in witness['packed_transfers'].values())
        if 'width_views' in witness:
            regions.add(witness['width_views']['declaration']['region'])
        if 'byte_surface_paths' in witness:
            regions.add(witness['byte_surface_paths']['declaration']['region'])
        if 'exhaust_target_paths' in witness:
            regions.add(witness['exhaust_target_paths']['declaration']['region'])
        if 'bfs_paths' in witness:
            regions.add(witness['bfs_paths']['declaration']['region'])
        if 'ignition_diagnostic_paths' in witness:
            regions.add(witness['ignition_diagnostic_paths']['declaration']['region'])
        if 'publication_inhibit_paths' in witness:
            regions.add(witness['publication_inhibit_paths']['declaration']['region'])
        if 'division_callees_paths' in witness:
            regions.add(witness['division_callees_paths']['declaration']['region'])
        if 'timing_division_paths' in witness:
            regions.add(witness['timing_division_paths']['declaration']['region'])
        if 'timing_tail_paths' in witness:
            regions.add(witness['timing_tail_paths']['declaration']['region'])
        if 'timing_denominator_paths' in witness:
            regions.add(witness['timing_denominator_paths']['declaration']['region'])
        if 'signed_curve_paths' in witness:
            regions.add(witness['signed_curve_paths']['declaration']['region'])
        if 'fine_gopher_paths' in witness:
            regions.add(witness['fine_gopher_paths']['declaration']['region'])
        if 'independent_leopard_paths' in witness:
            regions.add(witness['independent_leopard_paths']['declaration']['region'])
        if 'uptight_duck_paths' in witness:
            regions.add(witness['uptight_duck_paths']['declaration']['region'])
        if 'apc_reset_offset_paths' in witness:
            regions.add(witness['apc_reset_offset_paths']['declaration']['region'])
        if 'quiet_cat_paths' in witness:
            regions.add(witness['quiet_cat_paths']['declaration']['region'])
        if 'sexy_tamarin_paths' in witness:
            regions.add(witness['sexy_tamarin_paths']['declaration']['region'])
        if 'viridian_armadillo_paths' in witness:
            regions.add(witness['viridian_armadillo_paths']['declaration']['region'])
        if 'rugged_gerbil_paths' in witness:
            regions.add(witness['rugged_gerbil_paths']['declaration']['region'])
        if 'spirited_hamster_paths' in witness:
            regions.add(witness['spirited_hamster_paths']['declaration']['region'])
        if 'arrogant_catfish_paths' in witness:
            regions.add(witness['arrogant_catfish_paths']['declaration']['region'])
        if 'scaled_publication_paths' in witness:
            regions.add(witness['scaled_publication_paths']['declaration']['region'])
        if 'normalization_paths' in witness:
            regions.add(witness['normalization_paths']['declaration']['region'])
        if 'differential_curve_paths' in witness:
            regions.add(witness['differential_curve_paths']['declaration']['region'])
        if 'reciprocal_curves_paths' in witness:
            regions.add(witness['reciprocal_curves_paths']['declaration']['region'])
        if 'counter_threshold_paths' in witness:
            regions.add(witness['counter_threshold_paths']['declaration']['region'])
        if 'messy_roadrunner_paths' in witness:
            regions.add(witness['messy_roadrunner_paths']['declaration']['region'])
        if 'radical_capuchin_paths' in witness:
            regions.add(witness['radical_capuchin_paths']['declaration']['region'])
        if 'adorable_llama_paths' in witness:
            regions.add(witness['adorable_llama_paths']['declaration']['region'])
        if 'io_access_paths' in witness:
            regions.add(witness['io_access_paths']['declaration']['region'])
        if 'maf_copy_filter_paths' in witness:
            regions.add(witness['maf_copy_filter_paths']['declaration']['region'])
        if 'maf_extended_paths' in witness:
            regions.add(witness['maf_extended_paths']['declaration']['region'])
        if 'native_tests' in witness:
            regions.update(self.raw_regions())
        if self.sid22_text is not None:
            from kb import sid22_evidence
            regions.add(sid22_evidence.REGION)
        return regions

    def raw_regions(self, *, required=True):
        """Raw observations remain insufficient without each registered adapter."""
        witness = self.packet()['candidate']['witness']
        if 'native_tests' not in witness:
            if required:
                raise ValueError('the shared GNU original lacks native TEST raw observations')
            return {}
        packet = witness['native_tests']
        if (type(packet) is not dict
                or set(packet) != {'schema', 'kind', 'semantic_admission', 'regions'}
                or not test_contract.exact(packet['schema'], 1)
                or packet['kind'] != 'native-test-raw'
                or packet['semantic_admission'] is not False
                or type(packet['regions']) is not list):
            raise ValueError('the shared GNU packet lacks its raw native TEST observations')
        regions = {}
        for region in packet['regions']:
            if type(region) is not dict or type(region.get('region')) is not dict:
                raise ValueError('the native TEST raw packet has another region schema')
            key = region['region'].get('key')
            if type(key) is not str or not key or key in regions:
                raise ValueError('the native TEST raw packet repeats or omits a region identity')
            regions[key] = region
        return regions
