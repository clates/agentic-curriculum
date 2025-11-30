'use client';

import { Card, Button, Badge } from '@/components/ui';
import { Navigation } from '@/components/Navigation';
import { useEnrichedStudents, useWeeklyPacketsStats } from '@/lib/hooks';

export default function Dashboard() {
  const { students, isLoading: studentsLoading, error: studentsError } = useEnrichedStudents();
  const { data: stats, isLoading: statsLoading } = useWeeklyPacketsStats();

  const progressPercentage = (mastered: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((mastered / total) * 100);
  };

  // Loading state
  if (studentsLoading) {
    return (
      <div className="min-h-screen bg-background">
        <nav className="bg-white border-b border-neutral-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-2xl font-semibold text-primary-600">CurricuLearn</h1>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-12 bg-neutral-200 rounded w-64 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-neutral-200 rounded-md"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-64 bg-neutral-200 rounded-md"></div>
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
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <div className="text-center">
            <svg className="w-12 h-12 text-danger-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-xl font-semibold text-foreground mb-2">Failed to Load Students</h2>
            <p className="text-neutral-600 mb-4">Unable to connect to the backend API. Please make sure the backend server is running.</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Bar */}
      <Navigation />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-primary-200 rounded-full"></div>
            <h2 className="text-2xl font-semibold text-foreground">Welcome back, Sarah!</h2>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <a href="/students">
            <Card className="hover:-translate-y-0.5 transition-transform cursor-pointer">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-3xl font-semibold text-foreground">{students.length}</p>
                  <p className="text-sm text-neutral-600">Active Students</p>
                </div>
              </div>
            </Card>
          </a>

          <Card className="hover:-translate-y-0.5 transition-transform">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-secondary-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p className="text-3xl font-semibold text-foreground">
                  {statsLoading ? '...' : stats?.activePlans || 0}
                </p>
                <p className="text-sm text-neutral-600">Plans This Week</p>
              </div>
            </div>
          </Card>

          <Card className="hover:-translate-y-0.5 transition-transform">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-secondary-50 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p className="text-3xl font-semibold text-foreground">
                  {statsLoading ? '...' : stats?.totalWorksheets || 0}
                </p>
                <p className="text-sm text-neutral-600">Worksheets Ready</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Your Students Section */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-foreground mb-6">Your Students</h3>
        </div>

        {/* Student Cards Grid */}
        {students.length === 0 ? (
          <Card className="text-center py-12">
            <svg className="w-16 h-16 text-neutral-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <h3 className="text-lg font-medium text-foreground mb-2">No Students Yet</h3>
            <p className="text-neutral-600 mb-4">Get started by adding your first student</p>
            <Button variant="primary">Add Student</Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {students.map((student) => (
              <Card key={student.id} padding="lg" className="hover:-translate-y-1 transition-transform">
                <div className="flex flex-col space-y-4">
                  {/* Avatar and Name */}
                  <div className="flex items-center space-x-3">
                    {student.avatarUrl ? (
                      <img src={student.avatarUrl} alt={student.name} className="w-16 h-16 rounded-full" />
                    ) : (
                      <div className="w-16 h-16 bg-primary-200 rounded-full flex-shrink-0"></div>
                    )}
                    <div className="flex-1 min-w-0">
                      <h4 className="text-lg font-semibold text-foreground truncate">{student.name}</h4>
                      <Badge variant="default" className="mt-1">{student.grade}</Badge>
                    </div>
                  </div>

                  {/* Subject */}
                  <div>
                    <Badge variant="subject">{student.subject}</Badge>
                  </div>

                  {/* Progress Bar */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-neutral-600">Progress</span>
                      <span className="font-medium text-foreground">
                        {student.masteredCount}/{student.totalStandards} Standards
                      </span>
                    </div>
                    <div className="w-full bg-neutral-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full transition-all duration-300"
                        style={{ width: `${progressPercentage(student.masteredCount, student.totalStandards)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-neutral-500 mt-1">
                      {progressPercentage(student.masteredCount, student.totalStandards)}% Complete
                    </p>
                  </div>

                  {/* View Progress Button */}
                  <Button variant="secondary" size="md" className="w-full">
                    View Progress
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Floating Action Button */}
        <button
          className="fixed bottom-8 right-8 w-14 h-14 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-full shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-200 flex items-center justify-center"
          aria-label="Add Student"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </main>
    </div>
  );
}
