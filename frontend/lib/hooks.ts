import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studentsApi, systemApi, plansApi, parseMetadata, parseProgress } from '@/lib/api';

export interface EnrichedStudent {
  id: string;
  name: string;
  grade: string;
  subject: string;
  masteredCount: number;
  totalStandards: number;
  avatarUrl?: string;
}

export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: async () => {
      return await studentsApi.listStudents();
    },
  });
}

export function useEnrichedStudents() {
  const { data: profiles, isLoading, error } = useStudents();

  const enrichedStudents: EnrichedStudent[] = (profiles || []).map((profile) => {
    const metadata = parseMetadata(profile.metadata_blob);
    const progress = parseProgress(profile.progress_blob);

    const totalStandards =
      progress.mastered_standards.length + progress.developing_standards.length;
    const masteredCount = progress.mastered_standards.length;

    // Determine primary subject from most recent packet (simplified for now)
    const subject = 'Math'; // Will be enhanced with real data

    return {
      id: profile.student_id,
      name: metadata?.name || 'Unknown Student',
      grade: 'Kindergarten', // Will be enhanced with real data
      subject,
      masteredCount,
      totalStandards: totalStandards || 20, // Default to 20 if no standards
      avatarUrl: metadata?.avatar_url,
    };
  });

  return { students: enrichedStudents, isLoading, error };
}

export function useWeeklyPacketsStats() {
  const { data: profiles } = useStudents();

  return useQuery({
    queryKey: ['weekly-packets-stats'],
    queryFn: async () => {
      if (!profiles || profiles.length === 0) {
        return { activePlans: 0, totalWorksheets: 0 };
      }

      let activePlans = 0;
      let totalWorksheets = 0;

      await Promise.all(
        profiles.map(async (profile) => {
          try {
            const packets = await studentsApi.listWeeklyPackets(profile.student_id, {
              page_size: 10,
            });

            // Count active plans (status: 'ready' or 'draft')
            activePlans += packets.items.filter(
              (p) => p.status === 'ready' || p.status === 'draft'
            ).length;

            // Sum up artifact counts
            totalWorksheets += packets.items.reduce((sum, p) => sum + p.artifact_count, 0);
          } catch {
            // Ignore errors for individual students
          }
        })
      );

      return { activePlans, totalWorksheets };
    },
    enabled: !!profiles && profiles.length > 0,
  });
}

// Aggregate all weekly packets across all students
export function useAllWeeklyPackets() {
  const { data: students } = useStudents();

  return useQuery({
    queryKey: ['all-weekly-packets'],
    queryFn: async () => {
      if (!students || students.length === 0) return [];

      const allPackets = await Promise.all(
        students.map(async (student) => {
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
    enabled: !!students && students.length > 0,
  });
}

// Get pending plans (status: 'ready' or 'draft')
export function usePendingPackets() {
  const { data: allPackets, isLoading, error } = useAllWeeklyPackets();

  const pendingPackets =
    allPackets?.filter((packet) => packet.status === 'ready' || packet.status === 'draft') || [];

  return { packets: pendingPackets, isLoading, error };
}

// Get completed plans (status: 'complete')
export function useCompletedPackets() {
  const { data: allPackets, isLoading, error } = useAllWeeklyPackets();

  const completedPackets = allPackets?.filter((packet) => packet.status === 'complete') || [];

  return { packets: completedPackets, isLoading, error };
}

// Get system options (subjects, grades, etc.)
export function useSystemOptions() {
  return useQuery({
    queryKey: ['system-options'],
    queryFn: systemApi.getOptions,
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  });
}

// Generate weekly plan mutation
export function useGenerateWeeklyPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: plansApi.generateWeeklyPlan,
    onSuccess: () => {
      // Invalidate cached packet lists so they refresh
      queryClient.invalidateQueries({ queryKey: ['all-weekly-packets'] });
      queryClient.invalidateQueries({ queryKey: ['weekly-packets-stats'] });
    },
  });
}
