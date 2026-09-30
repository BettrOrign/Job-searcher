export interface JobOffer {
  id: string;
  title: string;
  description: string;
  company: string;
  location: string;
  salary_from: number | null;
  salary_to: number | null;
  currency: string;
  experience_required: string | null;
  employment_type: string | null;
  schedule_type: string | null;
  key_skills: string[];
  published_at: string | null;
  alternate_url: string;
  source: string;
}

export interface SearchQuery {
  q: string;
  location: string | null;
  experience: string | null;
  salary_min: number | null;
  salary_max: number | null;
  employment_type: string | null;
  schedule_type: string | null;
  skills: string[];
  page: number;
  size: number;
}

export interface SearchResult {
  total: number;
  page: number;
  size: number;
  results: JobOffer[];
  took_ms: number;
  cached: boolean;
}

export type ExperienceLevel =
  | "noExperience"
  | "between1And3"
  | "between3And6"
  | "moreThan6";

export type EmploymentType =
  | "full"
  | "part"
  | "temporary"
  | "proj"
  | "volunteer"
  | "probation";

export type ScheduleType =
  | "fullDay"
  | "shift"
  | "flexible"
  | "remote"
  | "travel"
  | "external";