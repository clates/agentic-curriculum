import { useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  studentsApi,
  systemApi,
  plansApi,
  curriculumApi,
  parseMetadata,
  WeeklyPacketSummary,
} from '@/lib/api';

// ... (skipping some lines)

// Generate weekly plan mutation
export function useGenerateWeeklyPlan() {
  const queryClient = useQueryClient();

  const onSuccess = useCallback(() => {
    // Invalidate cached packet lists so they refresh
    queryClient.invalidateQueries({ queryKey: ['all-weekly-packets'] });
    queryClient.invalidateQueries({ queryKey: ['weekly-packets-stats'] });
  }, [queryClient]);

  return useMutation({
    mutationFn: plansApi.generateWeeklyPlan,
    onSuccess,
  });
}

// Curriculum Graph hooks
export function useCurriculumGraph(subject: string, prune: boolean = false) {
  return useQuery({
    queryKey: ['curriculum-graph', subject, prune],
    queryFn: () => curriculumApi.getGraph(subject, prune),
    enabled: !!subject,
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
    queryFn: async () => {
      return await studentsApi.listStudents();
    },
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
    return students.map((s) => ({
      id: s.student_id,
      name: parseMetadata(s.metadata_blob)?.name || 'Unknown',
      grade: studentGradeLabel(s),
      subject: parseBlob(s.plan_rules_blob)?.theme_rules?.theme_subjects?.[0] || '—',
      masteredCount: parseBlob(s.progress_blob)?.mastered_standards?.length ?? 0,
      totalStandards: parseBlob(s.progress_blob)?.standard_metadata
        ? Object.keys(parseBlob(s.progress_blob).standard_metadata).length
        : 0,
      avatarUrl: parseMetadata(s.metadata_blob)?.avatar_url ?? undefined,
    }));
  }, [students]);

  return { students: enrichedStudents, isLoading, error };
}

export function useWeeklyPacketsStats() {
  const { data: allPackets, isLoading } = useAllWeeklyPackets();

  const stats = useMemo(() => {
    if (!allPackets) return { activePlans: 0, totalWorksheets: 0 };

    // Compute current Monday for "this week" filtering
    const now = new Date();
    const dayOfWeek = (now.getDay() + 6) % 7; // Monday = 0
    const monday = new Date(now);
    monday.setDate(now.getDate() - dayOfWeek);
    const weekKey = monday.toISOString().slice(0, 10); // YYYY-MM-DD

    const thisWeekPackets = allPackets.filter((p) => p.week_of === weekKey);
    const activePlans = thisWeekPackets.length;
    const totalWorksheets = allPackets.reduce((acc, packet) => {
      if (!packet.worksheet_counts) return acc;
      return acc + Object.values(packet.worksheet_counts).reduce((sum, count) => sum + count, 0);
    }, 0);

    return {
      activePlans,
      totalWorksheets,
    };
  }, [allPackets]);

  return { data: stats, isLoading };
}

// Base query for all weekly packets
function useWeeklyPacketsBase() {
  const { data: students } = useStudents();

  const studentIds = useMemo(() => students?.map((s) => s.student_id) ?? [], [students]);

  return useQuery({
    queryKey: ['all-weekly-packets', studentIds],
    queryFn: async () => {
      if (studentIds.length === 0) return [];

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

// Aggregate all weekly packets across all students
export function useAllWeeklyPackets() {
  return useWeeklyPacketsBase();
}

// Get pending plans (status: 'ready' or 'draft')
export function usePendingPackets() {
  const { data: allPackets, isLoading, error } = useWeeklyPacketsBase();

  const packets = useMemo(() => {
    if (!allPackets) return [];
    return allPackets.filter((packet) => packet.status === 'ready' || packet.status === 'draft');
  }, [allPackets]);

  return { packets, isLoading, error };
}

// Get completed plans (status: 'complete')
export function useCompletedPackets() {
  const { data: allPackets, isLoading, error } = useWeeklyPacketsBase();

  const packets = useMemo(() => {
    if (!allPackets) return [];
    return allPackets.filter((packet) => packet.status === 'complete');
  }, [allPackets]);

  return { packets, isLoading, error };
}

// Get system options (subjects, grades, etc.)
export function useSystemOptions() {
  return useQuery({
    queryKey: ['system-options'],
    queryFn: systemApi.getOptions,
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  });
}
