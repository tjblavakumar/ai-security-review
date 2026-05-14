"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { ChevronLeft, ChevronRight, Save } from "lucide-react";
import AISuggestionPanel from "@/components/ai/AISuggestionPanel";
import ChatPanel from "@/components/ai/ChatPanel";
import RiskScoreDisplay from "@/components/risk/RiskScoreDisplay";
import type { Question, SubmissionDetail } from "@/lib/types";

export default function QuestionStepPage() {
  const params = useParams();
  const router = useRouter();
  const submissionId = params.id as string;
  const step = parseInt(params.step as string, 10);

  const [questions, setQuestions] = useState<Question[]>([]);
  const [submission, setSubmission] = useState<SubmissionDetail | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState<string>("");
  const [multiAnswer, setMultiAnswer] = useState<string[]>([]);
  const [additionalComments, setAdditionalComments] = useState<string>("");
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<Question[]>("/questions/preview"),
      api.get<SubmissionDetail>(`/submissions/${submissionId}`),
    ]).then(([qRes, sRes]) => {
      setQuestions(qRes.data);
      setSubmission(sRes.data);
    });
  }, [submissionId]);

  const getApplicableQuestions = useCallback((): Question[] => {
    if (!submission) return questions;
    const responseMap = new Map<number, string | null>();
    submission.responses.forEach((r) => responseMap.set(r.question_id, r.response_value));
    return questions.filter((q) => {
      if (!q.conditions || q.conditions.length === 0) return true;
      return q.conditions.every((c) => {
        const val = responseMap.get(c.depends_on_question_id);
        return val !== undefined && val !== null && val.toLowerCase().trim() === c.expected_value.toLowerCase().trim();
      });
    });
  }, [questions, submission]);

  const applicableQuestions = getApplicableQuestions();
  const currentQuestion = applicableQuestions[step - 1];
  const totalSteps = applicableQuestions.length;

  useEffect(() => {
    if (!currentQuestion || !submission) return;
    const existing = submission.responses.find(
      (r) => r.question_id === currentQuestion.id
    );
    if (existing?.response_value) {
      if (currentQuestion.question_type === "multi_select") {
        try {
          const parsed = JSON.parse(existing.response_value);
          if (parsed.selections && parsed.comments !== undefined) {
            // New format with comments
            setMultiAnswer(parsed.selections);
            setAdditionalComments(parsed.comments || "");
          } else {
            // Old format without comments
            setMultiAnswer(parsed);
            setAdditionalComments("");
          }
        } catch {
          setMultiAnswer([]);
          setAdditionalComments("");
        }
        setCurrentAnswer("");
      } else if (currentQuestion.question_type === "yes_no" || currentQuestion.question_type === "single_select") {
        try {
          const parsed = JSON.parse(existing.response_value);
          if (parsed.selection && parsed.comments !== undefined) {
            // New format with comments
            setCurrentAnswer(parsed.selection);
            setAdditionalComments(parsed.comments || "");
          } else {
            // Old format without comments
            setCurrentAnswer(existing.response_value);
            setAdditionalComments("");
          }
        } catch {
          // Plain string value
          setCurrentAnswer(existing.response_value);
          setAdditionalComments("");
        }
        setMultiAnswer([]);
      } else {
        setCurrentAnswer(existing.response_value);
        setMultiAnswer([]);
        setAdditionalComments("");
      }
    } else {
      setCurrentAnswer("");
      setMultiAnswer([]);
      setAdditionalComments("");
    }
  }, [currentQuestion, submission]);

  const getAnswerValue = (): string => {
    if (currentQuestion?.question_type === "multi_select") {
      return JSON.stringify({
        selections: multiAnswer,
        comments: additionalComments || ""
      });
    }
    if (currentQuestion?.question_type === "yes_no" || currentQuestion?.question_type === "single_select") {
      if (additionalComments) {
        return JSON.stringify({
          selection: currentAnswer,
          comments: additionalComments
        });
      }
      return currentAnswer;
    }
    return currentAnswer;
  };

  const saveResponse = async () => {
    if (!currentQuestion) return;
    setSaving(true);
    try {
      const res = await api.post<SubmissionDetail>(
        `/submissions/${submissionId}/responses`,
        {
          responses: [
            {
              question_id: currentQuestion.id,
              response_value: getAnswerValue() || null,
              is_skipped: false,
            },
          ],
          current_step: step,
        }
      );
      setSubmission(res.data);
      setLastSaved(new Date());
    } catch {
      toast.error("Failed to save response");
    } finally {
      setSaving(false);
    }
  };

  const handleNext = async () => {
    await saveResponse();
    if (step < totalSteps) {
      router.push(`/submit/${submissionId}/question/${step + 1}`);
    } else {
      router.push(`/submit/${submissionId}/summary`);
    }
  };

  const handlePrevious = async () => {
    await saveResponse();
    if (step > 1) {
      router.push(`/submit/${submissionId}/question/${step - 1}`);
    }
  };

  const handleSaveDraft = async () => {
    await saveResponse();
    toast.success("Draft saved!");
  };

  if (!currentQuestion) {
    return <div className="text-center py-12 text-gray-500">Loading question...</div>;
  }

  const options: string[] = currentQuestion.options
    ? JSON.parse(currentQuestion.options)
    : [];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Risk Score Display - Always visible at top */}
      <RiskScoreDisplay submissionId={submissionId} autoRefresh={true} />
      
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            Question {step} of {totalSteps}
          </span>
          {lastSaved && (
            <span>Last saved: {lastSaved.toLocaleTimeString()}</span>
          )}
        </div>
        <Progress value={(step / totalSteps) * 100} className="h-2" />
        <p className="text-xs text-gray-400">
          Some questions may be skipped based on your answers.
        </p>
      </div>

      <Card>
        <CardHeader>
          {currentQuestion.category && (
            <Badge variant="secondary" className="w-fit mb-2">
              {currentQuestion.category.name}
            </Badge>
          )}
          <CardTitle className="text-xl">{currentQuestion.question_text}</CardTitle>
          {currentQuestion.description && (
            <p className="text-sm text-gray-500 mt-1">
              {currentQuestion.description}
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {currentQuestion.question_type === "text" && (
            <Input
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Enter your answer..."
            />
          )}

          {currentQuestion.question_type === "textarea" && (
            <Textarea
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Enter your detailed answer..."
              rows={5}
            />
          )}

          {currentQuestion.question_type === "yes_no" && (
            <div className="space-y-3">
              <div className="flex gap-4">
                <Button
                  type="button"
                  variant={currentAnswer === "Yes" ? "default" : "outline"}
                  onClick={() => setCurrentAnswer("Yes")}
                  className="flex-1"
                >
                  Yes
                </Button>
                <Button
                  type="button"
                  variant={currentAnswer === "No" ? "default" : "outline"}
                  onClick={() => setCurrentAnswer("No")}
                  className="flex-1"
                >
                  No
                </Button>
              </div>
              
              {/* Additional Comments for Yes/No */}
              <div className="space-y-2 pt-2">
                <Label htmlFor="additional-comments" className="text-sm text-gray-600">
                  Additional Information (Optional)
                </Label>
                <Textarea
                  id="additional-comments"
                  value={additionalComments}
                  onChange={(e) => setAdditionalComments(e.target.value)}
                  placeholder="Add context, explanation, or additional details here..."
                  rows={3}
                  className="text-sm"
                />
                <p className="text-xs text-gray-400">
                  Use AI suggestion to help fill this field, or provide your own context.
                </p>
              </div>
            </div>
          )}

          {currentQuestion.question_type === "single_select" && (
            <div className="space-y-3">
              <Select value={currentAnswer} onValueChange={setCurrentAnswer}>
                <SelectTrigger>
                  <SelectValue placeholder="Select an option..." />
                </SelectTrigger>
                <SelectContent>
                  {options.map((opt) => (
                    <SelectItem key={opt} value={opt}>
                      {opt}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {/* Additional Comments for Single Select */}
              {currentAnswer && (
                <div className="space-y-2 pt-2">
                  <Label htmlFor="additional-comments" className="text-sm text-gray-600">
                    Additional Information (Optional)
                  </Label>
                  <Textarea
                    id="additional-comments"
                    value={additionalComments}
                    onChange={(e) => setAdditionalComments(e.target.value)}
                    placeholder="Add context, explanation, or additional details here..."
                    rows={3}
                    className="text-sm"
                  />
                  <p className="text-xs text-gray-400">
                    Use AI suggestion to help fill this field, or provide your own context.
                  </p>
                </div>
              )}
            </div>
          )}

          {currentQuestion.question_type === "multi_select" && (
            <div className="space-y-3">
              <div className="space-y-3">
                {options.map((opt) => (
                  <div key={opt} className="flex items-center gap-2">
                    <Checkbox
                      id={opt}
                      checked={multiAnswer.includes(opt)}
                      onCheckedChange={(checked) => {
                        setMultiAnswer(
                          checked
                            ? [...multiAnswer, opt]
                            : multiAnswer.filter((a) => a !== opt)
                        );
                      }}
                    />
                    <Label htmlFor={opt} className="cursor-pointer">
                      {opt}
                    </Label>
                  </div>
                ))}
              </div>
              
              {/* Additional Comments for Multi Select */}
              {multiAnswer.length > 0 && (
                <div className="space-y-2 pt-2">
                  <Label htmlFor="additional-comments" className="text-sm text-gray-600">
                    Additional Information (Optional)
                  </Label>
                  <Textarea
                    id="additional-comments"
                    value={additionalComments}
                    onChange={(e) => setAdditionalComments(e.target.value)}
                    placeholder="Add context, explanation, or additional details here..."
                    rows={3}
                    className="text-sm"
                  />
                  <p className="text-xs text-gray-400">
                    Use AI suggestion to help fill this field, or provide your own context.
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <AISuggestionPanel
        questionId={currentQuestion.id}
        submissionId={submissionId}
        onUseSuggestion={(text) => {
          if (currentQuestion.question_type === "text" || currentQuestion.question_type === "textarea") {
            setCurrentAnswer(text);
          } else if (
            currentQuestion.question_type === "yes_no" || 
            currentQuestion.question_type === "single_select" || 
            currentQuestion.question_type === "multi_select"
          ) {
            // For selection types, put AI suggestion in comments field
            setAdditionalComments(text);
          }
        }}
      />

      <ChatPanel
        questionId={currentQuestion.id}
        submissionId={submissionId}
      />

      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={handlePrevious} disabled={step === 1}>
          <ChevronLeft className="h-4 w-4 mr-1" />
          Previous
        </Button>
        <Button variant="ghost" onClick={handleSaveDraft} disabled={saving}>
          <Save className="h-4 w-4 mr-1" />
          {saving ? "Saving..." : "Save Draft"}
        </Button>
        <Button onClick={handleNext}>
          {step === totalSteps ? "Review Summary" : "Next"}
          {step < totalSteps && <ChevronRight className="h-4 w-4 ml-1" />}
        </Button>
      </div>
    </div>
  );
}
