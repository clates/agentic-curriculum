import axios from 'axios';

// Calls go through the app's own /api route, which proxies them to the backend (no CORS, one port)
export const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// An expired or missing session (401 from anywhere except the sign-in call itself) sends the
// person back to the login screen, then on to the page they were on.
apiClient.interceptors.response.use(undefined, (error) => {
  const url: string = error?.config?.url ?? '';
  if (
    error?.response?.status === 401 &&
    typeof window !== 'undefined' &&
    !url.startsWith('/auth/login') &&
    window.location.pathname !== '/login'
  ) {
    const here = window.location.pathname + window.location.search;
    window.location.assign(`/login?next=${encodeURIComponent(here)}`);
  }
  return Promise.reject(error);
});

const get = async <T>(url: string, params?: object): Promise<T> =>
  (await apiClient.get<T>(url, { params })).data;

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
  interests?: string[];
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
  has_feedback: boolean;
  feedback_completed_at: string | null;
}

export interface FeedbackData {
  mastery_feedback: Record<string, string> | null;
  quantity_feedback: number | null;
  completed_at: string | null;
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
  getOptions: () => get<SystemOptions>('/system/options'),
};

// Students API
export const studentsApi = {
  listStudents: () => get<StudentProfile[]>('/students'),

  createStudent: async (payload: {
    metadata: StudentMetadata;
    plan_rules?: Record<string, unknown>;
  }): Promise<StudentProfile> => {
    const { data } = await apiClient.post('/students', payload);
    return data;
  },

  updateStudent: async (
    studentId: string,
    payload: {
      metadata?: Partial<StudentMetadata>;
      plan_rules?: Record<string, unknown>;
    }
  ): Promise<StudentProfile> => {
    const { data } = await apiClient.put(`/student/${studentId}`, payload);
    return data;
  },

  deleteStudent: async (studentId: string): Promise<void> => {
    await apiClient.delete(`/student/${studentId}`);
  },

  getStudent: (studentId: string) => get<StudentProfile>(`/student/${studentId}`),

  /** Per subject, counts of solid, shaky and still-to-come skills. */
  getCoverage: (studentId: string) =>
    get<{ subject: string; solid: number; shaky: number; to_come: number }[]>(
      `/students/${studentId}/coverage`
    ),

  listWeeklyPackets: (
    studentId: string,
    params?: { week_of?: string; page?: number; page_size?: number }
  ) => get<PaginatedResponse<WeeklyPacketSummary>>(`/students/${studentId}/weekly-packets`, params),
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

// Weekly packet detail types
export interface DailyLessonPlan {
  objective: string;
  materials_needed: string[];
  procedure: string[];
}

export interface DailyPlan {
  day: string;
  focus: string;
  lesson_plan: DailyLessonPlan;
  standard?: { standard_id: string; description: string };
  resource_errors?: string[];
}

export interface WeeklyPacketDetail {
  packet_id: string;
  student_id: string;
  week_of: string;
  subject: string;
  grade_level: number;
  status: string;
  weekly_overview?: string;
  daily_plan: DailyPlan[];
}

export interface WorksheetArtifact {
  artifact_id: string;
  format: string;
  download_url: string;
}

export interface WorksheetItem {
  resource_kind: string;
  day_label: string;
  artifacts: WorksheetArtifact[];
}

export interface PacketWorksheetsResponse {
  items: WorksheetItem[];
}

const packetUrl = (studentId: string, packetId: string) =>
  `/students/${studentId}/weekly-packets/${packetId}`;

// Plans API
export const plansApi = {
  getPacketDetail: (studentId: string, packetId: string) =>
    get<WeeklyPacketDetail>(packetUrl(studentId, packetId)),

  getPacketWorksheets: (studentId: string, packetId: string) =>
    get<PacketWorksheetsResponse>(`${packetUrl(studentId, packetId)}/worksheets`),

  getFeedback: (studentId: string, packetId: string) =>
    get<FeedbackData>(`${packetUrl(studentId, packetId)}/feedback`).catch(() => null),

  submitFeedback: async (
    studentId: string,
    packetId: string,
    feedback: {
      mastery_feedback?: Record<string, string>;
      quantity_feedback?: number;
    }
  ): Promise<void> => {
    await apiClient.post(`${packetUrl(studentId, packetId)}/feedback`, feedback);
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

// Curriculum Graph API
export interface GraphNode {
  id: string;
  data: {
    label: string;
    fullStatement: string;
    state: 'mastered' | 'ready' | 'locked';
    educationLevel: string;
  };
  type: string;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
}

export interface CurriculumGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export const curriculumApi = {
  getProgressMap: (studentId: string, subject: string, prune: boolean = true) =>
    get<CurriculumGraph>(`/students/${studentId}/progress-map/${subject}`, { prune }),
};
