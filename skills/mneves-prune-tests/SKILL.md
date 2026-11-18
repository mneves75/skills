---
name: mneves-prune-tests
description: Delete or rewrite tests that guard no behavior, with evidence for each change. Use when asked to prune, trim or de-duplicate a test suite.
license: MIT
---

# Prune tests

Prune every test in scope that guards no behavior.

**0. Fix the scope and the baseline**

- Scope is the path the user named. With no path, list candidates across the repository and
  prune only after the user confirms that list; never prune a whole repository unasked.
- Running a suite executes the repository's code. Run it only in a repository the user trusts
  or in an isolated environment (no secrets, no network, writes confined); otherwise ask first.
  With no named path, run nothing until the user confirms the candidate list.
- Run the suite in scope first and record the result. A test that already fails or is known
  to be flaky (marked, quarantined or seen failing intermittently) is not a prune candidate:
  report it and leave it for its own fix. A skipped test is a candidate only under "The past".

**1. Find what each test depends on**

Keep a test only if it depends on the intended behavior: it should change only when that behavior changes, and fail only when it regresses.

If another test already guards the same behavior, prune the copy. Name the test that stays,
and confirm it fails on the regression the copy would catch: plant it, or show the two use the
same inputs, setup, layer (unit, integration, end to end) and assertion. A copy that runs at
another layer or through another boundary guards that boundary too: keep it unless the plant shows
the survivor catches the same regression.

Prune tests that depend on:

**The past:** it guards code that no longer exists, so it has no reason of its own to change.

For example:

- A feature was removed, and tests assert it's gone. Removed code never changes, so they can't catch a regression.
- A module was moved, and a test asserts it's absent from its old path.

Absence is not always the past. A test that asserts something is refused, rejected or must not
come back as a standing rule (a security regression test, an invariant guard, a planted-violation
control for a checker) guards behavior: keep it. It is a standing rule when a spec, ADR,
advisory, issue or comment names it as a requirement, or live code could bring it back; when
unsure, list it as a candidate and ask.

**Nothing:** no change to the code can make it fail, so it has no reason of its own to change.

For example:

- It tests the browser: a `<button>` renders, or a click event fires. The browser is already tested.
- It mocks the unit under test, then asserts what the mock returns.
- It asserts what the type system already guarantees.

**The implementation:** it changes whenever the code does, even when behavior didn't.

For example:

- The expected value is derived from the same logic as the code, so a wrong result still passes.
- It asserts private state, internal call order, or which helper was invoked.

**2. Prune**

- Delete every test that isn't anchored to intended behavior.
- Where one also covers behavior something relies on, rewrite it against that behavior instead.
  Prove each rewrite: break that behavior on purpose, watch the rewritten test fail on its own
  assertion, then revert only your planted edit and check the file matches its prior diff.
- Delete production code that only existed for the tests you removed, only inside the scope
  from step 0; production code outside it (a test's named path does not cover its source module)
  is deleted only after the user confirms each item. Search for every caller
  first, counting dynamic use (string imports, reflection, registries, config, fixtures). A
  public interface (package entry point, documented API) stays unless the user agrees; a
  test-only hook with no other caller is not one.

**3. Report**

For each deleted or rewritten test, give its name, the category above, and for a duplicate the
test that stays. Run the suite again and give both results; when production code was deleted,
run the full suite, or every test that reaches the touched module. A test that newly fails means
deleted code or shared state was still in use: restore it and investigate. A passing re-run does
not prove a pruned test was redundant; the categories above do.

**What done looks like**

- Every test left is anchored to intended behavior.
- Each one would fail on a regression, and only on a regression.
- No test asserts code that no longer exists, except a standing absence guard.
- No two tests guard the same behavior.
- No production code exists only for tests.
- The suite passes as it did at the baseline, minus the pruned tests.

**Example**

```diff
--- a/pricing.test.ts
+++ b/pricing.test.ts
@@ rewritten: the expected value repeated the code's logic @@
 test("applies the discount", () => {
-  const price = 100;
-  expect(applyDiscount(price, 0.2)).toBe(price - price * 0.2);
+  expect(applyDiscount(100, 0.2)).toBe(80);
 });
--- a/cart.test.ts
+++ b/cart.test.ts
@@ rewritten against what callers see: it asserted private state @@
 test("adds an item to the cart", () => {
   const cart = new Cart();
   cart.add(book);
-  expect(cart._items.length).toBe(1);
+  expect(cart.total()).toBe(book.price);
 });
@@ deleted: checkout.test.ts already guards the same total @@
-test("total includes tax", () => {
-  expect(cartTotal([book], { tax: 0.1 })).toBe(11);
-});
--- a/export.test.ts
+++ b/export.test.ts
@@ deleted: it guards code that no longer exists @@
-test("legacy exporter is gone", () => {
-  expect(existsSync("src/export/legacy.ts")).toBe(false);
-});
--- a/session.test.ts
+++ b/session.test.ts
@@ deleted; the user confirmed removing the test-only hooks, which had no other caller @@
-test("clears the cache", () => {
-  _resetCacheForTests();
-  expect(_getCacheSize()).toBe(0);
-});
--- a/session.ts
+++ b/session.ts
@@ @@
-export function _resetCacheForTests() { cache.clear(); }
-export function _getCacheSize() { return cache.size; }
```
