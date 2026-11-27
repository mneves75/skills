# Playbook: release and deploy

Plain "ship" never authorizes a deploy. A deploy needs an explicit `ship-staging` or
`ship-prod`. Every gate runs on the exact candidate commit, in this order:

1. **Release record.** Bump the version, update the changelog and docs, and commit on a working
   branch. Check which pushes, merges and tags trigger a deploy; push now only if the push
   deploys nothing.
2. **Security verdict (mandatory).** `mneves-security` gives an exact-commit pass, or a waiver
   by name from the authority the governing rule names. The verdict binds to the audited tree,
   so a merge that lands a different tree needs a new one. If the skill is missing or acceptance
   fails, the deploy is blocked.
3. **Readiness (mandatory for staging and production).** `mneves-production-readiness`. It
   imports the security rows and checks the rest:
   - data, recovery, cost, operations and ownership;
   - the candidate's identity and preview bindings that can write;
   - the observation window;
   - where a code rollback cannot undo a state change.
4. **Merge.** Only with the user's authorization in this request. A merge that deploys
   production belongs to step 5: it waits for the staging proof and the owner's approval of the
   exact candidate and target. Then delete the branch and the worktree the task created. Tag
   here only for a release that nothing deploys.
5. **Deploy, prove live, then tag.** `mneves-ship-deploy` deploys the gated artifact, checks the
   live version against the candidate, and only then applies that target's tag (beta for
   staging, `vX.Y.Z` for production). After production succeeds, tear down the staging
   resources the release started.

If a required gate's skill is unavailable, report `BLOCKED`. Stop before merging, deploying or
tagging, and never fabricate a gate record.
