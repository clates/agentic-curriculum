'use client';

import { useState, useMemo, useCallback } from 'react';
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

export default function PlansPage() {
  const { data: students } = useStudents();
  const { packets: pendingPackets, isLoading: pendingLoading } = usePendingPackets();
  const { packets: completedPackets, isLoading: completedLoading } = useCompletedPackets();
  const { showToast } = useToast();

  // Modal state
  const [planDetailOpen, setPlanDetailOpen] = useState(false);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [selectedPacketIds, setSelectedPacketIds] = useState<{
    studentId: string;
    packetId: string;
  } | null>(null);
  const [masteryRating, setMasteryRating] = useState<string | null>(null);
  const [quantityRating, setQuantityRating] = useState<string | null>(null);

  // Modal state for plan generation
  const [generateModalOpen, setGenerateModalOpen] = useState(false);

  const queryClient = useQueryClient();

  // Fetch plan detail when packet is selected
  const { data: planDetail, isLoading: planDetailLoading } = useQuery({
    queryKey: ['plan-detail', selectedPacketIds?.studentId, selectedPacketIds?.packetId],
    queryFn: async () => {
      if (!selectedPacketIds) return null;
      return await plansApi.getPacketDetail(
        selectedPacketIds.studentId,
        selectedPacketIds.packetId
      );
    },
    enabled: !!selectedPacketIds && planDetailOpen,
  });

  // Fetch worksheet artifacts with IDs for downloads
  const { data: worksheetData } = useQuery({
    queryKey: ['packet-worksheets', selectedPacketIds?.studentId, selectedPacketIds?.packetId],
    queryFn: async () => {
      if (!selectedPacketIds) return null;
      return await plansApi.getPacketWorksheets(
        selectedPacketIds.studentId,
        selectedPacketIds.packetId
      );
    },
    enabled: !!selectedPacketIds && planDetailOpen,
  });

  const feedbackMutation = useMutation({
    mutationFn: async ({
      studentId,
      packetId,
      mastery,
      quantity,
    }: {
      studentId: string;
      packetId: string;
      mastery: string;
      quantity: string;
    }) => {
      // Convert quantity rating to integer
      const quantityValue = QUANTITY_RATING_MAP[quantity] ?? 0;
      await plansApi.submitFeedback(studentId, packetId, {
        mastery_feedback: { overall: mastery },
        quantity_feedback: quantityValue,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-weekly-packets'] });
      setFeedbackModalOpen(false);
      setPlanDetailOpen(false);
      setSelectedPacketIds(null);
      setMasteryRating(null);
      setQuantityRating(null);
    },
  });

  const { mutate: submitFeedback } = feedbackMutation;

  // Helper to find the selected packet from lists
  const selectedPacket = useMemo(() => {
    if (!selectedPacketIds) return null;
    const allPackets = [...pendingPackets, ...completedPackets];
    return allPackets.find(
      (p) =>
        p.student_id === selectedPacketIds.studentId && p.packet_id === selectedPacketIds.packetId
    );
  }, [selectedPacketIds, pendingPackets, completedPackets]);

  const handleViewPlan = useCallback((packet: WeeklyPacketWithStudent) => {
    setSelectedPacketIds({
      studentId: packet.student_id,
      packetId: packet.packet_id,
    });
    setPlanDetailOpen(true);
  }, []);

  const handleProvideFeedback = useCallback(() => {
    setMasteryRating(null);
    setQuantityRating(null);
    setFeedbackModalOpen(true);
    setPlanDetailOpen(false);
  }, []);

  const handleSubmitFeedback = useCallback(() => {
    if (!selectedPacketIds || !masteryRating || !quantityRating) return;

    submitFeedback({
      studentId: selectedPacketIds.studentId,
      packetId: selectedPacketIds.packetId,
      mastery: masteryRating,
      quantity: quantityRating,
    });
  }, [selectedPacketIds, masteryRating, quantityRating, submitFeedback]);

  const handleDownloadArtifact = (downloadUrl: string) => {
    // downloadUrl is already the correct path like /students/{id}/worksheet-artifacts/{artifact_id}
    const fullUrl = `/api${downloadUrl}`;
    window.open(fullUrl, '_blank');
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
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

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
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
            {pendingPackets && pendingPackets.length > 0 && (
              <section className="mb-12">
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-foreground text-2xl font-semibold">
                    Pending Plans - Feedback Needed!
                  </h2>
                  <Badge variant="warning" className="px-4 py-2 text-base">
                    {pendingPackets.length} {pendingPackets.length === 1 ? 'Plan' : 'Plans'}
                    Awaiting Feedback
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
                      className="border-primary-200 hover:border-primary-400 cursor-pointer border-2 transition-all hover:shadow-md"
                      onClick={() => handleViewPlan(packet)}
                    >
                      <div className="space-y-4">
                        <div className="flex items-start justify-between">
                          <div>
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
                          <div>
                            <span className="text-neutral-600">Subject:</span>
                            <span className="text-foreground ml-2 font-medium">
                              {packet.subject}
                            </span>
                          </div>
                          <div>
                            <span className="text-neutral-600">Grade:</span>
                            <span className="text-foreground ml-2 font-medium">
                              {packet.grade_level}
                            </span>
                          </div>
                          <div>
                            <span className="text-neutral-600">Days:</span>
                            <span className="text-foreground ml-2 font-medium">
                              {packet.resource_days}
                            </span>
                          </div>
                          <div>
                            <span className="text-neutral-600">Activities:</span>
                            <span className="text-foreground ml-2 font-medium">
                              {packet.daily_count} per day
                            </span>
                          </div>
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
            {completedPackets && completedPackets.length > 0 && (
              <section>
                <h2 className="text-foreground mb-6 text-2xl font-semibold">Completed Plans</h2>
                <Card>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="border-b border-neutral-200 bg-neutral-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase">
                            Student
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase">
                            Week Of
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase">
                            Subject
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase">
                            Grade
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase">
                            Artifacts
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium tracking-wider text-neutral-600 uppercase">
                            Updated
                          </th>
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
                            <td className="px-6 py-4 text-sm whitespace-nowrap text-neutral-600">
                              {formatDate(packet.week_of)}
                            </td>
                            <td className="px-6 py-4 text-sm whitespace-nowrap text-neutral-600">
                              {packet.subject}
                            </td>
                            <td className="px-6 py-4 text-sm whitespace-nowrap text-neutral-600">
                              {packet.grade_level}
                            </td>
                            <td className="px-6 py-4 text-sm whitespace-nowrap text-neutral-600">
                              {packet.artifact_count}
                            </td>
                            <td className="px-6 py-4 text-sm whitespace-nowrap text-neutral-600">
                              {formatDate(packet.updated_at)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </section>
            )}

            {/* Empty State */}
            {(!pendingPackets || pendingPackets.length === 0) &&
              (!completedPackets || completedPackets.length === 0) && (
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
        <Modal
          isOpen={planDetailOpen}
          onClose={() => {
            setPlanDetailOpen(false);
            setSelectedPacketIds(null);
          }}
          title="Plan Details"
        >
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
                {/* Lesson Plan */}
                {planDetail.lesson_plan && (
                  <div className="rounded-lg border border-neutral-200 p-4">
                    <h4 className="mb-2 font-medium">Lesson Plan</h4>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-neutral-600">
                        {planDetail.lesson_plan.title}
                      </span>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleDownloadArtifact(planDetail.lesson_plan!.pdf_path)}
                      >
                        View PDF
                      </Button>
                    </div>
                  </div>
                )}

                {/* Worksheets */}
                {worksheetData?.items && worksheetData.items.length > 0 && (
                  <div>
                    <h4 className="mb-2 font-medium">Worksheets</h4>
                    <div className="space-y-2">
                      {worksheetData.items.map((item) =>
                        item.artifacts.map((artifact) => (
                          <div
                            key={artifact.artifact_id}
                            className="flex items-center justify-between rounded-lg border border-neutral-200 p-3"
                          >
                            <div>
                              <p className="text-sm font-medium">
                                {item.resource_kind.replace('Worksheet', '')} - {item.day_label}
                              </p>
                              <p className="text-xs text-neutral-500">
                                {artifact.format.toUpperCase()}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDownloadArtifact(artifact.download_url)}
                            >
                              Download
                            </Button>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-neutral-500">No details available.</p>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <Button
                variant="ghost"
                onClick={() => {
                  setPlanDetailOpen(false);
                  setSelectedPacketIds(null);
                }}
              >
                Close
              </Button>
              {selectedPacket.status === 'ready' && (
                <Button
                  className="bg-primary-600 hover:bg-primary-700"
                  onClick={handleProvideFeedback}
                >
                  Provide Feedback
                </Button>
              )}
            </div>
          </div>
        </Modal>
      )}

      {selectedPacket && feedbackModalOpen && (
        <Modal
          isOpen={feedbackModalOpen}
          onClose={() => {
            setFeedbackModalOpen(false);
            setMasteryRating(null);
            setQuantityRating(null);
          }}
          title="Provide Feedback"
        >
          <div className="space-y-6">
            <p className="text-neutral-600">
              Help the AI understand how {selectedPacket.studentName} did with this week&apos;s
              plan.
            </p>

            {/* Mastery Rating */}
            <div>
              <label className="mb-3 block text-sm font-medium text-neutral-700">
                Overall Mastery
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  {
                    value: 'STRUGGLING',
                    label: 'Struggling',
                    color: 'bg-red-100 text-red-800 border-red-200',
                  },
                  {
                    value: 'DEVELOPING',
                    label: 'Developing',
                    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
                  },
                  {
                    value: 'MASTERED',
                    label: 'Mastered',
                    color: 'bg-green-100 text-green-800 border-green-200',
                  },
                ].map((option) => (
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
                {[
                  { value: 'TOO_LITTLE', label: 'Too Little' },
                  { value: 'JUST_RIGHT', label: 'Just Right' },
                  { value: 'TOO_MUCH', label: 'Too Much' },
                ].map((option) => (
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
                {feedbackMutation.isPending ? 'Submitting...' : 'Submit Feedback'}
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
