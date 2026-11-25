'use client';

import { useState, useMemo, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { Card, Button, Badge, Modal } from '@/components/ui';
import { Navigation } from '@/components/Navigation';
import {
  usePendingPackets,
  useCompletedPackets,
  useStudents,
  WeeklyPacketWithStudent,
} from '@/lib/hooks';
import { plansApi, parseMetadata } from '@/lib/api';
import { GeneratePlanModal } from '@/components/GeneratePlanModal';
import { useToast } from '@/components/ToastProvider';

// Map UI quantity ratings to backend integers
const QUANTITY_RATING_MAP: Record<string, number> = {
  TOO_LITTLE: 2,
  JUST_RIGHT: 0,
  TOO_MUCH: -2,
};

// Reverse map: backend integer to UI rating label
function quantityToRating(qty: number): string {
  if (qty > 0) return 'TOO_LITTLE';
  if (qty < 0) return 'TOO_MUCH';
  return 'JUST_RIGHT';
}

const FEEDBACK_LOCK_WEEKS = 3;

function isFeedbackLocked(feedbackCompletedAt: string | null): boolean {
  if (!feedbackCompletedAt) return false;
  const submitted = new Date(feedbackCompletedAt);
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - FEEDBACK_LOCK_WEEKS * 7);
  return submitted < cutoff;
}

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

const MASTERY_OPTIONS = [
  { value: 'STRUGGLING', label: 'Struggling', color: 'bg-red-100 text-red-800 border-red-200' },
  {
    value: 'DEVELOPING',
    label: 'Developing',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  },
  { value: 'MASTERED', label: 'Mastered', color: 'bg-green-100 text-green-800 border-green-200' },
];

const QUANTITY_OPTIONS = [
  { value: 'TOO_LITTLE', label: 'Too Little' },
  { value: 'JUST_RIGHT', label: 'Just Right' },
  { value: 'TOO_MUCH', label: 'Too Much' },
];

const COMPLETED_COLUMNS = ['Student', 'Week Of', 'Subject', 'Grade', 'Artifacts', 'Updated'];

