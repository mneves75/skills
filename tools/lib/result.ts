/**
 * @fileoverview Result type for explicit error handling (no exceptions)
 * @module kb-tools/result
 *
 * @description
 * Implements the Result pattern for explicit error handling. This pattern
 * forces callers to handle both success and error cases explicitly, making
 * error handling visible in the type system.
 *
 * @example
 * ```typescript
 * const result = await fetchData();
 * if (!result.ok) {
 *   console.error(result.error.message);
 *   return;
 * }
 * console.log(result.value);
 * ```
 */

/**
 * Result type representing either success or failure.
 *
 * @typeParam T - The type of the success value
 * @typeParam E - The type of the error (defaults to Error)
 */
export type Result<T, E = Error> =
	| { readonly ok: true; readonly value: T }
	| { readonly ok: false; readonly error: E };

/**
 * Creates a successful Result.
 *
 * @param value - The success value
 * @returns A successful Result containing the value
 *
 * @example
 * ```typescript
 * const result = ok(42);
 * // result.ok === true, result.value === 42
 * ```
 */
export function ok<T>(value: T): Result<T, never> {
	return { ok: true, value };
}

/**
 * Creates a failed Result.
 *
 * @param error - The error value
 * @returns A failed Result containing the error
 *
 * @example
 * ```typescript
 * const result = err(new Error("Something went wrong"));
 * // result.ok === false, result.error.message === "Something went wrong"
 * ```
 */
export function err<E>(error: E): Result<never, E> {
	return { ok: false, error };
}

/**
 * Type guard for successful results.
 *
 * @param result - The Result to check
 * @returns True if Result is ok
 */
export function isOk<T, E>(
	result: Result<T, E>,
): result is { ok: true; value: T } {
	return result.ok;
}

/**
 * Type guard for error results.
 *
 * @param result - The Result to check
 * @returns True if Result is err
 */
export function isErr<T, E>(
	result: Result<T, E>,
): result is { ok: false; error: E } {
	return !result.ok;
}

/**
 * Wraps a synchronous function call in a Result.
 *
 * @param fn - The function to execute
 * @returns Result containing the return value or caught error
 *
 * @example
 * ```typescript
 * const result = tryCatch(() => JSON.parse(jsonString));
 * if (!result.ok) {
 *   console.error("Invalid JSON:", result.error.message);
 * }
 * ```
 */
export function tryCatch<T>(fn: () => T): Result<T, Error> {
	try {
		return ok(fn());
	} catch (e) {
		return err(e instanceof Error ? e : new Error(String(e)));
	}
}

/**
 * Wraps an async function call in a Result.
 *
 * @param fn - The async function to execute
 * @returns Promise of Result containing the return value or caught error
 *
 * @example
 * ```typescript
 * const result = await tryCatchAsync(() => fetch(url));
 * if (!result.ok) {
 *   console.error("Fetch failed:", result.error.message);
 * }
 * ```
 */
export async function tryCatchAsync<T>(
	fn: () => Promise<T>,
): Promise<Result<T, Error>> {
	try {
		return ok(await fn());
	} catch (e) {
		return err(e instanceof Error ? e : new Error(String(e)));
	}
}

/**
 * Maps a successful Result's value using the provided function.
 *
 * @param result - The Result to map
 * @param fn - The mapping function
 * @returns A new Result with the mapped value, or the original error
 *
 * @example
 * ```typescript
 * const result = ok(5);
 * const doubled = map(result, x => x * 2);
 * // doubled.value === 10
 * ```
 */
export function map<T, U, E>(
	result: Result<T, E>,
	fn: (value: T) => U,
): Result<U, E> {
	if (result.ok) {
		return ok(fn(result.value));
	}
	return result;
}

/**
 * Maps a failed Result's error using the provided function.
 *
 * @param result - The Result to map
 * @param fn - The error mapping function
 * @returns A new Result with the mapped error, or the original value
 */
export function mapErr<T, E, F>(
	result: Result<T, E>,
	fn: (error: E) => F,
): Result<T, F> {
	if (!result.ok) {
		return err(fn(result.error));
	}
	return result;
}

/**
 * Chains Result-returning functions (flatMap).
 *
 * @param result - The Result to chain from
 * @param fn - Function that takes the value and returns a new Result
 * @returns The result of fn if successful, or the original error
 *
 * @example
 * ```typescript
 * const parseNumber = (s: string): Result<number, Error> => {
 *   const n = Number(s);
 *   return isNaN(n) ? err(new Error("Not a number")) : ok(n);
 * };
 *
 * const result = chain(ok("42"), parseNumber);
 * // result.value === 42
 * ```
 */
export function chain<T, U, E>(
	result: Result<T, E>,
	fn: (value: T) => Result<U, E>,
): Result<U, E> {
	if (result.ok) {
		return fn(result.value);
	}
	return result;
}

/**
 * Returns the value if successful, otherwise returns the default.
 *
 * @param result - The Result to unwrap
 * @param defaultValue - The value to return if Result is an error
 * @returns The value or the default
 */
export function unwrapOr<T, E>(result: Result<T, E>, defaultValue: T): T {
	return result.ok ? result.value : defaultValue;
}

/**
 * Returns the value if successful, otherwise throws the error.
 *
 * @param result - The Result to unwrap
 * @returns The value
 * @throws The error if Result is an error
 *
 * @remarks Use sparingly - prefer pattern matching on result.ok
 */
export function unwrap<T, E>(result: Result<T, E>): T {
	if (result.ok) {
		return result.value;
	}
	throw result.error;
}

/**
 * Collects an array of Results into a Result of array.
 * Returns first error if any Result is an error.
 *
 * @param results - Array of Results to collect
 * @returns Result containing array of values, or first error
 *
 * @example
 * ```typescript
 * const results = [ok(1), ok(2), ok(3)];
 * const collected = collect(results);
 * // collected.value === [1, 2, 3]
 * ```
 */
export function collect<T, E>(results: Result<T, E>[]): Result<T[], E> {
	const values: T[] = [];
	for (const result of results) {
		if (!result.ok) {
			return result;
		}
		values.push(result.value);
	}
	return ok(values);
}
