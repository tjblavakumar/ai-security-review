"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Search, Trash2 } from "lucide-react";
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

export default function MySubmissionsPage() {
  const [email, setEmail] = useState("");
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!email) {
      toast.error("Please enter your email");
      return;
    }
    try {
      const res = await api.get<Submission[]>(
        `/submissions?email=${encodeURIComponent(email)}`
      );
      setSubmissions(res.data);
      setSearched(true);
    } catch {
      toast.error("Failed to fetch submissions");
    }
  };

  const handleDelete = async (submission: Submission) => {
    // Only allow deletion of draft and returned submissions
    if (submission.status !== "draft" && submission.status !== "returned") {
      toast.error(`Cannot delete ${submission.status} submissions. Only draft and returned submissions can be deleted.`);
      return;
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete "${submission.project_name}"?\n\nThis action cannot be undone. All responses and attachments will be permanently deleted.`
    );

    if (!confirmed) return;

    try {
      await api.delete(`/submissions/${submission.id}`);
      toast.success("Submission deleted successfully");
      // Remove from list
      setSubmissions(submissions.filter((s) => s.id !== submission.id));
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to delete submission";
      toast.error(errorMessage);
    }
  };

  const getActionButton = (s: Submission) => {
    const canDelete = s.status === "draft" || s.status === "returned";
    
    return (
      <div className="flex items-center gap-2 justify-end">
        {s.status === "draft" && (
          <Link href={`/submit/${s.id}/question/${s.current_step}`}>
            <Button size="sm">Continue</Button>
          </Link>
        )}
        {s.status === "returned" && (
          <Link href={`/submit/${s.id}/question/1`}>
            <Button size="sm" variant="outline">Revise</Button>
          </Link>
        )}
        {s.status !== "draft" && s.status !== "returned" && (
          <Link href={`/submit/${s.id}/summary`}>
            <Button size="sm" variant="ghost">View</Button>
          </Link>
        )}
        {canDelete && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(s)}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            title="Delete submission"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">My Submissions</h1>

      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-end">
            <div className="flex-1 space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email to find submissions"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {searched && submissions.length === 0 && (
        <p className="text-center text-gray-500 py-8">
          No submissions found for this email.
        </p>
      )}

      {submissions.length > 0 && (
        <div className="rounded-lg border bg-white">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left p-3 text-sm font-medium text-gray-500">Project Name</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-left p-3 text-sm font-medium text-gray-500">Last Updated</th>
                <th className="text-right p-3 text-sm font-medium text-gray-500">Action</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((s) => (
                <tr key={s.id} className="border-b last:border-0">
                  <td className="p-3 font-medium">{s.project_name}</td>
                  <td className="p-3">
                    <Badge className={statusColors[s.status]}>
                      {statusLabels[s.status]}
                    </Badge>
                  </td>
                  <td className="p-3 text-sm text-gray-500">
                    {new Date(s.updated_at).toLocaleDateString()}
                  </td>
                  <td className="p-3 text-right">{getActionButton(s)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