export default function PlansPage() {
  const { data: students } = useStudents();
  const { packets: pendingPackets, isLoading: pendingLoading } = usePendingPackets();
  const { packets: completedPackets, isLoading: completedLoading } = useCompletedPackets();
  const { showToast } = useToast();

  const [planDetailOpen, setPlanDetailOpen] = useState(false);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [selectedPacketIds, setSelectedPacketIds] = useState<{
    studentId: string;
    packetId: string;
  } | null>(null);
  const [masteryRating, setMasteryRating] = useState<string | null>(null);
  const [quantityRating, setQuantityRating] = useState<string | null>(null);

  const [generateModalOpen, setGenerateModalOpen] = useState(false);

  const queryClient = useQueryClient();

  const selectedPacket = useMemo(() => {
    if (!selectedPacketIds) return null;
    const allPackets = [...pendingPackets, ...completedPackets];
    return allPackets.find(
      (p) =>
        p.student_id === selectedPacketIds.studentId && p.packet_id === selectedPacketIds.packetId
    );
  }, [selectedPacketIds, pendingPackets, completedPackets]);

  // Fetch existing feedback when the feedback modal is open for a packet that has feedback
  const ids = [selectedPacketIds?.studentId, selectedPacketIds?.packetId] as const;
  const sel = selectedPacketIds!; // the queries below only run once a packet is selected

  const { data: existingFeedback } = useQuery({
    queryKey: ['packet-feedback', ...ids],
    queryFn: () => plansApi.getFeedback(sel.studentId, sel.packetId),
    enabled: !!selectedPacketIds && feedbackModalOpen && !!selectedPacket?.has_feedback,
  });

  // Pre-populate feedback modal with existing values when editing
  useEffect(() => {
    if (existingFeedback && feedbackModalOpen && masteryRating === null) {
      setMasteryRating(existingFeedback.mastery_feedback?.overall ?? null);
      if (existingFeedback.quantity_feedback != null) {
        setQuantityRating(quantityToRating(existingFeedback.quantity_feedback));
      }
    }
  }, [existingFeedback, feedbackModalOpen, masteryRating]);

  // Fetch plan detail when packet is selected
  const { data: planDetail, isLoading: planDetailLoading } = useQuery({
    queryKey: ['plan-detail', ...ids],
    queryFn: () => plansApi.getPacketDetail(sel.studentId, sel.packetId),
    enabled: !!selectedPacketIds && planDetailOpen,
  });

  // Fetch worksheet artifacts with IDs for downloads
  const { data: worksheetData } = useQuery({
    queryKey: ['packet-worksheets', ...ids],
    queryFn: () => plansApi.getPacketWorksheets(sel.studentId, sel.packetId),
    enabled: !!selectedPacketIds && planDetailOpen,
  });

  const resetRatings = () => {
    setMasteryRating(null);
    setQuantityRating(null);
  };

  const closePlanDetail = () => {
    setPlanDetailOpen(false);
    setSelectedPacketIds(null);
  };

  const feedbackMutation = useMutation({
    mutationFn: (v: { studentId: string; packetId: string; mastery: string; quantity: string }) =>
      plansApi.submitFeedback(v.studentId, v.packetId, {
        mastery_feedback: { overall: v.mastery },
        quantity_feedback: QUANTITY_RATING_MAP[v.quantity] ?? 0,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-weekly-packets'] });
      setFeedbackModalOpen(false);
      closePlanDetail();
      resetRatings();
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to submit feedback. Please try again.', 'error');
    },
  });

  const handleViewPlan = (packet: WeeklyPacketWithStudent) => {
    setSelectedPacketIds({ studentId: packet.student_id, packetId: packet.packet_id });
    setPlanDetailOpen(true);
  };

  const handleProvideFeedback = () => {
    resetRatings();
    setFeedbackModalOpen(true);
    setPlanDetailOpen(false);
  };

  const handleSubmitFeedback = () => {
    if (!selectedPacketIds || !masteryRating || !quantityRating) return;
    feedbackMutation.mutate({
      ...selectedPacketIds,
      mastery: masteryRating,
      quantity: quantityRating,
    });
  };

  const modalStudents = useMemo(
    () =>
      (students || []).map((s) => ({
        id: s.student_id,
        name: parseMetadata(s.metadata_blob)?.name || 'Unknown',
        grade: 0, // TODO: Extract from student metadata
      })),
    [students]
  );

  const showSkeleton =
    (pendingLoading || completedLoading) && !pendingPackets.length && !completedPackets.length;

  return (
    <div className="bg-background min-h-screen">
      <Navigation />

      <main className="mx-auto max-w-7xl px-4 py-8 [overflow-wrap:anywhere] sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="mb-2 flex items-center justify-between">
            <h1 className="text-foreground text-3xl font-semibold">Weekly Plans</h1>
            <Button
              onClick={() => setGenerateModalOpen(true)}
              className="bg-primary-600 hover:bg-primary-700"
            >
              Generate New Plan
            </Button>
          </div>
          <p className="text-neutral-600">
            Review lesson plans and provide feedback to improve future lessons
          </p>
        </div>

        {showSkeleton ? (
          <div className="animate-pulse space-y-8">
            <div className="h-8 w-48 rounded bg-neutral-200"></div>
            <div className="h-64 rounded bg-neutral-200"></div>
          </div>
        ) : (
          <>
            {/* Pending Plans - Prominent Section */}
            {pendingPackets.length > 0 && (
              <section className="mb-12">
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-foreground text-2xl font-semibold">Pending Plans</h2>
                  <Badge variant="default" className="px-4 py-2 text-base">
                    {pendingPackets.length} {pendingPackets.length === 1 ? 'Plan' : 'Plans'}
                  </Badge>
                </div>

                <div className="bg-primary-50 border-primary-200 mb-6 rounded-lg border-2 p-6">
                  <div className="flex items-start space-x-4">
                    <svg
                      className="text-primary-600 mt-0.5 h-6 w-6 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <div>
                      <h3 className="text-foreground mb-1 font-semibold">
                        Your Feedback Shapes Future Lessons
                      </h3>
                      <p className="text-sm text-neutral-700">
                        Click on a plan to view details, then provide feedback to help the AI
                        understand which concepts your student has mastered.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  {pendingPackets.map((packet) => (
                    <Card
                      key={packet.packet_id}
                      padding="lg"
                      role="button"
                      tabIndex={0}
                      className="border-primary-200 hover:border-primary-400 cursor-pointer border-2 transition-all hover:shadow-md"
                      onClick={() => handleViewPlan(packet)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleViewPlan(packet);
                        }
                      }}
                    >
                      <div className="space-y-4">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <h3 className="text-foreground text-xl font-semibold">
                              {packet.studentName}
                            </h3>
                            <p className="text-sm text-neutral-600">
                              Week of {formatDate(packet.week_of)}
                            </p>
                          </div>
                          <Badge variant={packet.status === 'ready' ? 'success' : 'default'}>
                            {packet.status}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          {(
                            [
                              ['Subject', packet.subject],
                              ['Grade', packet.grade_level],
                              ['Days', packet.daily_count],
                              ['Worksheets', packet.artifact_count],
                            ] as const
                          ).map(([label, value]) => (
                            <div key={label}>
                              <span className="text-neutral-600">{label}:</span>
                              <span className="text-foreground ml-2 font-medium">{value}</span>
                            </div>
                          ))}
                        </div>

                        {packet.worksheet_counts &&
                          Object.keys(packet.worksheet_counts).length > 0 && (
                            <div className="border-t border-neutral-200 pt-2">
                              <p className="mb-2 text-xs text-neutral-600">Worksheets:</p>
                              <div className="flex flex-wrap gap-2">
                                {Object.entries(packet.worksheet_counts).map(([type, count]) => (
                                  <span
                                    key={type}
                                    className="rounded bg-neutral-100 px-2 py-1 text-xs"
                                  >
                                    {type}: {count}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                        <div className="text-primary-600 pt-2 text-sm font-medium">
                          Click to view details →
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </section>
            )}

            {/* Completed Plans Table */}
            {completedPackets.length > 0 && (
              <section>
                <h2 className="text-foreground mb-6 text-2xl font-semibold">Completed Plans</h2>
                <Card>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="border-b border-neutral-200 bg-neutral-50">
                        <tr>
                          {COMPLETED_COLUMNS.map((column) => (
                            <th
                              key={column}
                              className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase"
                            >
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-200 bg-white">
                        {completedPackets.map((packet) => (
                          <tr
                            key={packet.packet_id}
                            className="cursor-pointer hover:bg-neutral-50"
                            onClick={() => handleViewPlan(packet)}
                          >
                            <td className="text-foreground px-6 py-4 text-sm font-medium whitespace-nowrap">
                              {packet.studentName}
                            </td>
                            {[
                              formatDate(packet.week_of),
                              packet.subject,
                              packet.grade_level,
                              packet.artifact_count,
                              formatDate(packet.updated_at),
                            ].map((value, i) => (
                              <td
                                key={i}
                                className="px-6 py-4 text-sm whitespace-nowrap text-neutral-600"
                              >
                                {value}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </section>
            )}

            {/* Empty State */}
            {pendingPackets.length === 0 && completedPackets.length === 0 && (
              <div className="rounded-lg bg-white p-12 text-center shadow-sm">
                <svg
                  className="mx-auto mb-4 h-16 w-16 text-neutral-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h3 className="text-foreground mb-2 text-lg font-medium">No Plans Yet</h3>
                <p className="text-neutral-600">
                  Weekly lesson plans will appear here once generated
                </p>
              </div>
            )}
          </>
        )}
      </main>

      {/* Modals */}
      {selectedPacket && planDetailOpen && (
        <Modal isOpen={planDetailOpen} onClose={closePlanDetail} title="Plan Details">
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold">{selectedPacket.studentName}</h3>
              <p className="text-neutral-600">Week of {formatDate(selectedPacket.week_of)}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-neutral-600">Subject</p>
                <p className="font-medium">{selectedPacket.subject}</p>
              </div>
              <div>
                <p className="text-sm text-neutral-600">Grade Level</p>
                <p className="font-medium">{selectedPacket.grade_level}</p>
              </div>
            </div>

            {/* Plan Content */}
            {planDetailLoading ? (
              <div className="space-y-2">
                <div className="h-4 w-3/4 animate-pulse rounded bg-neutral-100"></div>
                <div className="h-4 w-1/2 animate-pulse rounded bg-neutral-100"></div>
              </div>
            ) : planDetail ? (
              <div className="space-y-4">
                {/* Weekly Overview */}
                {planDetail.weekly_overview && (
                  <div className="rounded-lg bg-neutral-50 p-4 text-sm text-neutral-700">
                    {planDetail.weekly_overview}
                  </div>
                )}

                {/* Daily Plans */}
                {planDetail.daily_plan?.map((day) => {
                  const dayWorksheets = worksheetData?.items?.filter(
                    (w) => w.day_label === day.day
                  );
                  return (
                    <div key={day.day} className="rounded-lg border border-neutral-200 p-4">
                      <div className="mb-2 flex items-center justify-between">
                        <h4 className="font-semibold">{day.day}</h4>
                        {day.resource_errors && day.resource_errors.length > 0 && (
                          <span className="text-xs text-red-500">
                            {day.resource_errors.length} worksheet error(s)
                          </span>
                        )}
                      </div>
                      <p className="mb-2 text-sm text-neutral-600">{day.focus}</p>
                      {day.lesson_plan && (
                        <div className="space-y-1">
                          <p className="text-sm font-medium">{day.lesson_plan.objective}</p>
                          {day.lesson_plan.procedure?.length > 0 && (
                            <ol className="ml-4 list-decimal space-y-1">
                              {day.lesson_plan.procedure.map((step, i) => (
                                <li key={i} className="text-xs text-neutral-600">
                                  {step}
                                </li>
                              ))}
                            </ol>
                          )}
                        </div>
                      )}
                      {dayWorksheets && dayWorksheets.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {dayWorksheets.map((item) =>
                            item.artifacts.map((artifact) => (
                              <Button
                                key={artifact.artifact_id}
                                variant="ghost"
                                size="sm"
                                // download_url is a backend path; the app reaches it through /api
                                onClick={() =>
                                  window.open(`/api${artifact.download_url}`, '_blank')
                                }
                                className="text-xs"
                              >
                                {item.resource_kind.replace('Worksheet', '')}{' '}
                                {artifact.format.toUpperCase()} ↓
                              </Button>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-neutral-500">No details available.</p>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <Button variant="ghost" onClick={closePlanDetail}>
                Close
              </Button>
              {selectedPacketIds && (
                <Button
                  variant="ghost"
                  onClick={() =>
                    window.open(
                      `/api/students/${selectedPacketIds.studentId}/weekly-packets/${selectedPacketIds.packetId}/print`,
                      '_blank'
                    )
                  }
                >
                  Print All
                </Button>
              )}
              {selectedPacket.status === 'ready' &&
                (isFeedbackLocked(selectedPacket.feedback_completed_at) ? (
                  <Button variant="ghost" disabled className="cursor-default opacity-60">
                    Feedback Submitted
                  </Button>
                ) : (
                  <Button
                    className="bg-primary-600 hover:bg-primary-700"
                    onClick={handleProvideFeedback}
                  >
                    {selectedPacket.has_feedback ? 'Edit Feedback' : 'Provide Feedback'}
                  </Button>
                ))}
            </div>
          </div>
        </Modal>
      )}

      {selectedPacket && feedbackModalOpen && (
        <Modal
          isOpen={feedbackModalOpen}
          onClose={() => {
            setFeedbackModalOpen(false);
            resetRatings();
          }}
          title={selectedPacket.has_feedback ? 'Edit Feedback' : 'Provide Feedback'}
        >
          <div className="space-y-6">
            <p className="text-neutral-600">
              {selectedPacket.has_feedback
                ? `Update how ${selectedPacket.studentName} did with this week’s plan.`
                : `Help the AI understand how ${selectedPacket.studentName} did with this week’s plan.`}
            </p>

            {/* Mastery Rating */}
            <div>
              <label className="mb-3 block text-sm font-medium text-neutral-700">
                Overall Mastery
              </label>
              <div className="grid grid-cols-3 gap-3">
                {MASTERY_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setMasteryRating(option.value)}
                    className={`rounded-lg border p-3 text-center text-sm font-medium transition-all ${
                      masteryRating === option.value
                        ? `ring-2 ring-offset-1 ${option.color} border-transparent ring-primary-500`
                        : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Quantity Rating */}
            <div>
              <label className="mb-3 block text-sm font-medium text-neutral-700">
                Workload Amount
              </label>
              <div className="grid grid-cols-3 gap-3">
                {QUANTITY_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setQuantityRating(option.value)}
                    className={`rounded-lg border p-3 text-center text-sm font-medium transition-all ${
                      quantityRating === option.value
                        ? 'bg-primary-50 border-primary-500 text-primary-700 ring-2 ring-primary-500 ring-offset-1'
                        : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <Button
                variant="ghost"
                onClick={() => setFeedbackModalOpen(false)}
                disabled={feedbackMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                className="bg-primary-600 hover:bg-primary-700"
                onClick={handleSubmitFeedback}
                disabled={!masteryRating || !quantityRating || feedbackMutation.isPending}
              >
                {feedbackMutation.isPending
                  ? 'Submitting...'
                  : selectedPacket.has_feedback
                    ? 'Update Feedback'
                    : 'Submit Feedback'}
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Generate Plan Modal */}
      <GeneratePlanModal
        isOpen={generateModalOpen}
        onClose={() => setGenerateModalOpen(false)}
        students={modalStudents}
        onSuccess={() => {
          showToast('Plan is being generated! The page will refresh when complete.', 'success');
        }}
      />
    </div>
  );
}
