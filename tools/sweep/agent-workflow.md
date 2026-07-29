# Provider-neutral caller experiment workflow

`agent_protocol.py` defines the execution protocol for the `closure-v1`
caller-semantics experiment. `agent_workflow.py` is a local state processor for that
protocol. Neither file launches an agent, imports a vendor SDK, selects a provider, or
sends data off the machine.

The experiment control plane remains `caller_ab_experiment.py`. It creates and validates
the private manifest, blinded artifacts, worklists, condition mapping, cards, scoring
inputs, and final comparison. The neutral workflow only replaces the Claude-specific
execution and archive layer.

## Boundary

The workflow has three roles:

1. The control plane creates an immutable execution JSON document.
2. An operator-selected agent environment executes every task in a generated batch.
3. The neutral protocol validates result bundles and assembles a complete agent-run
   archive for the control plane.

An agent environment may be Claude Code, Codex, another hosted agent, or a local model.
Provider-specific code is an adapter outside the experiment protocol. A native agent
session can act as the adapter directly; no launcher wrapper is required.

One experiment must use the exact same executor descriptor for prep, both opaque arms,
and blind scoring. Changing provider, backend, model, effort, adapter, or adapter version
changes the executor identity and is rejected.

## Registered closure-v1 outcome

The registered run `ar_e4757e629bc7d606a54fe869` closed without an effect estimate on
2026-07-30. The executor
`openai/codex-cli-chatgpt/gpt-5.6-terra:medium@codex-exec-json-schema:0.146.0`
completed five Prep Analyze and five Prep Verify calls. Both result bundles pass the
provider-neutral schema, executor, receipt, raw-output digest, freshness, and no-tools
checks.

Adversarial Verify accepted two of five caller cards and refuted three. Caller
`000bef6e` also contains a citation excerpt that differs from the assigned artifact
indentation. Consequently, `validate-prep` rejects the archive and the mandatory Prep
gate prevents card finalization. Opaque arms and scoring did not run, so the experiment
has no paired contrast or causal result. The remaining 48 calls are intentionally absent.
This frozen run cannot be retried or continued; a future attempt is a new preregistered
experiment.

The private frozen artifacts and raw outputs remain outside Git under
`~/tools/ghidra-projects/vq-caller-experiments/closure-v1-20260730-prep-failed/`.
The `closure-v1-prep-failed.tar.gz` SHA-256 is
`1a80ddf7ae06a444c187c7ec611ec872bb514ee02861e1f16b2de0d25c70f8f0`.

## Frozen task policy

Every task has this policy:

```json
{
  "context": "isolated_per_task",
  "tools": "none",
  "structured_output": "json_schema",
  "fresh_invocation": true,
  "fallback": false,
  "retry_count": 0,
  "cache_reuse": false
}
```

Only `task.prompt` and `task.response_schema` are supplied to a worker. Routing IDs,
condition meaning, private truth, repository state, other tasks, and previous sessions
remain outside the worker context. A Verify prompt contains only its exact Analyze
payload and the same assigned artifact.

`tools: none` means no domain or repository tools. A platform-internal structured-output
submission mechanism is transport, not a domain tool; the receipt records
`domain_tool_calls: 0`.

## Result bundle

The selected agent environment writes one `vq.agent-task-results/v1` object per batch:

```json
{
  "schema": "vq.agent-task-results/v1",
  "batch_sha256": "<SHA-256 of the complete task batch>",
  "executor": {
    "schema": "vq.agent-executor/v1",
    "provider": "<provider>",
    "backend": "<agent runtime>",
    "model": "<resolved model, not an alias>",
    "effort": "<resolved effort>",
    "adapter": "<native environment or adapter name>",
    "adapter_version": "<exact version>"
  },
  "operator_attested": true,
  "results": [
    {
      "task_id": "<exact batch task ID>",
      "status": "completed",
      "response": {},
      "receipt": {
        "invocation_id": "<unique fresh invocation ID>",
        "fresh": true,
        "fallback": false,
        "retry_count": 0,
        "cache_reuse": false,
        "domain_tool_calls": 0,
        "input_tokens": null,
        "output_tokens": null,
        "duration_ms": null,
        "cost_usd": null,
        "raw_output": {},
        "raw_output_sha256": "<SHA-256 of canonical raw_output JSON>"
      }
    }
  ]
}
```

