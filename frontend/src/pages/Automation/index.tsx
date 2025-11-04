import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";
import { formatDate } from "@/utils/formatters";
import { useToast } from "@/context/ToastContext";

interface JobRecord {
  name: string;
  status: string;
  next_run_at?: string;
  last_run_at?: string;
  last_duration_ms?: number;
}

interface JobsResponse {
  jobs: JobRecord[];
}

interface JobHistoryRecord {
  id: string;
  job_name: string;
  status: string;
  finished_at?: string;
  duration_ms?: number;
}

interface JobHistoryResponse {
  history: JobHistoryRecord[];
}

export const AutomationPage = () => {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const [selectedJob, setSelectedJob] = useState<string | null>(null);

  const { data: jobs } = useQuery<JobsResponse>({
    queryKey: ["jobs", "list"],
    queryFn: async () => apiFetch<JobsResponse>(API_ROUTES.jobs.list)
  });

  const { data: history } = useQuery<JobHistoryResponse>({
    queryKey: ["jobs", "history", selectedJob],
    enabled: Boolean(selectedJob),
    queryFn: async () =>
      apiFetch<JobHistoryResponse>(
        `${API_ROUTES.jobs.history}?job_name=${encodeURIComponent(selectedJob ?? "")}`
      )
  });

  const toggleJob = useMutation({
    mutationFn: (payload: { job_name: string; enabled: boolean }) =>
      apiFetch(API_ROUTES.jobs.update, {
        method: "POST",
        json: payload
      }),
    onSuccess: () => {
      addToast({ title: "Job updated", variant: "success" });
      queryClient.invalidateQueries({ queryKey: ["jobs", "list"] });
    }
  });

  const runNow = useMutation({
    mutationFn: (job_name: string) =>
      apiFetch(API_ROUTES.jobs.update, {
        method: "POST",
        json: { job_name, run_now: true }
      }),
    onSuccess: () => {
      addToast({ title: "Job triggered", variant: "success" });
    }
  });

  return (
    <div className="space-y-6">
      <Card title="Scheduler">
        <div className="overflow-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="text-white/60">
                <th className="py-2">Job</th>
                <th className="py-2">Next run</th>
                <th className="py-2">Last run</th>
                <th className="py-2">Duration</th>
                <th className="py-2">Status</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs?.jobs.map((job) => (
                <tr className="border-t border-white/10" key={job.name}>
                  <td className="py-3 font-medium text-white">{job.name}</td>
                  <td className="py-3 text-white/60">{formatDate(job.next_run_at)}</td>
                  <td className="py-3 text-white/60">{formatDate(job.last_run_at)}</td>
                  <td className="py-3 text-white/60">
                    {job.last_duration_ms ? `${Math.round(job.last_duration_ms)} ms` : "—"}
                  </td>
                  <td className="py-3 text-white/60">{job.status}</td>
                  <td className="py-3">
                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={() => runNow.mutate(job.name)}
                        variant="secondary"
                      >
                        Run now
                      </Button>
                      <Button
                        onClick={() =>
                          toggleJob.mutate({
                            job_name: job.name,
                            enabled: job.status === "disabled"
                          })
                        }
                        variant="ghost"
                      >
                        {job.status === "disabled" ? "Enable" : "Disable"}
                      </Button>
                      <Button onClick={() => setSelectedJob(job.name)} variant="ghost">
                        View history
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
              {jobs?.jobs.length === 0 && (
                <tr>
                  <td className="py-6 text-center text-white/50" colSpan={6}>
                    No jobs configured.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {selectedJob ? (
        <Card title={`History • ${selectedJob}`}>
          <div className="space-y-3">
            {history?.history.map((item) => (
              <div className="rounded-xl border border-white/10 p-3 text-sm" key={item.id}>
                <p className="font-medium text-white">{item.status}</p>
                <p className="text-xs text-white/60">
                  Finished {formatDate(item.finished_at)} • {item.duration_ms ?? "—"} ms
                </p>
              </div>
            ))}
            {history?.history.length === 0 && (
              <p className="text-sm text-white/60">No runs recorded yet.</p>
            )}
          </div>
        </Card>
      ) : null}
    </div>
  );
};

export default AutomationPage;
