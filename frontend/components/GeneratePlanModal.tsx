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
  }, [isOpen, preSelectedStudent, generateMutation.reset]);

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

  const canSubmit = selectedStudentId && subject && !generateMutation.isPending;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Generate Weekly Plan">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* ... (student selector) ... */}

        {/* ... (subject/grade selectors) ... */}

        {/* Error Display */}
        {generateMutation.isError && (
          <div className="bg-danger-50 border-danger-200 rounded-lg border p-4">
            <div className="flex items-start space-x-3">
              <svg
                className="text-danger-500 mt-0.5 h-5 w-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="flex-1">
                <h4 className="text-danger-800 mb-1 text-sm font-semibold">
                  Failed to Generate Plan
                </h4>
                <p className="text-danger-700 text-sm">
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
          <div className="bg-primary-50 border-primary-200 rounded-lg border p-4">
            <div className="flex items-center space-x-3">
              <div className="border-primary-600 h-5 w-5 animate-spin rounded-full border-b-2" />
              <div>
                <p className="text-primary-900 text-sm font-medium">Generating plan...</p>
                <p className="text-primary-700 mt-1 text-xs">This may take 30-60 seconds</p>
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
