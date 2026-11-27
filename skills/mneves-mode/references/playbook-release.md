# Playbook: release and deploy

Plain "ship" never authorizes a deploy. A deploy needs an explicit `ship-staging` or
`ship-prod`. Every gate runs on the exact candidate commit, in this order:

1. **Release record.** Bump the version, update the changelog and docs, commit and push on a
   working branch.
2. **Security verdict (mandatory).** `mneves-security` gives an exact-commit pass, or a waiver
   by name from the authority the governing rule names. If the skill is missing or acceptance
   fails, the deploy is blocked.
3. **Readiness (mandatory for staging and production).** `mneves-production-readiness`. It
   imports the security rows and checks the rest:
   - data, recovery, cost, operations and ownership;
   - the candidate's identity and preview bindings that can write;
   - the observation window;
   - where a code rollback cannot undo a state change.
4. **Merge.** Only with the user's authorization in this request. Then delete the branch and
   the worktree the task created. Tag here only for a release that nothing deploys.
5. **Deploy, prove live, then tag.** `mneves-ship-deploy` deploys the gated artifact, checks the
   live version against the candidate, and only then tags it. After production succeeds, tear
   down the staging resources the release started.

If a required gate's skill is unavailable, report `BLOCKED`. Stop before merging, deploying or
tagging, and never fabricate a gate record.
