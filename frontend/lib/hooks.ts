import { useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  studentsApi,
  systemApi,
  plansApi,
  parseMetadata,
  parseProgress,
  WeeklyPacketSummary,
} from '@/lib/api';

export interface EnrichedStudent {
  id: string;
  name: string;
  grade: string;
  subject: string;
  masteredCount: number;
  totalStandards: number;
  avatarUrl?: string;
}

export interface WeeklyPacketWithStudent extends WeeklyPacketSummary {
  studentName: string;
}

export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: async () => {
      console.log('Fetching students...');
      return await studentsApi.listStudents();
    },
    staleTime: Infinity,
  });
}

export function useEnrichedStudents() {
  const { data: students, isLoading, error } = useStudents();

  const enrichedStudents = useMemo(() => {
    if (!students) return [];
    return students.map((s) => ({
      id: s.student_id,
      name: parseMetadata(s.metadata_blob)?.name || 'Unknown',
      grade: '3rd Grade', // TODO: Extract from metadata
      subject: 'Math', // TODO: Extract from metadata
      masteredCount: 0, // TODO: Calculate from progress
      totalStandards: 20, // TODO: Calculate from progress
      avatarUrl: undefined,
    }));
  }, [students]);

  return { students: enrichedStudents, isLoading, error };
}

export function useWeeklyPacketsStats() {
  const { data: allPackets, isLoading } = useAllWeeklyPackets();

  const stats = useMemo(() => {
    if (!allPackets) return { activePlans: 0, totalWorksheets: 0 };

    const activePlans = allPackets.length;
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

  return useQuery({
    queryKey: ['all-weekly-packets', students?.length || 0],
    queryFn: async () => {
      console.log('Fetching weekly packets...');
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
    // Always enabled to prevent toggling, but returns empty if no students
    enabled: true,
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