`response` must match the task's embedded JSON Schema exactly. Usage values may be null
when the runtime does not expose them. `raw_output` contains the unmodified executor
output available to the adapter; its digest uses sorted compact JSON as implemented by
`agent_protocol.value_sha256`.

The neutral receipt is an operator-attested local record, not independent provider
attestation. A provider-native adapter may retain additional raw logs outside the
archive, but those logs are not portable protocol fields.

## Frozen closure-v1 sequence

The frozen closure profile contains six exposed maps, two identical-input controls, and
five unique direct callers. One complete run contains 58 fresh agent invocations:

- prep Analyze: 5;
- prep Verify: 5;
- map Analyze: 8 per opaque arm, 16 total;
- map Verify: 8 per opaque arm, 16 total;
- arm-blind semantic score: 16.

### 1. Prep Analyze

After `freeze` and `build-prep`, build the first neutral batch:

```bash
python3 tools/sweep/agent_workflow.py build-batch \
  --execution <prep-execution.json> \
  --phase analyze \
  --output <prep-analyze-batch.json>
```

Execute every task independently and create `<prep-analyze-results.json>`. Validate it:

```bash
python3 tools/sweep/agent_workflow.py validate-results \
  --batch <prep-analyze-batch.json> \
  --results <prep-analyze-results.json>
```

### 2. Prep Verify and archive

```bash
python3 tools/sweep/agent_workflow.py build-batch \
  --execution <prep-execution.json> \
  --phase verify \
  --prior-results <prep-analyze-results.json> \
  --output <prep-verify-batch.json>
```

Execute the Verify tasks and archive both result bundles:

```bash
python3 tools/sweep/agent_workflow.py archive \
  --execution <prep-execution.json> \
  --results <prep-analyze-results.json> \
  --results <prep-verify-results.json> \
  --fresh-launch-attested \
  --output <prep-agent-archive.json>
```

`validate-prep` accepts a conforming archive directly. Manual exact-payload approval
remains mandatory before `finalize-cards`.

### 3. Opaque A/B arms

`build-conditions` creates two execution documents without exposing which condition
contains approved caller text. For each document, build Analyze and Verify batches using
the same commands and archive the two bundles. Pass both agent-run archives to
`validate-run`.

The executor descriptor must match prep exactly. Controls remain byte-identical across
the two arms.

### 4. Blind scoring

After `build-score`, build the single score batch:

```bash
python3 tools/sweep/agent_workflow.py build-batch \
  --execution <score-execution.json> \
  --phase score \
  --output <score-batch.json>
```

Execute all score tasks, then archive the one result bundle. `validate-score` verifies
the archive and `compare` computes the paired contrast.

## Validation and immutability

Runtime JSON and artifacts stay outside the repository. The protocol binds:

- embedded protocol source and SHA-256;
- exact execution JSON and task-batch SHA-256;
- exact executor identity across all phases and stages;
- one unique fresh invocation per task;
- raw output digests;
- response JSON Schema;
- Analyze to Verify byte-equivalent payload linkage;
- complete task coverage with no extra result;
- no tools, fallback, retry, resume, or cache reuse.

Validate a completed neutral archive independently:

```bash
python3 tools/sweep/agent_workflow.py validate-archive \
  --execution <execution.json> \
  --archive <agent-archive.json>
```

The downstream control plane repeats archive validation, citation binding, arm-neutrality
checks, evidence grammar checks, control gates, and exact executor matching.

## Legacy full-v4 profile

The historical `full-v4` profile retains its frozen Claude Code Dynamic Workflow v3
contract and its 24-map selection. Its `.claude/workflows/vq-caller-*.js` files remain
available for validation of that frozen design.

The `closure-v1` profile uses private manifest v5, execution config v4, and this
provider-neutral protocol. It does not depend on `.claude/`, a Claude model allowlist, or
the native Claude Workflow output schema.
