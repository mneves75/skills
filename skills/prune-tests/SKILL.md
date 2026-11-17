---
name: prune-tests
description: Delete or rewrite tests that guard no behavior, with evidence for each change. Use when asked to prune, trim or de-duplicate a test suite.
license: MIT
---

# Prune tests

Prune every test in scope that guards no behavior.

**0. Fix the scope and the baseline**

- Scope is the path the user named. With no path, list candidates across the repository and
  prune only after the user confirms that list; never prune a whole repository unasked.
- Run the suite in scope first and record the result. A test that already fails, is skipped
  or is flaky is not a prune candidate: report it and leave it for its own fix.

**1. Find what each test depends on**

Keep a test only if it depends on the intended behavior: it should change only when that behavior changes, and fail only when it regresses.

If another test already guards the same behavior, prune the copy. Name the test that stays.

Prune tests that depend on:

**The past:** it guards code that no longer exists, so it has no reason of its own to change.

For example:

- A feature was removed, and tests assert it's gone. Removed code never changes, so they can't catch a regression.
- A module was moved, and a test asserts it's absent from its old path.

Absence is not always the past. A test that asserts something is refused, rejected or must not
come back as a standing rule (a security regression test, an invariant guard, a planted-violation
control for a checker) guards behavior: keep it.

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
  assertion, then restore the code.
- Delete production code that only existed for the tests you removed. Search for every caller
  first; an exported or documented interface stays unless the user agrees to remove it.

**3. Report**

For each deleted or rewritten test, give its name, the category above, and for a duplicate the
test that stays. Run the suite again and give both results; a test that newly fails means a
pruned test was guarding behavior, so restore it.

**What done looks like**

- Every test left is anchored to intended behavior.
- Each one would fail on a regression, and only on a regression.
- No test asserts code that no longer exists.
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
@@ deleted, with the production code that only existed for it @@
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
