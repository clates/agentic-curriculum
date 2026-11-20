import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { PARENT_QUERY } from '@/lib/parentQuery';

export interface SkillItem {
  skill: string;
  subject?: string;
  why?: string;
}

export interface ProgressSummary {
  student_name: string | null;
  summary: string;
  solid: SkillItem[];
  shaky: SkillItem[];
  needs_work: SkillItem[];
  due_for_review: SkillItem[];
  last_four_weeks: {
    skills_checked: number;
    went_well: SkillItem[];
    still_shaky: SkillItem[];
    needs_work: SkillItem[];
  };
}

export function useProgressSummary(studentId: string | null) {
  return useQuery({
    queryKey: ['progress-summary', studentId],
    enabled: !!studentId,
    queryFn: async (): Promise<ProgressSummary> => {
      const { data } = await apiClient.get(`/students/${studentId}/progress-summary`);
      return data;
    },
    ...PARENT_QUERY,
  });
}
