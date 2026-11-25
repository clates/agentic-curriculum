import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { PARENT_QUERY } from '@/lib/parentQuery';
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

/** Both check-ins post to the week's feedback, with the workload only when the parent gave one. */
function useSendFeedback<A extends { studentId: string; packetId: string; workload?: Workload }>(
  body: (args: A) => object
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (args: A) => {
      await apiClient.post(`/students/${args.studentId}/weekly-packets/${args.packetId}/feedback`, {
        ...body(args),
        ...(args.workload === undefined ? {} : { workload: args.workload }),
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['this-week'] }),
  });
}

export const useSendQuickCheckIn = () =>
  useSendFeedback((args: QuickCheckIn) => ({ quick_rating: args.rating }));

export interface PrepCheck {
  check_id: string;
  day: string;
  prompt: string;
  pass_criteria: string;
}

export type CheckResult = 'got_it' | 'shaky' | 'missed';

export function usePrepChecks(studentId: string, packetId: string | null | undefined) {
  return useQuery({
    queryKey: ['prep-checks', studentId, packetId],
    enabled: !!packetId,
    queryFn: async (): Promise<PrepCheck[]> => {
      const { data } = await apiClient.get(
        `/students/${studentId}/weekly-packets/${packetId}/checks`
      );
      return data.checks;
    },
    ...PARENT_QUERY,
  });
}

export const useSendCheckResults = () =>
  useSendFeedback(
    (args: {
      studentId: string;
      packetId: string;
      results: Record<string, CheckResult>;
      workload?: Workload;
    }) => ({ check_results: args.results })
  );
