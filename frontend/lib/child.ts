import { isAxiosError } from 'axios';
import { useQuery } from '@tanstack/react-query';
import { apiClient, parseMetadata, studentsApi } from '@/lib/api';
import { PARENT_QUERY } from '@/lib/parentQuery';

export interface SubjectCoverage {
  subject: string;
  solid: number;
  shaky: number;
  to_come: number;
}

/** The child's first name. A missing or someone else's child answers 404, so `data` stays empty. */
export function useChildName(studentId: string) {
  return useQuery({
    queryKey: ['child-name', studentId],
    queryFn: async (): Promise<string> => {
      const { data } = await apiClient.get(`/student/${studentId}`);
      const name = parseMetadata(data.metadata_blob)?.name ?? '';
      return name.trim().split(/\s+/)[0] ?? '';
    },
    ...PARENT_QUERY,
  });
}

/** Per subject, counts of solid, shaky and still-to-come skills. */
export function useCoverage(studentId: string) {
  return useQuery({
    queryKey: ['coverage', studentId],
    queryFn: async (): Promise<SubjectCoverage[]> => {
      const { data } = await apiClient.get(`/students/${studentId}/coverage`);
      return data;
    },
    ...PARENT_QUERY,
  });
}

/** The weeks already written, newest first. A week still being written is not listed. */
export function usePastWeeks(studentId: string) {
  return useQuery({
    queryKey: ['past-weeks', studentId],
    queryFn: async () => {
      const { items } = await studentsApi.listWeeklyPackets(studentId, { page_size: 50 });
      return [...items].sort((a, b) => b.week_of.localeCompare(a.week_of));
    },
    ...PARENT_QUERY,
  });
}

/** True when the server said "no such child" (missing, or another family's). */
export function isNotFound(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 404;
}
