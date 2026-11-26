'use client';

import { useThisWeek } from '@/lib/thisWeek';

/** Max children per family; the server enforces it too. */
export const MAX_CHILDREN = 5;

/** How many children the family has, once known. */
export function useChildCount() {
  const query = useThisWeek();
  return { count: query.data?.length, isLoading: query.isLoading };
}
