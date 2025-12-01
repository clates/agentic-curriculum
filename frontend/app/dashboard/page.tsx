'use client';

import { useState } from 'react';
import { Card, Button, Badge } from '@/components/ui';
import { Navigation } from '@/components/Navigation';
import { useEnrichedStudents, useWeeklyPacketsStats, usePendingPackets } from '@/lib/hooks';
import { GeneratePlanModal } from '@/components/GeneratePlanModal';
import { useToast } from '@/components/ToastProvider';

export default function Dashboard() {
  const { students, isLoading: studentsLoading, error: studentsError } = useEnrichedStudents();
  const { data: stats, isLoading: statsLoading } = useWeeklyPacketsStats();
  const { packets: pendingPackets } = usePendingPackets();
  const { showToast } = useToast();

  const [generateModalOpen, setGenerateModalOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<{
    id: string;
    name: string;
    grade: number;
  } | null>(null);

  const progressPercentage = (mastered: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((mastered / total) * 100);
  };

  // Loading state
  if (studentsLoading) {
    return (
      <div className="bg-background min-h-screen">
        <nav className="border-b border-neutral-200 bg-white shadow-sm">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              <h1 className="text-primary-600 text-2xl font-semibold">CurricuLearn</h1>
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="mb-8 h-12 w-64 rounded bg-neutral-200"></div>
            <div className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 rounded-md bg-neutral-200"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-64 rounded-md bg-neutral-200"></div>
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Error state
  if (studentsError) {
    return (
      <div className="bg-background flex min-h-screen items-center justify-center">
        <Card className="max-w-md">
          <div className="text-center">
            <svg
              className="text-danger-500 mx-auto mb-4 h-12 w-12"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h2 className="text-foreground mb-2 text-xl font-semibold">Failed to Load Students</h2>
            <p className="mb-4 text-neutral-600">
              Unable to connect to the backend API. Please make sure the backend server is running.
            </p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <>
      <div className="bg-background min-h-screen">
        {/* Navigation Bar */}
        <Navigation />

        {/* Main Content */}
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {/* Welcome Header */}
          <div className="mb-8">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-200 h-12 w-12 rounded-full"></div>
              <h2 className="text-foreground text-2xl font-semibold">Welcome back, Sarah!</h2>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-3">
            <a href="/students">
              <Card className="cursor-pointer transition-transform hover:-translate-y-0.5">
                <div className="flex items-center space-x-4">
                  <div className="bg-primary-100 flex h-12 w-12 items-center justify-center rounded-full">
                    <svg
                      className="text-primary-600 h-6 w-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-foreground text-3xl font-semibold">{students.length}</p>
                    <p className="text-sm text-neutral-600">Active Students</p>
                  </div>
                </div>
              </Card>
            </a>

            <Card className="transition-transform hover:-translate-y-0.5">
              <div className="flex items-center space-x-4">
                <div className="bg-secondary-100 flex h-12 w-12 items-center justify-center rounded-full">
                  <svg
                    className="text-secondary-600 h-6 w-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div>
                  <p className="text-foreground text-3xl font-semibold">
                    {statsLoading ? '...' : stats?.activePlans || 0}
                  </p>
                  <p className="text-sm text-neutral-600">Plans This Week</p>
                </div>
              </div>
            </Card>

            <Card className="transition-transform hover:-translate-y-0.5">
              <div className="flex items-center space-x-4">
                <div className="bg-secondary-50 flex h-12 w-12 items-center justify-center rounded-full">
                  <svg
                    className="text-secondary-600 h-6 w-6"
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
                </div>
                <div>
                  <p className="text-foreground text-3xl font-semibold">
                    {statsLoading ? '...' : stats?.totalWorksheets || 0}
                  </p>
                  <p className="text-sm text-neutral-600">Worksheets Ready</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Your Students Section */}
          <div className="mb-6">
            <h3 className="text-foreground mb-6 text-xl font-semibold">Your Students</h3>
          </div>

          {/* Student Cards Grid */}
          {students.length === 0 ? (
            <Card className="py-12 text-center">
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
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
              <h3 className="text-foreground mb-2 text-lg font-medium">No Students Yet</h3>
              <p className="mb-4 text-neutral-600">Get started by adding your first student</p>
              <Button variant="primary">Add Student</Button>
            </Card>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {students.map((student) => (
                <Card
                  key={student.id}
                  padding="lg"
                  className="transition-transform hover:-translate-y-1"
                >
                  <div className="flex flex-col space-y-4">
                    {/* Avatar and Name */}
                    <div className="flex items-center space-x-3">
                      {student.avatarUrl ? (
                        <img
                          src={student.avatarUrl}
                          alt={student.name}
                          className="h-16 w-16 rounded-full"
                        />
                      ) : (
                        <div className="bg-primary-200 h-16 w-16 flex-shrink-0 rounded-full"></div>
                      )}
                      <div className="min-w-0 flex-1">
                        <h4 className="text-foreground truncate text-lg font-semibold">
                          {student.name}
                        </h4>
                        <Badge variant="default" className="mt-1">
                          {student.grade}
                        </Badge>
                      </div>
                    </div>

                    {/* Subject */}
                    <div>
                      <Badge variant="subject">{student.subject}</Badge>
                    </div>

                    {/* Progress Bar */}
                    <div>
                      <div className="mb-2 flex justify-between text-sm">
                        <span className="text-neutral-600">Progress</span>
                        <span className="text-foreground font-medium">
                          {student.masteredCount}/{student.totalStandards} Standards
                        </span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-neutral-100">
                        <div
                          className="from-primary-500 to-secondary-500 h-full rounded-full bg-gradient-to-r transition-all duration-300"
                          style={{
                            width: `${progressPercentage(
                              student.masteredCount,
                              student.totalStandards
                            )}%`,
                          }}
                        ></div>
                      </div>
                      <p className="mt-1 text-xs text-neutral-500">
                        {progressPercentage(student.masteredCount, student.totalStandards)}%
                        Complete
                      </p>
                    </div>

                    {/* Action Button */}
                    {(() => {
                      // Check if this student has pending packets
                      const hasPendingPacket = pendingPackets?.some(
                        (p) => p.student_id === student.id
                      );

                      if (hasPendingPacket) {
                        return (
                          <Button variant="primary" size="md" className="w-full">
                            Submit Feedback
                          </Button>
                        );
                      } else {
                        return (
                          <Button
                            variant="secondary"
                            size="md"
                            className="w-full"
                            onClick={() => {
                              setSelectedStudent({
                                id: student.id,
                                name: student.name,
                                grade: 0, // TODO: extract from student metadata
                              });
                              setGenerateModalOpen(true);
                            }}
                          >
                            Generate Plan
                          </Button>
                        );
                      }
                    })()}
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Floating Action Button */}
          <button
            className="from-primary-500 to-secondary-500 fixed right-8 bottom-8 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r text-white shadow-lg transition-all duration-200 hover:-translate-y-1 hover:shadow-xl"
            aria-label="Add Student"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </button>
        </main>
      </div>

      {/* Generate Plan Modal */}
      <GeneratePlanModal
        isOpen={generateModalOpen}
        onClose={() => {
          setGenerateModalOpen(false);
          setSelectedStudent(null);
        }}
        preSelectedStudent={selectedStudent || undefined}
        onSuccess={() => {
          showToast('Plan is being generated! Go to Plans page to view progress.', 'success');
        }}
      />
    </>
  );
}
