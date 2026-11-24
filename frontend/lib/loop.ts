import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

/** The loop console's API (src/loop_admin.py). An operator tool: it speaks in loop terms. */

export interface LoopStep {
  key: string;
  label: string;
  actor: 'parent' | 'system';
  state: 'done' | 'current' | 'todo' | 'expired';
}

export interface LoopAction {
  id: string;
  label: string;
  enabled: boolean;
  why_not: string;
}

export interface LoopJob {
  id: number;
  kind: string;
  state: string;
  attempts: number;
  max_attempts: number;
  last_error: string | null;
}

export interface LoopIdea {
  option_id: string;
  title: string;
  hook: string;
  topic: string | null;
  skills: number;
}

export interface LoopPlan {
  plan_id: string;
  week_start: string;
  status: string;
  picked_option: string | null;
  packet_id: string | null;
  outlines: LoopIdea[];
  jobs: LoopJob[];
}

export interface LoopChild {
  student_id: string;
  name: string;
  grade: number | null;
  plan: LoopPlan | null;
  steps: LoopStep[];
  actions: LoopAction[];
}

export interface LoopQueue {
  counts: Record<string, number>;
  ready_now: number;
  running: number;
  worker_may_be_down: boolean;
  dead: { id: number; kind: string; attempts: number; last_error: string }[];
}

export interface LoopOverview {
  loop_switch: boolean;
  children: LoopChild[];
  queue: LoopQueue;
}

export interface FeedForward {
  week_start: string;
  grade: number;
  known: { mastered: number; developing: number; rated: number };
  skills: {
    standard_id: string;
    subject: string;
    grade: number;
    description: string;
    reason: string;
  }[];
}

const KEY = ['loop-overview'];

export function useLoopOverview() {
  return useQuery({
    queryKey: KEY,
    queryFn: async () => (await apiClient.get<LoopOverview>('/loop-admin/overview')).data,
    refetchInterval: 3000,
  });
}

export function errorMessage(error: unknown): string {
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  if (detail && typeof detail === 'object' && 'message' in detail)
    return String((detail as { message: unknown }).message);
  return 'That did not work. Try again.';
}

export function useLoopAction(studentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (v: { action: string; option?: string; week?: string }) =>
      (
        await apiClient.post(`/loop-admin/students/${studentId}/actions/${v.action}`, {
          option: v.option,
          week: v.week || undefined,
        })
      ).data,
    onSettled: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useSeedDemo() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await apiClient.post('/loop-admin/seed-demo')).data,
    onSettled: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useRetryJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (jobId: number) =>
      (await apiClient.post(`/loop-admin/jobs/${jobId}/retry`)).data,
    onSettled: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useFeedForward(studentId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['loop-feed-forward', studentId],
    enabled,
    queryFn: async () =>
      (await apiClient.get<FeedForward>(`/loop-admin/students/${studentId}/feed-forward`)).data,
  });
}
