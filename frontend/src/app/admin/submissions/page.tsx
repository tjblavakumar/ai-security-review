"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import type { Submission, SubmissionStatus } from "@/lib/types";

const statusColors: Record<SubmissionStatus, string> = {
  draft: "bg-gray-100 text-gray-700",
  submitted: "bg-blue-100 text-blue-700",
  in_review: "bg-yellow-100 text-yellow-700",
  returned: "bg-orange-100 text-orange-700",
  approved: "bg-green-100 text-green-700",
};

const statusLabels: Record<SubmissionStatus, string> = {
  draft: "Draft",
  submitted: "Submitted",
  in_review: "In Review",
  returned: "Returned",
  approved: "Approved",
};

export default function ReviewSubmissionsPage() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);

  useEffect(() => {
    api.get<Submission[]>("/reviews/queue").then((res) =>
      setSubmissions(res.data)
    );
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Review Submissions</h1>

      {submissions.length === 0 ? (
        <p className="text-center text-gray-500 py-8">
          No submissions pending review.
        </p>
      ) : (
        <div className="rounded-lg border bg-white">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left p-3 text-sm font-medium text-gray-500">
                  Project Name
                </th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">
                  Submitter
                </th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">
                  Submitted Date
                </th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">
                  Status
                </th>
                <th className="text-right p-3 text-sm font-medium text-gray-500">
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((s) => (
                <tr key={s.id} className="border-b last:border-0">
                  <td className="p-3 font-medium">{s.project_name}</td>
                  <td className="p-3 text-sm">
                    {s.submitter_name}
                    <br />
                    <span className="text-gray-400">{s.submitter_email}</span>
                  </td>
                  <td className="p-3 text-sm text-gray-500">
                    {s.submitted_at
                      ? new Date(s.submitted_at).toLocaleDateString()
                      : "—"}
                  </td>
                  <td className="p-3">
                    <Badge className={statusColors[s.status]}>
                      {statusLabels[s.status]}
                    </Badge>
                  </td>
                  <td className="p-3 text-right">
                    <Link href={`/admin/submissions/${s.id}`}>
                      <Button size="sm">Review</Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
