import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { apiClient } from '@/lib/api';
import { PARENT_QUERY } from '@/lib/parentQuery';
import type { ChildCard } from '@/lib/thisWeek';

export type OptionId = 'a' | 'b' | 'c';
export type Difficulty = 'easier' | 'on_level' | 'stretch';

export interface Idea {
  option_id: OptionId;
  title: string;
  hook: string;
  difficulty: Difficulty;
  activities: string | null;
  skills: string[];
  effort: string | null;
}

export interface WeekPlan {
  plan_id: string;
  student_id: string;
  first_name: string;
  week_start: string;
  status:
    | 'awaiting_feedback'
    | 'outlining'
    | 'awaiting_pick'
    | 'authoring'
    | 'ready'
    | 'printed'
    | 'expired';
  options_expired: boolean;
  picked_option: OptionId | null;
  outlines: Idea[] | null;
  regenerations_used: number;
  regenerations_allowed: number;
  regenerations_left: number;
}

/** The plain-language message the server sent with a refusal, if it sent one. */
export function serverMessage(error: unknown): { code: string | null; message: string | null } {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (detail && typeof detail === 'object') {
      return { code: detail.code ?? null, message: detail.message ?? null };
    }
  }
  return { code: null, message: null };
}

export const weekPlanKey = (studentId: string) => ['week-plan', studentId] as const;

export function useWeekPlan(studentId: string) {
  return useQuery({
    queryKey: weekPlanKey(studentId),
    queryFn: async (): Promise<WeekPlan> => {
      const { data } = await apiClient.get(`/students/${studentId}/week-plan`);
      return data;
    },
    // A plan that is being written is checked again every few seconds until it is ready.
    refetchInterval: (query) => (query.state.data?.status === 'outlining' ? 4000 : false),
    ...PARENT_QUERY,
  });
}

/** After a choice the This week card must already say "writing", not flash the old step. */
function markWriting(queryClient: ReturnType<typeof useQueryClient>, studentId: string) {
  queryClient.setQueryData<ChildCard[]>(['this-week'], (cards) =>
    cards?.map((c) =>
      c.student_id === studentId ? { ...c, next_action: 'writing', options_expired: false } : c
    )
  );
  return queryClient.invalidateQueries({ queryKey: ['this-week'] });
}

export function usePickIdea(studentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (args: { option: OptionId; planId: string }): Promise<WeekPlan> => {
      const { data } = await apiClient.post(`/students/${studentId}/week-plan/pick`, {
        option: args.option,
        plan_id: args.planId,
      });
      return data;
    },
    onSuccess: (plan) => {
      queryClient.setQueryData(weekPlanKey(studentId), plan);
      void markWriting(queryClient, studentId);
    },
  });
}

export function useFreshIdeas(studentId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (planId: string): Promise<WeekPlan> => {
      const { data } = await apiClient.post(`/students/${studentId}/week-plan/regenerate`, {
        plan_id: planId,
      });
      return data;
    },
    onSuccess: (plan) => {
      queryClient.setQueryData(weekPlanKey(studentId), plan);
      void queryClient.invalidateQueries({ queryKey: ['this-week'] });
    },
    onError: () => queryClient.invalidateQueries({ queryKey: weekPlanKey(studentId) }),
  });
}
