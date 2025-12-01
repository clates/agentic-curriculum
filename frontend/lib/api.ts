import axios from 'axios';

// Use Next.js API routes as proxy to backend
// This eliminates CORS issues and allows single-port deployment
const API_BASE_URL = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Student types
export interface StudentProfile {
  student_id: string;
  progress_blob: string | null;
  plan_rules_blob: string | null;
  metadata_blob: string | null;
}

export interface StudentMetadata {
  name: string;
  birthday: string;
  avatar_url?: string;
  notes?: string;
}

export interface ProgressBlob {
  mastered_standards: string[];
  developing_standards: string[];
}

// Weekly packet types
export interface WeeklyPacketSummary {
  packet_id: string;
  student_id: string;
  week_of: string;
  subject: string;
  grade_level: number;
  status: string;
  worksheet_counts: Record<string, number>;
  artifact_count: number;
  resource_days: number;
  daily_count: number;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    page_size: number;
    has_more: boolean;
    next_page: number | null;
  };
}

// System configuration API
export interface SystemOptions {
  subjects: string[];
  grades: { value: number; label: string }[];
  worksheet_types: string[];
  statuses: string[];
}

export const systemApi = {
  getOptions: async (): Promise<SystemOptions> => {
    const { data } = await apiClient.get('/system/options');
    return data;
  },
};

// Students API
export const studentsApi = {
  listStudents: async (): Promise<StudentProfile[]> => {
    const { data } = await apiClient.get('/students');
    return data;
  },

  getStudent: async (studentId: string): Promise<StudentProfile> => {
    const { data } = await apiClient.get(`/student/${studentId}`);
    return data;
  },

  createStudent: async (payload: {
    student_id: string;
    metadata: StudentMetadata;
    plan_rules?: Record<string, any>;
  }): Promise<StudentProfile> => {
    const { data } = await apiClient.post('/students', payload);
    return data;
  },

  updateStudent: async (
    studentId: string,
    payload: {
      metadata?: Partial<StudentMetadata>;
      plan_rules?: Record<string, any>;
    }
  ): Promise<StudentProfile> => {
    const { data } = await apiClient.put(`/student/${studentId}`, payload);
    return data;
  },

  deleteStudent: async (studentId: string): Promise<void> => {
    await apiClient.delete(`/student/${studentId}`);
  },

  listWeeklyPackets: async (
    studentId: string,
    params?: { week_of?: string; page?: number; page_size?: number }
  ): Promise<PaginatedResponse<WeeklyPacketSummary>> => {
    const { data } = await apiClient.get(`/students/${studentId}/weekly-packets`, { params });
    return data;
  },
};

// Helper functions to parse JSON blobs
export const parseMetadata = (metadataBlob: string | null): StudentMetadata | null => {
  if (!metadataBlob) return null;
  try {
    return JSON.parse(metadataBlob);
  } catch {
    return null;
  }
};

export const parseProgress = (progressBlob: string | null): ProgressBlob => {
  if (!progressBlob) {
    return { mastered_standards: [], developing_standards: [] };
  }
  try {
    return JSON.parse(progressBlob);
  } catch {
    return { mastered_standards: [], developing_standards: [] };
  }
};

// Weekly packet detail types
export interface LessonPlan {
  title: string;
  pdf_path: string;
  [key: string]: any;
}

export interface Worksheet {
  title: string;
  type: string;
  pdf_path: string;
  [key: string]: any;
}

export interface WeeklyPacketDetail {
  packet_id: string;
  student_id: string;
  week_of: string;
  subject: string;
  grade_level: number;
  status: string;
  lesson_plan?: LessonPlan;
  worksheets?: Worksheet[];
  [key: string]: any;
}

// Plans API
export const plansApi = {
  getPacketDetail: async (studentId: string, packetId: string): Promise<WeeklyPacketDetail> => {
    const { data } = await apiClient.get(`/students/${studentId}/weekly-packets/${packetId}`);
    return data;
  },

  getPacketWorksheets: async (studentId: string, packetId: string): Promise<any> => {
    const { data } = await apiClient.get(
      `/students/${studentId}/weekly-packets/${packetId}/worksheets`
    );
    return data;
  },

  submitFeedback: async (
    studentId: string,
    packetId: string,
    feedback: {
      mastery_feedback?: Record<string, string>;
      quantity_feedback?: string;
    }
  ): Promise<void> => {
    await apiClient.post(`/students/${studentId}/weekly-packets/${packetId}/feedback`, feedback);
  },

  downloadArtifact: (path: string): string => {
    // This is now just for legacy - we should use artifact IDs from worksheets endpoint
    return `${API_BASE_URL}/artifact?path=${encodeURIComponent(path)}`;
  },

  generateWeeklyPlan: async (payload: {
    student_id: string;
    grade_level: number;
    subject: string;
  }): Promise<WeeklyPacketDetail> => {
    const { data } = await apiClient.post('/generate_weekly_plan', payload);
    return data;
  },
};
