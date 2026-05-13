"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { toast } from "sonner";
import type { Submission, ProjectType } from "@/lib/types";

export default function NewSubmissionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    project_name: "",
    project_description: "",
    submitter_name: "",
    submitter_email: "",
    team_department: "",
    target_go_live_date: "",
    project_type: "new" as ProjectType,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.project_name || !form.submitter_name || !form.submitter_email) {
      toast.error("Please fill in all required fields.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post<Submission>("/submissions", form);
      toast.success("Submission created!");
      router.push(`/submit/${res.data.id}/question/1`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to create submission");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>New Security Review Submission</CardTitle>
          <CardDescription>
            Provide basic project information to begin the questionnaire.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="project_name">Project Name *</Label>
              <Input
                id="project_name"
                value={form.project_name}
                onChange={(e) => setForm({ ...form, project_name: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="project_description">Project Description</Label>
              <Textarea
                id="project_description"
                value={form.project_description}
                onChange={(e) => setForm({ ...form, project_description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="submitter_name">Your Name *</Label>
                <Input
                  id="submitter_name"
                  value={form.submitter_name}
                  onChange={(e) => setForm({ ...form, submitter_name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="submitter_email">Your Email *</Label>
                <Input
                  id="submitter_email"
                  type="email"
                  value={form.submitter_email}
                  onChange={(e) => setForm({ ...form, submitter_email: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="team_department">Team / Department</Label>
                <Input
                  id="team_department"
                  value={form.team_department}
                  onChange={(e) => setForm({ ...form, team_department: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="target_go_live_date">Target Go-Live Date</Label>
                <Input
                  id="target_go_live_date"
                  type="date"
                  value={form.target_go_live_date}
                  onChange={(e) => setForm({ ...form, target_go_live_date: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Project Type *</Label>
              <Select
                value={form.project_type}
                onValueChange={(v) => setForm({ ...form, project_type: v as ProjectType })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">New Project</SelectItem>
                  <SelectItem value="modification">Modification</SelectItem>
                  <SelectItem value="third-party">Third-Party</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating..." : "Start Questionnaire"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
