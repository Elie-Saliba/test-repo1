# Agent Skill Security Benchmark

Two independent AI-agent skills that turn a JSON change log into a Markdown release brief. They have matching descriptions, sample inputs, and user-facing behavior; one implementation contains an intentionally planted security weakness for evaluating NVIDIA SkillSpector.

## Layout

- `skills/change-brief-alpha/`: standalone agent skill (`SKILL.md`, `scripts/`, `examples/`)
- `skills/change-brief-beta/`: standalone agent skill (`SKILL.md`, `scripts/`, `examples/`)
- `evaluation/ANSWER_KEY.md`: ground truth and expected findings **(do not include in either skill's scan scope)**
- `evaluation/verify_benchmark.py`: offline functional smoke checks

## Scan with NVIDIA SkillSpector

```bash
git clone https://github.com/Elie-Saliba/test-repo1.git
cd test-repo1

# Compare the two skills independently (static checks only):
skillspector scan ./skills/change-brief-alpha --no-llm --format json
skillspector scan ./skills/change-brief-beta --no-llm --format json

# Or scan the two-skill collection:
skillspector scan ./skills --recursive --no-llm --format json
```

To include optional semantic analysis, omit `--no-llm` after configuring a supported model provider. Scan each **skill directory** (not only the `SKILL.md` file), because the bundled Python code is material to this benchmark.

The repository root is a *collection*, not a single skill; cloning and scanning `./skills --recursive` is the documented way to compare both. Do not scan `evaluation/` as a skill. The individual skill folders are also suitable for making separate ZIP archives and scanning them independently.

## Exercise both skills

From either `skills/change-brief-*/` directory:

```bash
python3 scripts/build_brief.py --input examples/changes.json --output release-brief.md --cache-dir .cache
```

The tools use only the Python standard library, operate offline, and require no external accounts. The optional cache is part of the test surface. Execute only in a disposable test workspace, and do not load third-party cache artifacts.

```bash
python3 evaluation/verify_benchmark.py
```

See `evaluation/ANSWER_KEY.md` **after** reviewing the SkillSpector results.
