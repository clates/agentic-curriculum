'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Input, Modal } from '@/components/ui';
import { Navigation } from '@/components/Navigation';
import { studentsApi, parseMetadata } from '@/lib/api';
import { useStudents } from '@/lib/hooks';

// Validation schema
const studentSchema = z.object({
  student_id: z.string().min(1, 'Student ID is required').regex(/^[a-z0-9_]+$/, 'Use lowercase letters, numbers, and underscores only'),
  name: z.string().min(1, 'Name is required'),
  birthday: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Format: YYYY-MM-DD'),
  avatar_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  notes: z.string().optional(),
});

type StudentFormData = z.infer<typeof studentSchema>;

export default function StudentsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState<string | null>(null);
  const [deletingStudent, setDeletingStudent] = useState<string | null>(null);

  const { data: students, isLoading } = useStudents();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<StudentFormData>({
    resolver: zodResolver(studentSchema),
  });

  // Update form when editing
  useEffect(() => {
    if (editingStudent && students) {
      const student = students.find((s) => s.student_id === editingStudent);
      if (student) {
        const metadata = parseMetadata(student.metadata_blob);
        if (metadata) {
          setValue('student_id', student.student_id);
          setValue('name', metadata.name);
          setValue('birthday', metadata.birthday);
          setValue('avatar_url', metadata.avatar_url || '');
          setValue('notes', metadata.notes || '');
        }
        setIsModalOpen(true);
      }
    }
  }, [editingStudent, students, setValue]);

  // Create student mutation
  const createMutation = useMutation({
    mutationFn: (data: StudentFormData) =>
      studentsApi.createStudent({
        student_id: data.student_id,
        metadata: {
          name: data.name,
          birthday: data.birthday,
          avatar_url: data.avatar_url || undefined,
          notes: data.notes || undefined,
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      setIsModalOpen(false);
      setEditingStudent(null);
      reset();
    },
  });

  // Update student mutation
  const updateMutation = useMutation({
    mutationFn: (data: StudentFormData) =>
      studentsApi.updateStudent(data.student_id, {
        metadata: {
          name: data.name,
          birthday: data.birthday,
          avatar_url: data.avatar_url || undefined,
          notes: data.notes || undefined,
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      setIsModalOpen(false);
      setEditingStudent(null);
      reset();
    },
  });

  // Delete student mutation
  const deleteMutation = useMutation({
    mutationFn: (studentId: string) => studentsApi.deleteStudent(studentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] });
      setDeletingStudent(null);
    },
  });

  const onSubmit = (data: StudentFormData) => {
    if (editingStudent) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = (studentId: string) => {
    deleteMutation.mutate(studentId);
  };

  const handleAddNew = () => {
    setEditingStudent(null);
    reset();
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingStudent(null);
    reset();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        {/* Navigation Bar */}
        <Navigation />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-neutral-200 rounded w-48 mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-neutral-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const isEditing = !!editingStudent;
  const activeMutation = isEditing ? updateMutation : createMutation;

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Bar */}
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-semibold text-foreground">Manage Students</h1>
          <Button onClick={handleAddNew}>Add Student</Button>
        </div>

        {/* Students List */}
        {!students || students.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <svg className="w-16 h-16 text-neutral-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <h3 className="text-lg font-medium text-foreground mb-2">No Students Yet</h3>
            <p className="text-neutral-600 mb-4">Get started by adding your first student</p>
            <Button onClick={handleAddNew}>Add Student</Button>
          </div>
        ) : (
          <div className="space-y-4">
            {students.map((student) => {
              const metadata = parseMetadata(student.metadata_blob);
              return (
                <div key={student.student_id} className="bg-white rounded-lg shadow-sm p-6 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {metadata?.avatar_url ? (
                      <img src={metadata.avatar_url} alt={metadata.name} className="w-16 h-16 rounded-full" />
                    ) : (
                      <div className="w-16 h-16 bg-primary-200 rounded-full"></div>
                    )}
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">{metadata?.name || 'Unknown'}</h3>
                      <p className="text-sm text-neutral-600">ID: {student.student_id}</p>
                      <p className="text-sm text-neutral-500">Birthday: {metadata?.birthday || 'Not set'}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="secondary" size="sm" onClick={() => setEditingStudent(student.student_id)}>
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-danger-600 border-danger-600 hover:bg-danger-50"
                      onClick={() => setDeletingStudent(student.student_id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Create/Edit Student Modal */}
        <Modal 
          isOpen={isModalOpen} 
          onClose={handleCloseModal} 
          title={isEditing ? 'Edit Student' : 'Add New Student'}
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Student ID"
              {...register('student_id')}
              error={errors.student_id?.message}
              helperText="Use lowercase letters, numbers, and underscores (e.g., student_01)"
              disabled={isEditing}
              className={isEditing ? 'bg-neutral-100 cursor-not-allowed' : ''}
            />

            <Input
              label="Full Name"
              {...register('name')}
              error={errors.name?.message}
            />

            <Input
              label="Birthday"
              type="date"
              {...register('birthday')}
              error={errors.birthday?.message}
              helperText="Format: YYYY-MM-DD"
            />

            <Input
              label="Avatar URL (optional)"
              {...register('avatar_url')}
              error={errors.avatar_url?.message}
            />

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Notes (optional)
              </label>
              <textarea
                {...register('notes')}
                className="w-full px-4 py-3 bg-white border-2 border-neutral-300 rounded-sm text-base text-foreground focus:outline-none focus:border-primary-500 focus:ring-3 focus:ring-primary-100"
                rows={3}
                placeholder="Any special notes about this student..."
              />
            </div>

            {activeMutation.error && (
              <div className="bg-danger-50 border border-danger-200 rounded p-3 text-sm text-danger-700">
                {activeMutation.error instanceof Error ? activeMutation.error.message : `Failed to ${isEditing ? 'update' : 'create'} student`}
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4">
              <Button type="button" variant="ghost" onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting || activeMutation.isPending}>
                {activeMutation.isPending ? (isEditing ? 'Updating...' : 'Creating...') : (isEditing ? 'Update Student' : 'Create Student')}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Delete Confirmation Modal */}
        {deletingStudent && (
          <Modal isOpen={true} onClose={() => setDeletingStudent(null)} title="Delete Student">
            <div>
              <p className="text-neutral-700 mb-6">
                Are you sure you want to delete this student? This action cannot be undone and will remove all associated lesson plans and worksheets.
              </p>
              {deleteMutation.error && (
                <div className="bg-danger-50 border border-danger-200 rounded p-3 text-sm text-danger-700 mb-4">
                  {deleteMutation.error instanceof Error ? deleteMutation.error.message : 'Failed to delete student'}
                </div>
              )}
              <div className="flex justify-end space-x-3">
                <Button variant="ghost" onClick={() => setDeletingStudent(null)}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  className="bg-danger-600 hover:bg-danger-700"
                  onClick={() => handleDelete(deletingStudent)}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Delete Student'}
                </Button>
              </div>
            </div>
          </Modal>
        )}
      </div>
    </div>
  );
}
