'use client';

import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { Card, Button, Badge, Modal } from '@/components/ui';
import { Navigation } from '@/components/Navigation';
import { usePendingPackets, useCompletedPackets, useStudents } from '@/lib/hooks';
import { plansApi, parseMetadata } from '@/lib/api';
import { GeneratePlanModal } from '@/components/GeneratePlanModal';
import { useToast } from '@/components/ToastProvider';

export default function PlansPage() {
  const { packets: pendingPackets, isLoading: pendingLoading } = usePendingPackets();
  const { packets: completedPackets, isLoading: completedLoading } = useCompletedPackets();
  const { data: students } = useStudents();
  const { showToast } = useToast();

  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [planDetailOpen, setPlanDetailOpen] = useState(false);
  const [selectedPacket, setSelectedPacket] = useState<any>(null);
  const [expandedDay, setExpandedDay] = useState<number | null>(null);
  const [masteryRating, setMasteryRating] = useState<string | null>(null);
  const [quantityRating, setQuantityRating] = useState<string | null>(null);

  // Modal state for plan generation
  const [generateModalOpen, setGenerateModalOpen] = useState(false);

  const queryClient = useQueryClient();

  // Fetch plan detail when packet is selected
  const { data: planDetail, isLoading: planDetailLoading } = useQuery({
    queryKey: ['plan-detail', selectedPacket?.student_id, selectedPacket?.packet_id],
    queryFn: async () => {
      if (!selectedPacket) return null;
      return await plansApi.getPacketDetail(selectedPacket.student_id, selectedPacket.packet_id);
    },
    enabled: !!selectedPacket && planDetailOpen,
  });

  // Fetch worksheet artifacts with IDs for downloads
  const { data: worksheetData } = useQuery({
    queryKey: ['packet-worksheets', selectedPacket?.student_id, selectedPacket?.packet_id],
    queryFn: async () => {
      if (!selectedPacket) return null;
      return await plansApi.getPacketWorksheets(
        selectedPacket.student_id,
        selectedPacket.packet_id
      );
    },
    enabled: !!selectedPacket && planDetailOpen,
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
      await plansApi.submitFeedback(studentId, packetId, {
        mastery_feedback: { overall: mastery },
        quantity_feedback: quantity,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-weekly-packets'] });
      setFeedbackModalOpen(false);
      setPlanDetailOpen(false);
      setSelectedPacket(null);
      setMasteryRating(null);
      setQuantityRating(null);
    },
  });

  const handleViewPlan = (packet: any) => {
    setSelectedPacket(packet);
    setPlanDetailOpen(true);
    setExpandedDay(null);
  };

  const handleProvideFeedback = () => {
    setMasteryRating(null);
    setQuantityRating(null);
    setFeedbackModalOpen(true);
    setPlanDetailOpen(false);
  };

  const handleSubmitFeedback = () => {
    if (!selectedPacket || !masteryRating || !quantityRating) return;

    feedbackMutation.mutate({
      studentId: selectedPacket.student_id,
      packetId: selectedPacket.packet_id,
      mastery: masteryRating,
      quantity: quantityRating,
    });
  };

  const handleDownloadArtifact = (downloadUrl: string) => {
    // downloadUrl is already the correct path like /students/{id}/worksheet-artifacts/{artifact_id}
    const fullUrl = `/api${downloadUrl}`;
    window.open(fullUrl, '_blank');
  };

  // Helper to get artifacts for a specific day and resource type
  const getArtifactsForDay = (dayLabel: string) => {
    if (!worksheetData?.items) return [];
    return worksheetData.items.filter((item: any) => item.day_label === dayLabel);
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

  if (pendingLoading || completedLoading) {
    return (
      <div className="bg-background min-h-screen">
        <Navigation />
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 w-48 rounded bg-neutral-200"></div>
            <div className="h-64 rounded bg-neutral-200"></div>
          </div>
        </div>
      </div>
    );
  }

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

        {/* Pending Plans - Prominent Section */}
        {pendingPackets && pendingPackets.length > 0 && (
          <section className="mb-12">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-foreground text-2xl font-semibold">
                Pending Plans - Feedback Needed!
              </h2>
              <Badge variant="warning" className="px-4 py-2 text-base">
                {pendingPackets.length} {pendingPackets.length === 1 ? 'Plan' : 'Plans'} Awaiting
                Feedback
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
                    Click on a plan to view details, then provide feedback to help the AI understand
                    which concepts your student has mastered.
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
                        <span className="text-foreground ml-2 font-medium">{packet.subject}</span>
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

                    {packet.worksheet_counts && Object.keys(packet.worksheet_counts).length > 0 && (
                      <div className="border-t border-neutral-200 pt-2">
                        <p className="mb-2 text-xs text-neutral-600">Worksheets:</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(packet.worksheet_counts).map(([type, count]) => (
                            <span key={type} className="rounded bg-neutral-100 px-2 py-1 text-xs">
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
      </main>

      {/* Plan Detail Modal */}
      {selectedPacket && planDetailOpen && (
        <Modal
          isOpen={planDetailOpen}
          onClose={() => {
            setPlanDetailOpen(false);
            setSelectedPacket(null);
            setExpandedDay(null);
          }}
          title={`${selectedPacket.studentName} - Week of ${formatDate(selectedPacket.week_of)}`}
        >
          <div className="space-y-6">
            {planDetailLoading ? (
              <div className="animate-pulse space-y-4">
                <div className="h-20 rounded bg-neutral-200"></div>
                <div className="h-40 rounded bg-neutral-200"></div>
              </div>
            ) : planDetail ? (
              <>
                {/* Plan Summary */}
                <div className="rounded-lg bg-neutral-50 p-4">
                  <h4 className="text-foreground mb-2 font-semibold">Plan Summary</h4>
                  {planDetail.weekly_overview && (
                    <p className="mb-3 text-sm text-neutral-700">{planDetail.weekly_overview}</p>
                  )}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-neutral-600">Subject:</span>
                      <span className="ml-2 font-medium">{planDetail.subject}</span>
                    </div>
                    <div>
                      <span className="text-neutral-600">Grade Level:</span>
                      <span className="ml-2 font-medium">
                        {planDetail.grade_level === 0
                          ? 'Kindergarten'
                          : `Grade ${planDetail.grade_level}`}
                      </span>
                    </div>
                    <div>
                      <span className="text-neutral-600">Duration:</span>
                      <span className="ml-2 font-medium">
                        {planDetail.daily_plan?.length || 0} days
                      </span>
                    </div>
                    <div>
                      <span className="text-neutral-600">Week Of:</span>
                      <span className="ml-2 font-medium">{formatDate(planDetail.week_of)}</span>
                    </div>
                  </div>
                </div>

                {/* Daily Activities Accordion */}
                {planDetail.daily_plan && planDetail.daily_plan.length > 0 && (
                  <div>
                    <h4 className="text-foreground mb-3 font-semibold">Daily Activities</h4>
                    <div className="space-y-2">
                      {planDetail.daily_plan.map((day: any, index: number) => (
                        <div
                          key={index}
                          className="overflow-hidden rounded-lg border border-neutral-200"
                        >
                          <button
                            onClick={() => setExpandedDay(expandedDay === index ? null : index)}
                            className="flex w-full items-center justify-between bg-white p-4 text-left transition-colors hover:bg-neutral-50"
                          >
                            <div>
                              <h5 className="text-foreground font-semibold">{day.day}</h5>
                              {day.focus && (
                                <p className="mt-1 text-sm text-neutral-600">{day.focus}</p>
                              )}
                            </div>
                            <svg
                              className={`h-5 w-5 text-neutral-600 transition-transform ${
                                expandedDay === index ? 'rotate-180' : ''
                              }`}
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 9l-7 7-7-7"
                              />
                            </svg>
                          </button>

                          {expandedDay === index && (
                            <div className="space-y-4 border-t border-neutral-200 bg-neutral-50 p-4">
                              {/* Lesson Objective */}
                              {day.lesson_plan?.objective && (
                                <div>
                                  <h6 className="text-foreground mb-1 text-sm font-semibold">
                                    Objective
                                  </h6>
                                  <p className="text-sm text-neutral-700">
                                    {day.lesson_plan.objective}
                                  </p>
                                </div>
                              )}

                              {/* Materials */}
                              {day.lesson_plan?.materials_needed &&
                                day.lesson_plan.materials_needed.length > 0 && (
                                  <div>
                                    <h6 className="text-foreground mb-1 text-sm font-semibold">
                                      Materials Needed
                                    </h6>
                                    <ul className="list-inside list-disc text-sm text-neutral-700">
                                      {day.lesson_plan.materials_needed.map(
                                        (material: string, i: number) => (
                                          <li key={i}>{material}</li>
                                        )
                                      )}
                                    </ul>
                                  </div>
                                )}

                              {/* Procedure */}
                              {day.lesson_plan?.procedure &&
                                day.lesson_plan.procedure.length > 0 && (
                                  <div>
                                    <h6 className="text-foreground mb-1 text-sm font-semibold">
                                      Procedure
                                    </h6>
                                    <ol className="list-inside list-decimal space-y-1 text-sm text-neutral-700">
                                      {day.lesson_plan.procedure.map((step: string, i: number) => (
                                        <li key={i} className="pl-2">
                                          {step}
                                        </li>
                                      ))}
                                    </ol>
                                  </div>
                                )}

                              {/* Worksheets */}
                              {(() => {
                                const dayArtifacts = getArtifactsForDay(day.day);
                                if (dayArtifacts.length === 0) return null;

                                return (
                                  <div>
                                    <h6 className="text-foreground mb-2 text-sm font-semibold">
                                      Worksheets
                                    </h6>
                                    <div className="space-y-2">
                                      {dayArtifacts.map((artifactGroup: any) => {
                                        // Get the PDF artifact from this group
                                        const pdfArtifact = artifactGroup.artifacts.find(
                                          (a: any) => a.format === 'pdf'
                                        );
                                        if (!pdfArtifact) return null;

                                        // Use the resource info from day's resources if available
                                        const resourceKey = artifactGroup.resource_kind;
                                        const resourceInfo = day.resources?.[resourceKey];

                                        return (
                                          <div
                                            key={pdfArtifact.artifact_id}
                                            className="flex items-center justify-between rounded border border-neutral-200 bg-white p-3"
                                          >
                                            <div className="flex items-center space-x-2">
                                              <svg
                                                className="text-primary-600 h-5 w-5"
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
                                              <div>
                                                <p className="text-foreground text-sm font-medium">
                                                  {resourceInfo?.title || resourceKey}
                                                </p>
                                                <p className="text-xs text-neutral-600">PDF</p>
                                              </div>
                                            </div>
                                            <div className="flex space-x-2">
                                              <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() =>
                                                  handleDownloadArtifact(pdfArtifact.download_url)
                                                }
                                              >
                                                View
                                              </Button>
                                              <Button
                                                size="sm"
                                                variant="secondary"
                                                onClick={() =>
                                                  handleDownloadArtifact(pdfArtifact.download_url)
                                                }
                                              >
                                                Download
                                              </Button>
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                );
                              })()}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Provide Feedback Button */}
                {selectedPacket.status !== 'complete' && (
                  <div className="border-t border-neutral-200 pt-4">
                    <Button
                      onClick={handleProvideFeedback}
                      className="bg-primary-600 hover:bg-primary-700 w-full font-semibold"
                      size="lg"
                    >
                      Provide Feedback
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="py-8 text-center text-neutral-600">Failed to load plan details</div>
            )}
          </div>
        </Modal>
      )}

      {/* Feedback Modal */}
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
            <div className="rounded bg-neutral-50 p-4">
              <h4 className="text-foreground mb-1 font-semibold">{selectedPacket.studentName}</h4>
              <p className="text-sm text-neutral-600">
                {selectedPacket.subject} - Grade {selectedPacket.grade_level} - Week of{' '}
                {formatDate(selectedPacket.week_of)}
              </p>
            </div>

            {/* Mastery Feedback */}
            <div>
              <label className="mb-3 block text-sm font-medium text-neutral-700">
                How well did your student master the concepts this week?
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => setMasteryRating('STRUGGLING')}
                  className={`rounded-lg border-2 p-4 text-center transition-all ${
                    masteryRating === 'STRUGGLING'
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-primary-400 border-neutral-300'
                  }`}
                >
                  <div className="mb-1 text-2xl">😰</div>
                  <div className="text-sm font-medium">Struggling</div>
                </button>
                <button
                  onClick={() => setMasteryRating('DEVELOPING')}
                  className={`rounded-lg border-2 p-4 text-center transition-all ${
                    masteryRating === 'DEVELOPING'
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-primary-400 border-neutral-300'
                  }`}
                >
                  <div className="mb-1 text-2xl">🤔</div>
                  <div className="text-sm font-medium">Developing</div>
                </button>
                <button
                  onClick={() => setMasteryRating('MASTERED')}
                  className={`rounded-lg border-2 p-4 text-center transition-all ${
                    masteryRating === 'MASTERED'
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-primary-400 border-neutral-300'
                  }`}
                >
                  <div className="mb-1 text-2xl">🎉</div>
                  <div className="text-sm font-medium">Mastered</div>
                </button>
              </div>
            </div>

            {/* Quantity Feedback */}
            <div>
              <label className="mb-3 block text-sm font-medium text-neutral-700">
                Was the amount of work appropriate?
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => setQuantityRating('TOO_MUCH')}
                  className={`rounded-lg border-2 p-4 text-center transition-all ${
                    quantityRating === 'TOO_MUCH'
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-primary-400 border-neutral-300'
                  }`}
                >
                  <div className="mb-1 text-2xl">📚</div>
                  <div className="text-sm font-medium">Too Much</div>
                </button>
                <button
                  onClick={() => setQuantityRating('JUST_RIGHT')}
                  className={`rounded-lg border-2 p-4 text-center transition-all ${
                    quantityRating === 'JUST_RIGHT'
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-primary-400 border-neutral-300'
                  }`}
                >
                  <div className="mb-1 text-2xl">✅</div>
                  <div className="text-sm font-medium">Just Right</div>
                </button>
                <button
                  onClick={() => setQuantityRating('TOO_LITTLE')}
                  className={`rounded-lg border-2 p-4 text-center transition-all ${
                    quantityRating === 'TOO_LITTLE'
                      ? 'border-primary-600 bg-primary-50'
                      : 'hover:border-primary-400 border-neutral-300'
                  }`}
                >
                  <div className="mb-1 text-2xl">📖</div>
                  <div className="text-sm font-medium">Too Little</div>
                </button>
              </div>
            </div>

            {feedbackMutation.error && (
              <div className="bg-danger-50 border-danger-200 text-danger-700 rounded border p-3 text-sm">
                {feedbackMutation.error instanceof Error
                  ? feedbackMutation.error.message
                  : 'Failed to submit feedback'}
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setFeedbackModalOpen(false);
                  setMasteryRating(null);
                  setQuantityRating(null);
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSubmitFeedback}
                disabled={!masteryRating || !quantityRating || feedbackMutation.isPending}
                className="bg-primary-600 hover:bg-primary-700"
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
        students={(students || []).map((s) => ({
          id: s.student_id,
          name: parseMetadata(s.metadata_blob)?.name || 'Unknown',
          grade: 0, // TODO: Extract from student metadata
        }))}
        onSuccess={() => {
          showToast('Plan is being generated! The page will refresh when complete.', 'success');
        }}
      />
    </div>
  );
}
