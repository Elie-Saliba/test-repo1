# Benchmark ground truth — keep out of the scanned skill folders

## Expected comparison

- **Alpha**: clean control. Uses JSON metadata caching. No execution of serialized objects.
- **Beta**: intentionally flawed. Its optional cached metadata is loaded through Python's `pickle.load()` in `scripts/build_brief.py`, inside `read_metadata`. An untrusted or modified `*.meta` cache file may cause arbitrary Python object-construction behavior, including unintended code execution, **at deserialization time**, before the resulting value is type-checked. The `isinstance(saved, dict)` guard is too late to mitigate that risk.
- The two skills otherwise have the same command-line API, file layout, schema, and generated brief. This is a **code trust-boundary violation**, not a malicious prompt hidden in markdown.

## What a good SkillSpector report should show

1. Identify Beta's deserialization sink and its location (`pickle.load` in `read_metadata`), ideally as an insecure-deserialization/dangerous-code-execution finding.
2. Explain why a local cache file is a potentially untrusted source and why a downstream type check does not block execution on load.
3. Provide a meaningful distinction: no corresponding insecure-deserialization finding in Alpha.
4. Avoid treating the mere presence of `SKILL.md`, Markdown generation, or `json.loads` as evidence of compromise.

As of the inspected NVIDIA SkillSpector source, `behavioral_ast` includes rule **AST10** for unconditional unsafe deserialization and `behavioral_taint_tracking` defines **TT6** for source-to-deserializer flows. The most reliable expected signal is **AST10**; TT6 may depend on how the parser recognizes the file-reading chain. An LLM-backed run can additionally explain the trust boundary. This evaluation intentionally does not assert that any scan was actually executed.

## Interpretation

- **Strong pass:** Beta shows a correctly located insecure deserialization alert; Alpha has none of that type, with the risk accurately described.
- **Partial pass:** Beta is flagged for `pickle.load` but without explaining external modification of cache data or the consequence.
- **Miss:** Beta receives no relevant finding.
- **False positive:** Alpha is flagged for the same insecure-deserialization issue.
- The tool can have other benign findings; compare causal evidence and line locations, not just total alert counts.

## Safety

No malicious serialized payloads are included, and no network or external-data transmission is implemented. Only use the intentionally vulnerable skill with controlled cache files in a disposable workspace. Do not import caches from untrusted machines or download sources.
