/** A parent on a phone should see the error state in about a second, not after seven retries. */
export const PARENT_QUERY = { retry: 1, retryDelay: 400 } as const;
