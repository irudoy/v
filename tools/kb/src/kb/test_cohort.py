"""Profile execution views of one unmodified complete pytest candidate.

A view refers to actual global collection and report positions. It never
manufactures a smaller successful run, exit status or terminal. Semantic
adapters and current native owning-context validation remain separate.
"""

from kb import test_contract


class Cohort:
    def __init__(self, registry):
        self.registry = registry
        self.contract = registry.cohort()
        self._registry = test_contract.json_text(registry.packets())
        self._contract = test_contract.json_text(self.contract.packet())

    def _current(self):
        if (test_contract.json_text(self.registry.packets()) != self._registry
                or test_contract.json_text(self.registry.cohort().packet()) != self._contract
                or test_contract.json_text(self.contract.packet()) != self._contract):
            raise ValueError('the common TEST execution obligations changed')

    def view(self, candidate, profile_key):
        """Reference original positions only after the entire cohort succeeds."""
        self._current()
        failure = self.contract.failure(candidate)
        if failure:
            raise ValueError(failure)
        profile = self.registry.profile(profile_key)
        positions = {nodeid: index for index, nodeid in enumerate(candidate['collected'])}
        case_positions = [positions[case.nodeid] for case in profile.contract.cases]
        if case_positions != sorted(set(case_positions)):
            raise ValueError('the TEST profile has another actual case order')
        report_positions = [position * len(test_contract.PHASES) + phase
                            for position in case_positions
                            for phase in range(len(test_contract.PHASES))]
        return dict(schema=1, profile=profile_key,
                    profile_digest=test_contract.digest(profile.packet()),
                    run_id=candidate['run_id'],
                    candidate_digest=test_contract.digest(candidate),
                    cohort_digest=test_contract.digest(self.contract.packet()),
                    case_positions=case_positions, report_positions=report_positions)

    def require_view(self, candidate, profile_key, view):
        if not test_contract.exact(view, self.view(candidate, profile_key)):
            raise ValueError('the TEST execution view changes its original cohort or profile scope')

    def require_terminal(self, record, root):
        """Every scoped consumer revalidates the complete original process."""
        self._current()
        failure = test_contract.terminal_failure(record, root, self.contract)
        if failure:
            raise ValueError(failure)

    def execution(self, record, root, profile_key):
        self.require_terminal(record, root)
        return self.view(record['candidate'], profile_key)
