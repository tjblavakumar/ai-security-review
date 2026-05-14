"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { CheckCircle, RotateCcw, MessageSquare } from "lucide-react";
import RiskScoreDisplay from "@/components/risk/RiskScoreDisplay";
import type { Question, SubmissionDetail } from "@/lib/types";

export default function ReviewDetailPage() {
  const params = useParams();
  const router = useRouter();
  const submissionId = params.id as string;

  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reviewerName, setReviewerName] = useState("");
  const [reviewerEmail, setReviewerEmail] = useState("");
  const [overallComments, setOverallComments] = useState("");
  const [comments, setComments] = useState<Record<number, string>>({});
  const [expandedComments, setExpandedComments] = useState<Set<number>>(new Set());
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<SubmissionDetail>(`/reviews/submission/${submissionId}`),
      api.get<Question[]>("/questions/preview"),
    ]).then(([sRes, qRes]) => {
      setSubmission(sRes.data);
      setQuestions(qRes.data);
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

  const toggleComment = (qId: number) => {
    const next = new Set(expandedComments);
    if (next.has(qId)) next.delete(qId);
    else next.add(qId);
    setExpandedComments(next);
  };

  const handleApprove = async () => {
    if (!reviewerName || !reviewerEmail) {
      toast.error("Please enter reviewer name and email");
      return;
    }
    setSubmitting(true);
    try {
      await api.post(`/reviews/submission/${submissionId}/approve`, {
        reviewer_name: reviewerName,
        reviewer_email: reviewerEmail,
        overall_comments: overallComments || null,
      });
      toast.success("Submission approved!");
      router.push("/admin/submissions");
    } catch {
      toast.error("Failed to approve");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReturn = async () => {
    if (!reviewerName || !reviewerEmail) {
      toast.error("Please enter reviewer name and email");
      return;
    }
    setSubmitting(true);
    try {
      const commentList = Object.entries(comments)
        .filter(([, v]) => v.trim())
        .map(([qId, text]) => ({
          question_id: parseInt(qId),
          comment_text: text,
        }));
      await api.post(`/reviews/submission/${submissionId}/return`, {
        reviewer_name: reviewerName,
        reviewer_email: reviewerEmail,
        overall_comments: overallComments || null,
        comments: commentList,
      });
      toast.success("Submission returned with comments");
      router.push("/admin/submissions");
    } catch {
      toast.error("Failed to return submission");
    } finally {
      setSubmitting(false);
    }
  };

  if (!submission) {
    return <div className="text-center py-12 text-gray-500">Loading review...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Risk Score Display - Always visible at top */}
      <RiskScoreDisplay submissionId={submissionId} autoRefresh={false} />
      
      <div>
        <h1 className="text-2xl font-bold">Review: {submission.project_name}</h1>
        <p className="text-gray-500">
          Submitted by {submission.submitter_name} ({submission.submitter_email})
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
            {qs.map((q, idx) => {
              const val = responseMap.get(q.id);
              const isExpanded = expandedComments.has(q.id);
              return (
                <div key={q.id} className="border-b pb-3 last:border-0">
                  <p className="font-medium text-sm">
                    <span className="text-gray-400 mr-1">{idx + 1}.</span>
                    {q.question_text}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {formatValue(val)}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-1"
                    onClick={() => toggleComment(q.id)}
                  >
                    <MessageSquare className="h-3 w-3 mr-1" />
                    {isExpanded ? "Hide Comment" : "Add Comment"}
                  </Button>
                  {isExpanded && (
                    <Textarea
                      className="mt-2"
                      placeholder="Enter review comment..."
                      value={comments[q.id] || ""}
                      onChange={(e) =>
                        setComments({ ...comments, [q.id]: e.target.value })
                      }
                      rows={2}
                    />
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      ))}

      <Card>
        <CardHeader>
          <CardTitle>Reviewer Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Reviewer Name *</Label>
              <Input
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Reviewer Email *</Label>
              <Input
                type="email"
                value={reviewerEmail}
                onChange={(e) => setReviewerEmail(e.target.value)}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Overall Comments</Label>
            <Textarea
              value={overallComments}
              onChange={(e) => setOverallComments(e.target.value)}
              rows={3}
            />
          </div>
          <div className="flex gap-4">
            <Button
              className="flex-1"
              onClick={handleApprove}
              disabled={submitting}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Approve
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              onClick={handleReturn}
              disabled={submitting}
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Return with Comments
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
