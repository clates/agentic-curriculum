import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export type QuickRating = 'smooth' | 'mixed' | 'rough';
/** The feedback API's workload scale: +2 too little, 0 just right, -2 too much. */
export type Workload = 2 | 0 | -2;

export interface QuickCheckIn {
  studentId: string;
  packetId: string;
  rating: QuickRating;
  workload?: Workload;
}

export function useSendQuickCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ studentId, packetId, rating, workload }: QuickCheckIn) => {
      await apiClient.post(`/students/${studentId}/weekly-packets/${packetId}/feedback`, {
        quick_rating: rating,
        ...(workload === undefined ? {} : { workload }),
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['this-week'] }),
  });
}
