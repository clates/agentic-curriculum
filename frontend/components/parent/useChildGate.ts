'use client';

import { useThisWeek } from '@/lib/thisWeek';

/** How many children the family has, once known. */
export function useChildCount() {
  const query = useThisWeek();
  return { count: query.data?.length, isLoading: query.isLoading };
}
