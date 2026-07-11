export type ProjectInfo = {
  id: string;
  name: string;
  api_key_prefix: string;
  created_at: string;
};

export type RunSummary = {
  id: string;
  client_run_id: string | null;
  overall_passed: boolean;
  exit_reason: string;
  total_cases: number;
  failed_cases: number;
  judge_calls: number;
  faithfulness_mean: number | null;
  answer_relevancy_mean: number | null;
  prompt_injection_mean: number | null;
  git_sha: string | null;
  git_ref: string | null;
  repo: string | null;
  created_at: string;
};

export type RunDetail = RunSummary & {
  schema_version: string;
  client_version: string | null;
  payload: {
    aggregates?: Record<
      string,
      {
        mean?: number;
        threshold?: number;
        passed?: boolean;
        n_scored?: number;
      }
    >;
    top_failures?: Array<{
      case_id: string;
      metric: string;
      score: number;
      question?: string;
      answer?: string;
      reason?: string | null;
    }>;
    metadata?: Record<string, unknown>;
    [key: string]: unknown;
  };
};
