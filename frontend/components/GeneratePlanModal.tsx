'use client';

import { useState, useEffect } from 'react';
import { Modal, Button } from '@/components/ui';
import { useSystemOptions, useGenerateWeeklyPlan } from '@/lib/hooks';
import type { WeeklyPacketDetail } from '@/lib/api';

export interface GeneratePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  preSelectedStudent?: { id: string; name: string; grade: number };
  students?: Array<{ id: string; name: string; grade: number }>;
  onSuccess?: (plan: WeeklyPacketDetail) => void;
}

export function GeneratePlanModal({
  isOpen,
  onClose,
  preSelectedStudent,
  students = [],
  onSuccess,
}: GeneratePlanModalProps) {
  const { data: systemOptions, isLoading: optionsLoading } = useSystemOptions();
  const generateMutation = useGenerateWeeklyPlan();

  const [selectedStudentId, setSelectedStudentId] = useState(preSelectedStudent?.id || '');
  const [subject, setSubject] = useState('');
  const [gradeLevel, setGradeLevel] = useState(preSelectedStudent?.grade || 0);

  // Update selected student when preSelectedStudent changes
  useEffect(() => {
    if (preSelectedStudent) {
      setSelectedStudentId(preSelectedStudent.id);
      setGradeLevel(preSelectedStudent.grade);
    }
  }, [preSelectedStudent]);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      generateMutation.reset();
      setSubject('');
      if (!preSelectedStudent) {
        setSelectedStudentId('');
        setGradeLevel(0);
      }
    }
  }, [isOpen, preSelectedStudent, generateMutation]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedStudentId || !subject) {
      return;
    }

    try {
      const plan = await generateMutation.mutateAsync({
        student_id: selectedStudentId,
        grade_level: gradeLevel,
        subject,
      });

      if (onSuccess) {
        onSuccess(plan);
      }

      onClose();
    } catch (error) {
      // Error is handled by the mutation state
      console.error('Failed to generate plan:', error);
    }
  };

  const selectedStudent = preSelectedStudent || students.find(s => s.id === selectedStudentId);
  const canSubmit = selectedStudentId && subject && !generateMutation.isPending;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Generate Weekly Plan">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Student Selector */}
        {!preSelectedStudent && students.length > 0 && (
          <div>
            <label htmlFor="student" className="block text-sm font-medium text-neutral-700 mb-2">
              Student
            </label>
            <select
              id="student"
              value={selectedStudentId}
              onChange={(e) => {
                setSelectedStudentId(e.target.value);
                const student = students.find(s => s.id === e.target.value);
                if (student) {
                  setGradeLevel(student.grade);
                }
              }}
              className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="">Select a student...</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Show selected student name if pre-selected */}
        {preSelectedStudent && (
          <div className="bg-neutral-50 rounded-lg p-4">
            <p className="text-sm text-neutral-600">Student</p>
            <p className="font-semibold text-foreground">{preSelectedStudent.name}</p>
          </div>
        )}

        {/* Subject Dropdown */}
        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-neutral-700 mb-2">
            Subject
          </label>
          {optionsLoading ? (
            <div className="h-10 bg-neutral-100 rounded animate-pulse" />
          ) : (
            <select
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="">Select a subject...</option>
              {systemOptions?.subjects.map(subj => (
                <option key={subj} value={subj}>
                  {subj}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Grade Level */}
        <div>
          <label htmlFor="grade" className="block text-sm font-medium text-neutral-700 mb-2">
            Grade Level
          </label>
          <select
            id="grade"
            value={gradeLevel}
            onChange={(e) => setGradeLevel(Number(e.target.value))}
            className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          >
            {systemOptions?.grades.map(grade => (
              <option key={grade.value} value={grade.value}>
                {grade.label}
              </option>
            ))}
          </select>
        </div>

        {/* Error Display */}
        {generateMutation.isError && (
          <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <svg className="w-5 h-5 text-danger-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-danger-800 mb-1">Failed to Generate Plan</h4>
                <p className="text-sm text-danger-700">
                  {generateMutation.error instanceof Error 
                    ? generateMutation.error.message 
                    : 'An error occurred while generating the plan. Please try again.'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {generateMutation.isPending && (
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600" />
              <div>
                <p className="text-sm font-medium text-primary-900">Generating plan...</p>
                <p className="text-xs text-primary-700 mt-1">This may take 30-60 seconds</p>
              </div>
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          <Button
            type="button"
            variant="ghost"
            onClick={onClose}
            disabled={generateMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="bg-primary-600 hover:bg-primary-700"
            disabled={!canSubmit}
          >
            {generateMutation.isPending ? 'Generating...' : 'Generate Plan'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
