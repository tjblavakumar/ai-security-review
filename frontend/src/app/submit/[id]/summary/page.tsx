"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Send, Edit2, Check } from "lucide-react";
import RiskScoreDisplay from "@/components/risk/RiskScoreDisplay";
import type { Question, SubmissionDetail } from "@/lib/types";

export default function SummaryPage() {
  const params = useParams();
  const router = useRouter();
  const submissionId = params.id as string;

  const [questions, setQuestions] = useState<Question[]>([]);
  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<Question[]>("/questions/preview"),
      api.get<SubmissionDetail>(`/submissions/${submissionId}`),
    ]).then(([qRes, sRes]) => {
      setQuestions(qRes.data);
      setSubmission(sRes.data);
    });
  }, [submissionId]);

  const responseMap = new Map(
    (submission?.responses || []).map((r) => [r.question_id, r.response_value])
  );

  const grouped = questions.reduce<Record<string, Question[]>>((acc, q) => {
    const cat = q.category?.name || "Uncategorized";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(q);
    return acc;
  }, {});

  const startEdit = (questionId: number) => {
    setEditingId(questionId);
    setEditValue(responseMap.get(questionId) || "");
  };

  const saveEdit = async (questionId: number) => {
    try {
      await api.post(`/submissions/${submissionId}/responses`, {
        responses: [{ question_id: questionId, response_value: editValue }],
      });
      if (submission) {
        const updated = { ...submission };
        const idx = updated.responses.findIndex((r) => r.question_id === questionId);
        if (idx >= 0) {
          updated.responses[idx] = { ...updated.responses[idx], response_value: editValue };
        }
        setSubmission(updated);
      }
      setEditingId(null);
      toast.success("Response updated");
    } catch {
      toast.error("Failed to update response");
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await api.post(`/submissions/${submissionId}/submit`);
      router.push(`/submit/${submissionId}/confirmation`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to submit");
    } finally {
      setSubmitting(false);
    }
  };

  const formatValue = (val: string | null | undefined): string => {
    if (!val) return "— Not answered —";
    try {
      const parsed = JSON.parse(val);
      
      // Handle new format with selection/selections and comments
      if (parsed && typeof parsed === 'object') {
        // Multi-select format: {selections: [...], comments: "..."}
        if (parsed.selections && Array.isArray(parsed.selections)) {
          const answer = parsed.selections.join(", ");
          const comments = parsed.comments ? ` (${parsed.comments})` : "";
          return answer + comments;
        }
        
        // Single select / yes-no format: {selection: "...", comments: "..."}
        if (parsed.selection) {
          const answer = parsed.selection;
          const comments = parsed.comments ? ` (${parsed.comments})` : "";
          return answer + comments;
        }
      }
      
      // Handle old array format (legacy multi-select)
      if (Array.isArray(parsed)) {
        return parsed.join(", ");
      }
    } catch {
      /* not JSON */
    }
    return val;
  };

  if (!submission) {
    return <div className="text-center py-12 text-gray-500">Loading summary...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Risk Score Display - Always visible at top */}
      <RiskScoreDisplay submissionId={submissionId} autoRefresh={false} />
      
      <div>
        <h1 className="text-2xl font-bold">Review Your Responses</h1>
        <p className="text-gray-500">
          Review all your answers below. Click the edit icon to make changes
          before submitting.
        </p>
      </div>

      {Object.entries(grouped).map(([category, qs]) => (
        <Card key={category}>
          <CardHeader>
            <CardTitle className="text-lg">
              <Badge variant="secondary" className="mr-2">{category}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {qs.map((q) => {
              const val = responseMap.get(q.id);
              const isEditing = editingId === q.id;
              return (
                <div key={q.id} className="border-b pb-3 last:border-0">
                  <div className="flex items-start justify-between">
                    <p className="font-medium text-sm">{q.question_text}</p>
                    {!isEditing && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => startEdit(q.id)}
                      >
                        <Edit2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                  {isEditing ? (
                    <div className="mt-2 space-y-2">
                      <Textarea
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        rows={2}
                      />
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => saveEdit(q.id)}>
                          <Check className="h-3 w-3 mr-1" /> Save
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setEditingId(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-600 mt-1">
                      {formatValue(val)}
                    </p>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      ))}

      <Button
        className="w-full"
        size="lg"
        onClick={handleSubmit}
        disabled={submitting}
      >
        <Send className="h-4 w-4 mr-2" />
        {submitting ? "Submitting..." : "Submit for Review"}
      </Button>
    </div>
  );
}
