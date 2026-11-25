import { useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  studentsApi,
  systemApi,
  plansApi,
  curriculumApi,
  parseMetadata,
  WeeklyPacketSummary,
} from '@/lib/api';

export function useGenerateWeeklyPlan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: plansApi.generateWeeklyPlan,
    // Refresh the cached packet lists (not awaited: the mutation settles without waiting for it)
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['all-weekly-packets'] });
    },
  });
}

export function useStudentProgressMap(studentId: string, subject: string, prune: boolean = true) {
  return useQuery({
    queryKey: ['student-progress-map', studentId, subject, prune],
    queryFn: () => curriculumApi.getProgressMap(studentId, subject, prune),
    enabled: !!studentId && !!subject,
  });
}

export interface WeeklyPacketWithStudent extends WeeklyPacketSummary {
  studentName: string;
}

export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: () => studentsApi.listStudents(),
    staleTime: Infinity,
  });
}

function parseBlob(raw: string | null | undefined): Record<string, any> {
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function studentGradeLabel(student: any): string {
  const grade = student?.grade_level;
  if (grade === 0 || grade === '0') return 'Kindergarten';
  if (grade != null) return `Grade ${grade}`;
  return '—';
}

export function useEnrichedStudents() {
  const { data: students, isLoading, error } = useStudents();

  const enrichedStudents = useMemo(() => {
    if (!students) return [];
    return students.map((s) => {
      const metadata = parseMetadata(s.metadata_blob);
      const progress = parseBlob(s.progress_blob);
      return {
        id: s.student_id,
        name: metadata?.name || 'Unknown',
        grade: studentGradeLabel(s),
        subject: parseBlob(s.plan_rules_blob)?.theme_rules?.theme_subjects?.[0] || '—',
        masteredCount: progress?.mastered_standards?.length ?? 0,
        totalStandards: progress?.standard_metadata
          ? Object.keys(progress.standard_metadata).length
          : 0,
        avatarUrl: metadata?.avatar_url ?? undefined,
      };
    });
  }, [students]);

  return { students: enrichedStudents, isLoading, error };
}

export function useWeeklyPacketsStats() {
  const { data: allPackets, isLoading } = useAllWeeklyPackets();

  const stats = useMemo(() => {
    if (!allPackets) return { activePlans: 0, totalWorksheets: 0 };

    // This week's Monday, as YYYY-MM-DD
    const now = new Date();
    const monday = new Date(now);
    monday.setDate(now.getDate() - ((now.getDay() + 6) % 7));
    const weekKey = monday.toISOString().slice(0, 10);

    return {
      activePlans: allPackets.filter((p) => p.week_of === weekKey).length,
      totalWorksheets: allPackets.reduce(
        (acc, packet) =>
          acc + Object.values(packet.worksheet_counts ?? {}).reduce((sum, n) => sum + n, 0),
        0
      ),
    };
  }, [allPackets]);

  return { data: stats, isLoading };
}

// Every student's weekly packets, in one list
export function useAllWeeklyPackets() {
  const { data: students } = useStudents();

  const studentIds = useMemo(() => students?.map((s) => s.student_id) ?? [], [students]);

  return useQuery({
    queryKey: ['all-weekly-packets', studentIds],
    queryFn: async () => {
      const allPackets = await Promise.all(
        students!.map(async (student) => {
          try {
            const response = await studentsApi.listWeeklyPackets(student.student_id, {
              page_size: 50,
            });
            return response.items.map((packet) => ({
              ...packet,
              studentName: parseMetadata(student.metadata_blob)?.name || 'Unknown',
            }));
          } catch {
            return [];
          }
        })
      );
      return allPackets.flat();
    },
    enabled: studentIds.length > 0,
    staleTime: Infinity,
  });
}

function useFilteredPackets(keep: (packet: WeeklyPacketWithStudent) => boolean) {
  const { data: allPackets, isLoading, error } = useAllWeeklyPackets();
  const packets = useMemo(() => allPackets?.filter(keep) ?? [], [allPackets, keep]);
  return { packets, isLoading, error };
}

const isPending = (p: WeeklyPacketSummary) =>
  (p.status === 'ready' || p.status === 'draft') && !p.has_feedback;
const isCompleted = (p: WeeklyPacketSummary) => p.status === 'complete' || p.has_feedback;

export const usePendingPackets = () => useFilteredPackets(isPending);
export const useCompletedPackets = () => useFilteredPackets(isCompleted);

export function useSystemOptions() {
  return useQuery({
    queryKey: ['system-options'],
    queryFn: systemApi.getOptions,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}
