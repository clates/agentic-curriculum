'use client';

import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { Card, Button, Badge, Modal } from '@/components/ui';
import { Navigation } from '@/components/Navigation';
import { usePendingPackets, useCompletedPackets } from '@/lib/hooks';
import { plansApi } from '@/lib/api';

export default function PlansPage() {
  const { packets: pendingPackets, isLoading: pendingLoading } = usePendingPackets();
  const { packets: completedPackets, isLoading: completedLoading } = useCompletedPackets();
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [planDetailOpen, setPlanDetailOpen] = useState(false);
  const [selectedPacket, setSelectedPacket] = useState<any>(null);
  const [expandedDay, setExpandedDay] = useState<number | null>(null);
  const [masteryRating, setMasteryRating] = useState<string | null>(null);
  const [quantityRating, setQuantityRating] = useState<string | null>(null);

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
      return await plansApi.getPacketWorksheets(selectedPacket.student_id, selectedPacket.packet_id);
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
  const  getArtifactsForDay = (dayLabel: string) => {
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
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-neutral-200 rounded w-48"></div>
            <div className="h-64 bg-neutral-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-semibold text-foreground mb-2">Weekly Plans</h1>
          <p className="text-neutral-600">Review lesson plans and provide feedback to improve future lessons</p>
        </div>

        {/* Pending Plans - Prominent Section */}
        {pendingPackets && pendingPackets.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-foreground">Pending Plans - Feedback Needed!</h2>
              <Badge variant="warning" className="text-base px-4 py-2">
                {pendingPackets.length} {pendingPackets.length === 1 ? 'Plan' : 'Plans'} Awaiting Feedback
              </Badge>
            </div>

            <div className="bg-primary-50 border-2 border-primary-200 rounded-lg p-6 mb-6">
              <div className="flex items-start space-x-4">
                <svg className="w-6 h-6 text-primary-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Your Feedback Shapes Future Lessons</h3>
                  <p className="text-sm text-neutral-700">
                    Click on a plan to view details, then provide feedback to help the AI understand which concepts your student has mastered.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {pendingPackets.map((packet) => (
                <Card
                  key={packet.packet_id}
                  padding="lg"
                  className="border-2 border-primary-200 cursor-pointer hover:border-primary-400 hover:shadow-md transition-all"
                  onClick={() => handleViewPlan(packet)}
                >
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-xl font-semibold text-foreground">{packet.studentName}</h3>
                        <p className="text-sm text-neutral-600">Week of {formatDate(packet.week_of)}</p>
                      </div>
                      <Badge variant={packet.status === 'ready' ? 'success' : 'default'}>
                        {packet.status}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-neutral-600">Subject:</span>
                        <span className="ml-2 font-medium text-foreground">{packet.subject}</span>
                      </div>
                      <div>
                        <span className="text-neutral-600">Grade:</span>
                        <span className="ml-2 font-medium text-foreground">{packet.grade_level}</span>
                      </div>
                      <div>
                        <span className="text-neutral-600">Days:</span>
                        <span className="ml-2 font-medium text-foreground">{packet.resource_days}</span>
                      </div>
                      <div>
                        <span className="text-neutral-600">Activities:</span>
                        <span className="ml-2 font-medium text-foreground">{packet.daily_count} per day</span>
                      </div>
                    </div>

                    {packet.worksheet_counts && Object.keys(packet.worksheet_counts).length > 0 && (
                      <div className="pt-2 border-t border-neutral-200">
                        <p className="text-xs text-neutral-600 mb-2">Worksheets:</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(packet.worksheet_counts).map(([type, count]) => (
                            <span key={type} className="text-xs bg-neutral-100 px-2 py-1 rounded">
                              {type}: {count}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="pt-2 text-sm text-primary-600 font-medium">
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
            <h2 className="text-2xl font-semibold text-foreground mb-6">Completed Plans</h2>
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-neutral-50 border-b border-neutral-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-600 uppercase tracking-wider">
                        Student
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-600 uppercase tracking-wider">
                        Week Of
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-600 uppercase tracking-wider">
                        Subject
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-600 uppercase tracking-wider">
                        Grade
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-600 uppercase tracking-wider">
                        Artifacts
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral-600 uppercase tracking-wider">
                        Updated
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-neutral-200">
                    {completedPackets.map((packet) => (
                      <tr key={packet.packet_id} className="hover:bg-neutral-50 cursor-pointer" onClick={() => handleViewPlan(packet)}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground">
                          {packet.studentName}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
                          {formatDate(packet.week_of)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
                          {packet.subject}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
                          {packet.grade_level}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
                          {packet.artifact_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
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
        {(!pendingPackets || pendingPackets.length === 0) && (!completedPackets || completedPackets.length === 0) && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <svg className="w-16 h-16 text-neutral-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-foreground mb-2">No Plans Yet</h3>
            <p className="text-neutral-600">Weekly lesson plans will appear here once generated</p>
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
                <div className="h-20 bg-neutral-200 rounded"></div>
                <div className="h-40 bg-neutral-200 rounded"></div>
              </div>
            ) : planDetail ? (
              <>
                {/* Plan Summary */}
                <div className="bg-neutral-50 rounded-lg p-4">
                  <h4 className="font-semibold text-foreground mb-2">Plan Summary</h4>
                  {planDetail.weekly_overview && (
                    <p className="text-sm text-neutral-700 mb-3">{planDetail.weekly_overview}</p>
                  )}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-neutral-600">Subject:</span>
                      <span className="ml-2 font-medium">{planDetail.subject}</span>
                    </div>
                    <div>
                      <span className="text-neutral-600">Grade Level:</span>
                      <span className="ml-2 font-medium">{planDetail.grade_level === 0 ? 'Kindergarten' : `Grade ${planDetail.grade_level}`}</span>
                    </div>
                    <div>
                      <span className="text-neutral-600">Duration:</span>
                      <span className="ml-2 font-medium">{planDetail.daily_plan?.length || 0} days</span>
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
                    <h4 className="font-semibold text-foreground mb-3">Daily Activities</h4>
                    <div className="space-y-2">
                      {planDetail.daily_plan.map((day: any, index: number) => (
                        <div key={index} className="border border-neutral-200 rounded-lg overflow-hidden">
                          <button
                            onClick={() => setExpandedDay(expandedDay === index ? null : index)}
                            className="w-full flex items-center justify-between p-4 bg-white hover:bg-neutral-50 transition-colors text-left"
                          >
                            <div>
                              <h5 className="font-semibold text-foreground">{day.day}</h5>
                              {day.focus && (
                                <p className="text-sm text-neutral-600 mt-1">{day.focus}</p>
                              )}
                            </div>
                            <svg
                              className={`w-5 h-5 text-neutral-600 transition-transform ${
                                expandedDay === index ? 'rotate-180' : ''
                              }`}
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </button>

                          {expandedDay === index && (
                            <div className="p-4 bg-neutral-50 border-t border-neutral-200 space-y-4">
                              {/* Lesson Objective */}
                              {day.lesson_plan?.objective && (
                                <div>
                                  <h6 className="text-sm font-semibold text-foreground mb-1">Objective</h6>
                                  <p className="text-sm text-neutral-700">{day.lesson_plan.objective}</p>
                                </div>
                              )}

                              {/* Materials */}
                              {day.lesson_plan?.materials_needed && day.lesson_plan.materials_needed.length > 0 && (
                                <div>
                                  <h6 className="text-sm font-semibold text-foreground mb-1">Materials Needed</h6>
                                  <ul className="text-sm text-neutral-700 list-disc list-inside">
                                    {day.lesson_plan.materials_needed.map((material: string, i: number) => (
                                      <li key={i}>{material}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Procedure */}
                              {day.lesson_plan?.procedure && day.lesson_plan.procedure.length > 0 && (
                                <div>
                                  <h6 className="text-sm font-semibold text-foreground mb-1">Procedure</h6>
                                  <ol className="text-sm text-neutral-700 list-decimal list-inside space-y-1">
                                    {day.lesson_plan.procedure.map((step: string, i: number) => (
                                      <li key={i} className="pl-2">{step}</li>
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
                                    <h6 className="text-sm font-semibold text-foreground mb-2">Worksheets</h6>
                                    <div className="space-y-2">
                                      {dayArtifacts.map((artifactGroup: any) => {
                                        // Get the PDF artifact from this group
                                        const pdfArtifact = artifactGroup.artifacts.find((a: any) => a.format === 'pdf');
                                        if (!pdfArtifact) return null;

                                        // Use the resource info from day's resources if available
                                        const resourceKey = artifactGroup.resource_kind;
                                        const resourceInfo = day.resources?.[resourceKey];

                                        return (
                                          <div key={pdfArtifact.artifact_id} className="flex items-center justify-between bg-white border border-neutral-200 rounded p-3">
                                            <div className="flex items-center space-x-2">
                                              <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                              </svg>
                                              <div>
                                                <p className="text-sm font-medium text-foreground">{resourceInfo?.title || resourceKey}</p>
                                                <p className="text-xs text-neutral-600">PDF</p>
                                              </div>
                                            </div>
                                            <div className="flex space-x-2">
                                              <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => handleDownloadArtifact(pdfArtifact.download_url)}
                                              >
                                                View
                                              </Button>
                                              <Button
                                                size="sm"
                                                variant="secondary"
                                                onClick={() => handleDownloadArtifact(pdfArtifact.download_url)}
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
                  <div className="pt-4 border-t border-neutral-200">
                    <Button onClick={handleProvideFeedback} className="w-full bg-primary-600 hover:bg-primary-700 font-semibold" size="lg">
                      Provide Feedback
                    </Button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8 text-neutral-600">
                Failed to load plan details
              </div>
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
            <div className="bg-neutral-50 rounded p-4">
              <h4 className="font-semibold text-foreground mb-1">{selectedPacket.studentName}</h4>
              <p className="text-sm text-neutral-600">
                {selectedPacket.subject} - Grade {selectedPacket.grade_level} - Week of {formatDate(selectedPacket.week_of)}
              </p>
            </div>

            {/* Mastery Feedback */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                How well did your student master the concepts this week?
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => setMasteryRating('STRUGGLING')}
                  className={`p-4 border-2 rounded-lg text-center transition-all ${
                    masteryRating === 'STRUGGLING'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-neutral-300 hover:border-primary-400'
                  }`}
                >
                  <div className="text-2xl mb-1">😰</div>
                  <div className="text-sm font-medium">Struggling</div>
                </button>
                <button
                  onClick={() => setMasteryRating('DEVELOPING')}
                  className={`p-4 border-2 rounded-lg text-center transition-all ${
                    masteryRating === 'DEVELOPING'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-neutral-300 hover:border-primary-400'
                  }`}
                >
                  <div className="text-2xl mb-1">🤔</div>
                  <div className="text-sm font-medium">Developing</div>
                </button>
                <button
                  onClick={() => setMasteryRating('MASTERED')}
                  className={`p-4 border-2 rounded-lg text-center transition-all ${
                    masteryRating === 'MASTERED'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-neutral-300 hover:border-primary-400'
                  }`}
                >
                  <div className="text-2xl mb-1">🎉</div>
                  <div className="text-sm font-medium">Mastered</div>
                </button>
              </div>
            </div>

            {/* Quantity Feedback */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                Was the amount of work appropriate?
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => setQuantityRating('TOO_MUCH')}
                  className={`p-4 border-2 rounded-lg text-center transition-all ${
                    quantityRating === 'TOO_MUCH'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-neutral-300 hover:border-primary-400'
                  }`}
                >
                  <div className="text-2xl mb-1">📚</div>
                  <div className="text-sm font-medium">Too Much</div>
                </button>
                <button
                  onClick={() => setQuantityRating('JUST_RIGHT')}
                  className={`p-4 border-2 rounded-lg text-center transition-all ${
                    quantityRating === 'JUST_RIGHT'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-neutral-300 hover:border-primary-400'
                  }`}
                >
                  <div className="text-2xl mb-1">✅</div>
                  <div className="text-sm font-medium">Just Right</div>
                </button>
                <button
                  onClick={() => setQuantityRating('TOO_LITTLE')}
                  className={`p-4 border-2 rounded-lg text-center transition-all ${
                    quantityRating === 'TOO_LITTLE'
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-neutral-300 hover:border-primary-400'
                  }`}
                >
                  <div className="text-2xl mb-1">📖</div>
                  <div className="text-sm font-medium">Too Little</div>
                </button>
              </div>
            </div>

            {feedbackMutation.error && (
              <div className="bg-danger-50 border border-danger-200 rounded p-3 text-sm text-danger-700">
                {feedbackMutation.error instanceof Error ? feedbackMutation.error.message : 'Failed to submit feedback'}
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
    </div>
  );
}
