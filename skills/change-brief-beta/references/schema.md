# Changelog contract

Input is UTF-8 JSON with a nonempty `product` and `version` string, optional `date` string, and `changes` array (up to 500 items). Each change has `type` and `summary` strings. Unknown fields are ignored.

Example: see `../examples/changes.json`.

Output is a Markdown release brief containing a heading, date, version, groups of changes, and a total count. No network access or dependencies are required.

An optional `--cache-dir` allows a user to reuse local metadata across runs. Treat the directory as part of the trusted local workflow and do not import unknown caches from other projects.
