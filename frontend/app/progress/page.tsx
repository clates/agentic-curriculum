'use client';

import { useState, useEffect } from 'react';
import { Navigation } from '@/components/Navigation';
import { SkillTree } from '@/components/SkillTree';
import { useStudents, useStudentProgressMap, useSystemOptions } from '@/lib/hooks';
import { Card, Badge, Button } from '@/components/ui';
import { parseMetadata } from '@/lib/api';

export default function ProgressPage() {
  const { data: students, isLoading: studentsLoading } = useStudents();
  const { data: systemOptions } = useSystemOptions();

  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('English');
  const [showFullGraph, setShowFullGraph] = useState(false);

  const { data: graphData, isLoading: graphLoading } = useStudentProgressMap(
    selectedStudentId,
    selectedSubject,
    !showFullGraph
  );

  return (
    <div className="bg-background min-h-screen">
      <Navigation />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-foreground text-3xl font-bold">Curriculum Progress Map</h1>
          <p className="text-neutral-600 mt-2">
            Visualize standard dependencies and track student mastery across the curriculum.
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-secondary-700 mb-1 block text-sm font-medium">Student</label>
              <select
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                className="border-secondary-300 focus:border-primary-500 focus:ring-primary-500 block w-full rounded-md shadow-sm sm:text-sm"
              >
                <option value="">Select a student</option>
                {students?.map((s) => {
                  const metadata = parseMetadata(s.metadata_blob);
                  return (
                    <option key={s.student_id} value={s.student_id}>
                      {metadata?.name || s.student_id}
                    </option>
                  );
                })}
              </select>
            </div>
            <div>
              <label className="text-secondary-700 mb-1 block text-sm font-medium">
                Subject Area
              </label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="border-secondary-300 focus:border-primary-500 focus:ring-primary-500 block w-full rounded-md shadow-sm sm:text-sm"
              >
                {systemOptions?.subjects.map((sub) => (
                  <option key={sub} value={sub}>
                    {sub}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-4 flex items-center">
            <input
              id="show-full-graph"
              type="checkbox"
              checked={showFullGraph}
              onChange={(e) => setShowFullGraph(e.target.checked)}
              className="h-4 w-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            />
            <label htmlFor="show-full-graph" className="ml-2 block text-sm text-neutral-700">
              Show full curriculum graph (disables pruning)
            </label>
          </div>
        </Card>

        {/* Legend */}
        <div className="mb-4 flex space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded bg-green-100 border border-green-300"></div>
            <span className="text-sm font-medium text-neutral-700">Mastered</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded bg-blue-100 border border-blue-300"></div>
            <span className="text-sm font-medium text-neutral-700">Ready to Learn</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded bg-gray-100 border border-gray-300"></div>
            <span className="text-sm font-medium text-neutral-700">Locked</span>
          </div>
        </div>

        {/* Skill Tree Visualization */}
        {graphLoading ? (
          <div className="h-[600px] w-full bg-neutral-100 animate-pulse rounded-2xl flex items-center justify-center">
            <p className="text-neutral-500 font-medium">Loading map...</p>
          </div>
        ) : graphData && graphData.nodes.length > 0 ? (
          <SkillTree nodes={graphData.nodes as any} edges={graphData.edges as any} />
        ) : (
          <div className="h-[400px] w-full bg-white border border-dashed border-neutral-300 rounded-2xl flex flex-col items-center justify-center">
            <svg
              className="w-12 h-12 text-neutral-300 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            <p className="text-neutral-500 font-medium">
              Select a student and subject to view the progress map.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
