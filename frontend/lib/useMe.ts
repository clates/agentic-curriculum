import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface Me {
  auth_required: boolean;
  user: { username: string } | null;
  permissions: string[];
}

/** Who is signed in, and what they may do. Shared by every component that asks. */
export function useMe() {
  return useQuery<Me>({
    queryKey: ['me'],
    queryFn: async () => (await apiClient.get<Me>('/auth/me')).data,
  });
}
