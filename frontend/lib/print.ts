import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { PARENT_QUERY } from '@/lib/parentQuery';

export type PrintDoc = 'packet' | 'guide' | 'prep';

export interface PrintInfo {
  structured: boolean;
  title: string;
  documents: PrintDoc[];
}

/** What this week can print: all three documents, or just the pages for an older week. */
export function usePrintInfo(studentId: string, packetId: string | null | undefined) {
  return useQuery({
    queryKey: ['print-info', studentId, packetId],
    enabled: !!packetId,
    queryFn: async (): Promise<PrintInfo> => {
      const { data } = await apiClient.get(
        `/students/${studentId}/weekly-packets/${packetId}/print-info`
      );
      return data;
    },
    ...PARENT_QUERY,
  });
}

/**
 * Where a document lives, through the app's own /api route. A new tab opened on it is what a phone
 * hands to the print dialog (AirPrint).
 */
export function printUrl(studentId: string, packetId: string, doc: PrintDoc): string {
  return `/api/students/${studentId}/weekly-packets/${packetId}/print?doc=${doc}`;
}

/** "I've printed it": the week moves on to all set. Repeating it is harmless on the server. */
export function useMarkPrinted() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ studentId, planId }: { studentId: string; planId: string }) => {
      await apiClient.post(`/students/${studentId}/week-plans/${planId}/printed`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['this-week'] }),
  });
}

const DAY = { weekday: 'long', month: 'long', day: 'numeric' } as const;

function dateOf(iso: string): Date | null {
  const m = /^(\d{4}-\d{2}-\d{2})/.exec(iso);
  if (!m) return null;
  const d = new Date(`${m[1]}T12:00:00`);
  return Number.isNaN(d.getTime()) ? null : d;
}

/** "Monday, January 5 to Friday, January 9" for the school week that starts on `weekStart`. */
export function weekRange(weekStart: string): string | null {
  const monday = dateOf(weekStart);
  if (!monday) return null;
  const friday = new Date(monday);
  friday.setDate(friday.getDate() + 4);
  return `${monday.toLocaleDateString('en-US', DAY)} to ${friday.toLocaleDateString('en-US', DAY)}`;
}

/** The print-by day in friendly words, and whether it is already behind us. */
export function deadlineInfo(
  deadline: string | null,
  today: Date = new Date()
): { text: string; passed: boolean } | null {
  if (!deadline) return null;
  const d = dateOf(deadline);
  if (!d) return null;
  const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 12);
  return { text: d.toLocaleDateString('en-US', DAY), passed: d < startOfToday };
}
