"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Save } from "lucide-react";
import ConditionBuilder from "@/components/admin/ConditionBuilder";
import type { Question, QuestionCategory, QuestionType } from "@/lib/types";

export default function EditQuestionPage() {
  const params = useParams();
  const router = useRouter();
  const questionId = params.id as string;

  const [categories, setCategories] = useState<QuestionCategory[]>([]);
  const [allQuestions, setAllQuestions] = useState<Question[]>([]);
  const [question, setQuestion] = useState<Question | null>(null);
  const [form, setForm] = useState({
    question_text: "",
    description: "",
    category_id: 0,
    question_type: "text" as QuestionType,
    options: "",
    is_required: true,
    is_active: true,
    allows_attachment: false,
    display_order: 0,
  });
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([
      api.get<Question>(`/questions/${questionId}`),
      api.get<QuestionCategory[]>("/questions/categories"),
      api.get<Question[]>("/questions"),
    ]).then(([qRes, cRes, allRes]) => {
      const q = qRes.data;
      setQuestion(q);
      setForm({
        question_text: q.question_text,
        description: q.description || "",
        category_id: q.category_id,
        question_type: q.question_type,
        options: q.options || "",
        is_required: q.is_required,
        is_active: q.is_active,
        allows_attachment: q.allows_attachment,
        display_order: q.display_order,
      });
      setCategories(cRes.data);
      setAllQuestions(allRes.data);
      setLoading(false);
    });
  };

  useEffect(load, [questionId]);

  const handleSave = async () => {
    try {
      const body: Record<string, unknown> = { ...form };
      if (
        form.question_type !== "single_select" &&
        form.question_type !== "multi_select"
      ) {
        body.options = null;
      }
      await api.put(`/questions/${questionId}`, body);
      toast.success("Question updated");
      router.push("/admin/questions");
    } catch {
      toast.error("Failed to update question");
    }
  };

  if (loading || !question) {
    return <div className="text-center py-12 text-gray-500">Loading...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Edit Question</h1>

      <Card>
        <CardHeader>
          <CardTitle>Question Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Question Text *</Label>
            <Textarea
              value={form.question_text}
              onChange={(e) =>
                setForm({ ...form, question_text: e.target.value })
              }
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              rows={2}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Category</Label>
              <Select
                value={String(form.category_id)}
                onValueChange={(v) =>
                  setForm({ ...form, category_id: parseInt(v) })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <Select
                value={form.question_type}
                onValueChange={(v) =>
                  setForm({ ...form, question_type: v as QuestionType })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text">Text</SelectItem>
                  <SelectItem value="textarea">Textarea</SelectItem>
                  <SelectItem value="yes_no">Yes / No</SelectItem>
                  <SelectItem value="single_select">Single Select</SelectItem>
                  <SelectItem value="multi_select">Multi Select</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {(form.question_type === "single_select" ||
            form.question_type === "multi_select") && (
            <div className="space-y-2">
              <Label>Options (JSON array)</Label>
              <Textarea
                value={form.options}
                onChange={(e) =>
                  setForm({ ...form, options: e.target.value })
                }
                placeholder='["Option 1", "Option 2"]'
                rows={3}
              />
            </div>
          )}

          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <Switch
                checked={form.is_required}
                onCheckedChange={(v) => setForm({ ...form, is_required: v })}
              />
              <Label>Required</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={form.is_active}
                onCheckedChange={(v) => setForm({ ...form, is_active: v })}
              />
              <Label>Active</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={form.allows_attachment}
                onCheckedChange={(v) =>
                  setForm({ ...form, allows_attachment: v })
                }
              />
              <Label>Allows Attachment</Label>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Display Order</Label>
            <Input
              type="number"
              value={form.display_order}
              onChange={(e) =>
                setForm({
                  ...form,
                  display_order: parseInt(e.target.value) || 0,
                })
              }
            />
          </div>
        </CardContent>
      </Card>

      <ConditionBuilder
        questionId={parseInt(questionId)}
        conditions={question.conditions || []}
        allQuestions={allQuestions}
        onUpdate={load}
      />

      <Button className="w-full" onClick={handleSave}>
        <Save className="h-4 w-4 mr-2" />
        Save Changes
      </Button>
    </div>
  );
}
