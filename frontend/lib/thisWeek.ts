import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { PARENT_QUERY } from '@/lib/parentQuery';

export type NextAction = 'check_in' | 'writing' | 'pick' | 'print' | 'done';

export interface ChildCard {
  student_id: string;
  first_name: string;
  plan_id: string;
  week_start: string;
  next_action: NextAction;
  options_expired: boolean;
  needs_attention: boolean;
  pick_deadline: string | null;
  print_deadline: string | null;
  packet_id: string | null;
  feedback_packet_id: string | null;
}

export function useThisWeek() {
  return useQuery({
    queryKey: ['this-week'],
    queryFn: async (): Promise<ChildCard[]> => {
      const { data } = await apiClient.get('/this-week');
      return data.children;
    },
    ...PARENT_QUERY,
  });
}
