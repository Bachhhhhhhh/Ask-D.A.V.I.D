# Goal 4 remediation exclusion marker

This directory intentionally contains no executable SQL. The bundle keeps an
explicit `sync.exclude` for this path so a future approval-only remediation
cannot be synchronized accidentally. Do not add executable SQL here without a
new reviewed remediation and connected approval.
