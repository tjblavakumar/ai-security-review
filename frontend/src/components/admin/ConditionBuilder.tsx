"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Trash2, GitBranch, Save } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import type {
  Question,
  QuestionCondition,
  QuestionConditionCreate,
  ConditionOperator,
} from "@/lib/types";

interface ConditionBuilderProps {
  questionId: number;
  conditions: QuestionCondition[];
  allQuestions: Question[];
  onUpdate: () => void;
}

const OPERATORS: { value: ConditionOperator; label: string }[] = [
  { value: "equals", label: "Equals" },
  { value: "not_equals", label: "Not Equals" },
  { value: "contains", label: "Contains" },
  { value: "not_contains", label: "Does Not Contain" },
  { value: "greater_than", label: "Greater Than" },
  { value: "less_than", label: "Less Than" },
  { value: "regex", label: "Matches Regex" },
  { value: "is_empty", label: "Is Empty" },
  { value: "is_not_empty", label: "Is Not Empty" },
];

const NO_VALUE_OPS: ConditionOperator[] = ["is_empty", "is_not_empty"];

interface ConditionRow {
  depends_on_question_id: number;
  operator: ConditionOperator;
  expected_value: string;
}

export default function ConditionBuilder({
  questionId,
  conditions,
  allQuestions,
  onUpdate,
}: ConditionBuilderProps) {
  const [rows, setRows] = useState<ConditionRow[]>(
    conditions.map((c) => ({
      depends_on_question_id: c.depends_on_question_id,
      operator: c.operator || "equals",
      expected_value: c.expected_value,
    }))
  );
  const [saving, setSaving] = useState(false);

  const otherQuestions = allQuestions.filter((q) => q.id !== questionId);

  const addRow = () => {
    setRows([
      ...rows,
      {
        depends_on_question_id: otherQuestions[0]?.id || 0,
        operator: "equals",
        expected_value: "",
      },
    ]);
  };

  const removeRow = (index: number) => {
    setRows(rows.filter((_, i) => i !== index));
  };

  const updateRow = (index: number, field: keyof ConditionRow, value: string | number) => {
    const updated = [...rows];
    if (field === "depends_on_question_id") {
      updated[index] = { ...updated[index], [field]: Number(value) };
    } else {
      updated[index] = { ...updated[index], [field]: value };
    }
    setRows(updated);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload: QuestionConditionCreate[] = rows.map((r) => ({
        depends_on_question_id: r.depends_on_question_id,
        operator: r.operator,
        expected_value: NO_VALUE_OPS.includes(r.operator) ? "" : r.expected_value,
      }));
      await api.put(`/questions/${questionId}/conditions`, payload);
      toast.success("Conditions saved");
      onUpdate();
    } catch {
      toast.error("Failed to save conditions");
    } finally {
      setSaving(false);
    }
  };

  const getQuestionLabel = (id: number) => {
    const q = allQuestions.find((q) => q.id === id);
    if (!q) return `Question #${id}`;
    const text = q.question_text.length > 60 ? q.question_text.slice(0, 60) + "..." : q.question_text;
    return `#${q.id}: ${text}`;
  };

  return (
    <Card className="border-amber-200 bg-amber-50/30">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-amber-600" />
            <CardTitle className="text-sm font-medium text-amber-800">
              Conditional Logic
            </CardTitle>
            <Badge variant="outline" className="text-xs">
              {rows.length} condition{rows.length !== 1 ? "s" : ""}
            </Badge>
          </div>
          <Button variant="ghost" size="sm" onClick={addRow}>
            <Plus className="h-3 w-3 mr-1" />
            Add Condition
          </Button>
        </div>
        <p className="text-xs text-amber-600">
          This question is shown only when ALL conditions below are met.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {rows.length === 0 ? (
          <p className="text-xs text-gray-400 text-center py-2">
            No conditions — this question is always shown.
          </p>
        ) : (
          rows.map((row, i) => (
            <div key={i} className="flex items-start gap-2 p-3 rounded-md bg-white border">
              {i > 0 && (
                <Badge className="mt-1.5 bg-amber-100 text-amber-700 text-xs shrink-0">
                  AND
                </Badge>
              )}
              <div className="flex-1 space-y-2">
                <div>
                  <Label className="text-xs">If answer to:</Label>
                  <Select
                    value={String(row.depends_on_question_id)}
                    onValueChange={(v) => updateRow(i, "depends_on_question_id", v)}
                  >
                    <SelectTrigger className="text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {otherQuestions.map((q) => (
                        <SelectItem key={q.id} value={String(q.id)} className="text-xs">
                          {getQuestionLabel(q.id)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs">Operator:</Label>
                    <Select
                      value={row.operator}
                      onValueChange={(v) => updateRow(i, "operator", v)}
                    >
                      <SelectTrigger className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {OPERATORS.map((op) => (
                          <SelectItem key={op.value} value={op.value} className="text-xs">
                            {op.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  {!NO_VALUE_OPS.includes(row.operator) && (
                    <div>
                      <Label className="text-xs">Value:</Label>
                      <Input
                        value={row.expected_value}
                        onChange={(e) => updateRow(i, "expected_value", e.target.value)}
                        placeholder="Expected value..."
                        className="text-xs"
                      />
                    </div>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeRow(i)}
                className="text-red-500 hover:text-red-700 mt-5 shrink-0"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))
        )}
        {rows.length > 0 && (
          <Button size="sm" onClick={handleSave} disabled={saving} className="w-full">
            <Save className="h-3 w-3 mr-1" />
            {saving ? "Saving..." : "Save Conditions"}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
