"use client";

import { useState, useRef } from "react";
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
import { Upload, FileText, X } from "lucide-react";
import type { Submission, ProjectType } from "@/lib/types";

export default function NewSubmissionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [form, setForm] = useState({
    project_name: "",
    project_description: "",
    submitter_name: "",
    submitter_email: "",
    team_department: "",
    target_go_live_date: "",
    project_type: "new" as ProjectType,
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'text/plain'];
      if (!allowedTypes.includes(file.type)) {
        toast.error('Only PDF and TXT files are allowed');
        return;
      }
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
        return;
      }
      setUploadedFile(file);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.project_name || !form.submitter_name || !form.submitter_email) {
      toast.error("Please fill in all required fields.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post<Submission>("/submissions", form);
      const submissionId = res.data.id;
      
      // Upload document if provided
      if (uploadedFile) {
        const formData = new FormData();
        formData.append('file', uploadedFile);
        try {
          console.log('Uploading document:', uploadedFile.name, 'for submission:', submissionId);
          const uploadRes = await api.post(`/submissions/${submissionId}/upload-document`, formData);
          console.log('Upload response:', uploadRes);
          toast.success("Submission created with document!");
        } catch (uploadErr: any) {
          console.error('Document upload error:', uploadErr);
          const errorMsg = uploadErr?.response?.data?.detail || uploadErr?.message || 'Unknown error';
          toast.error(`Document upload failed: ${errorMsg}`);
        }
      } else {
        toast.success("Submission created!");
      }
      
      router.push(`/submit/${submissionId}/question/1`);
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

            <div className="space-y-2">
              <Label htmlFor="document_upload">Upload Project Document (Optional)</Label>
              <div className="text-sm text-gray-500 mb-2">
                Upload a PDF or TXT file with project information. The AI will use this to help auto-populate responses.
              </div>
              <input
                ref={fileInputRef}
                id="document_upload"
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                className="hidden"
              />
              {!uploadedFile ? (
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Choose File (PDF or TXT)
                </Button>
              ) : (
                <div className="flex items-center justify-between p-3 border rounded-md bg-blue-50">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <span className="text-sm font-medium">{uploadedFile.name}</span>
                    <span className="text-xs text-gray-500">
                      ({(uploadedFile.size / 1024).toFixed(1)} KB)
                    </span>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleRemoveFile}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
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
