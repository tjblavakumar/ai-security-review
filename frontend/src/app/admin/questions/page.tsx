"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
  Plus,
  Edit,
  XCircle,
  GripVertical,
  Download,
  Upload,
} from "lucide-react";
import type { Question, QuestionCategory, QuestionType } from "@/lib/types";

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

// ── Sortable row component ──────────────────────────────────────────

function SortableRow({
  q,
  onToggle,
}: {
  q: Question;
  onToggle: (q: Question) => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: q.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <tr ref={setNodeRef} style={style} className="border-b last:border-0">
      <td className="p-2 w-8">
        <button
          {...attributes}
          {...listeners}
          className="cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600"
        >
          <GripVertical className="h-4 w-4" />
        </button>
      </td>
      <td className="p-2 text-sm text-gray-500 w-12">{q.display_order}</td>
      <td className="p-2 text-sm max-w-xs truncate">{q.question_text}</td>
      <td className="p-2">
        <Badge variant="outline">{q.question_type}</Badge>
      </td>
      <td className="p-2 text-center">{q.is_required ? "Yes" : "No"}</td>
      <td className="p-2 text-center">
        <Badge
          className={
            q.is_active
              ? "bg-green-100 text-green-700"
              : "bg-gray-100 text-gray-500"
          }
        >
          {q.is_active ? "Active" : "Inactive"}
        </Badge>
      </td>
      <td className="p-2 text-center">
        {q.conditions && q.conditions.length > 0 ? (
          <Badge className="bg-amber-100 text-amber-700 text-xs">
            {q.conditions.length}
          </Badge>
        ) : (
          <span className="text-gray-300 text-xs">—</span>
        )}
      </td>
      <td className="p-2 text-right space-x-1">
        <Link href={`/admin/questions/${q.id}/edit`}>
          <Button size="sm" variant="ghost">
            <Edit className="h-3 w-3" />
          </Button>
        </Link>
        <Button size="sm" variant="ghost" onClick={() => onToggle(q)}>
          <XCircle className="h-3 w-3" />
        </Button>
      </td>
    </tr>
  );
}

// ── Main page ───────────────────────────────────────────────────────

export default function ManageQuestionsPage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [categories, setCategories] = useState<QuestionCategory[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importText, setImportText] = useState("");
  const [importOverwrite, setImportOverwrite] = useState(false);
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

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const load = () => {
    api.get<Question[]>("/questions").then((res) => setQuestions(res.data));
    api
      .get<QuestionCategory[]>("/questions/categories")
      .then((res) => setCategories(res.data));
  };

  useEffect(load, []);

  const grouped = questions.reduce<Record<string, Question[]>>((acc, q) => {
    const cat = categories.find((c) => c.id === q.category_id);
    const name = cat?.name || "Uncategorized";
    if (!acc[name]) acc[name] = [];
    acc[name].push(q);
    return acc;
  }, {});

  const handleAdd = async () => {
    if (!form.question_text || !form.category_id) {
      toast.error("Question text and category are required");
      return;
    }
    try {
      const body: Record<string, unknown> = { ...form };
      if (
        (form.question_type === "single_select" ||
          form.question_type === "multi_select") &&
        form.options
      ) {
        body.options = form.options;
      } else {
        body.options = null;
      }
      await api.post("/questions", body);
      toast.success("Question added");
      setDialogOpen(false);
      setForm({
        question_text: "",
        description: "",
        category_id: 0,
        question_type: "text",
        options: "",
        is_required: true,
        is_active: true,
        allows_attachment: false,
        display_order: 0,
      });
      load();
    } catch {
      toast.error("Failed to add question");
    }
  };

  const toggleActive = async (q: Question) => {
    try {
      await api.put(`/questions/${q.id}`, { is_active: !q.is_active });
      load();
    } catch {
      toast.error("Failed to update question");
    }
  };

  const handleDragEnd = useCallback(
    async (categoryName: string, event: DragEndEvent) => {
      const { active, over } = event;
      if (!over || active.id === over.id) return;

      const catQuestions = grouped[categoryName];
      if (!catQuestions) return;

      const oldIndex = catQuestions.findIndex((q) => q.id === active.id);
      const newIndex = catQuestions.findIndex((q) => q.id === over.id);
      if (oldIndex === -1 || newIndex === -1) return;

      const reordered = arrayMove(catQuestions, oldIndex, newIndex);
      const items = reordered.map((q, i) => ({
        id: q.id,
        display_order: i + 1,
      }));

      // Optimistic UI update
      setQuestions((prev) => {
        const updated = [...prev];
        for (const item of items) {
          const idx = updated.findIndex((q) => q.id === item.id);
          if (idx !== -1) {
            updated[idx] = { ...updated[idx], display_order: item.display_order };
          }
        }
        return updated;
      });

      try {
        await api.patch("/questions/reorder", { items });
      } catch {
        toast.error("Failed to save order");
        load();
      }
    },
    [grouped]
  );

  const handleExport = async () => {
    try {
      const res = await api.get<unknown[]>("/questions/bulk/export");
      const blob = new Blob([JSON.stringify(res.data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "questions-export.json";
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported ${Array.isArray(res.data) ? res.data.length : 0} questions`);
    } catch {
      toast.error("Export failed");
    }
  };

  const handleImport = async () => {
    try {
      const parsed = JSON.parse(importText);
      const payload = Array.isArray(parsed)
        ? { questions: parsed, overwrite: importOverwrite }
        : { ...parsed, overwrite: importOverwrite };
      const res = await api.post<{ created: number }>("/questions/bulk/import", payload);
      toast.success(`Imported ${res.data.created} questions`);
      setImportDialogOpen(false);
      setImportText("");
      load();
    } catch (e) {
      toast.error(e instanceof SyntaxError ? "Invalid JSON" : "Import failed");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Manage Questions</h1>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-4 w-4 mr-1" />
            Export
          </Button>
          <Dialog open={importDialogOpen} onOpenChange={setImportDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Upload className="h-4 w-4 mr-1" />
                Import
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Import Questions</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Paste JSON</Label>
                  <Textarea
                    value={importText}
                    onChange={(e) => setImportText(e.target.value)}
                    rows={10}
                    placeholder='[{"question_text": "...", "category_name": "...", "question_type": "text", ...}]'
                    className="font-mono text-xs"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={importOverwrite}
                    onCheckedChange={setImportOverwrite}
                  />
                  <Label className="text-sm text-red-600">
                    Overwrite existing questions (deletes all current questions)
                  </Label>
                </div>
                <Button className="w-full" onClick={handleImport}>
                  Import Questions
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Question
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Add New Question</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
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
                  <Input
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
                    }
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Category *</Label>
                    <Select
                      value={String(form.category_id || "")}
                      onValueChange={(v) =>
                        setForm({ ...form, category_id: parseInt(v) })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select..." />
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
                    <Label>Type *</Label>
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
                        <SelectItem value="single_select">
                          Single Select
                        </SelectItem>
                        <SelectItem value="multi_select">
                          Multi Select
                        </SelectItem>
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
                      rows={2}
                    />
                  </div>
                )}
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={form.is_required}
                      onCheckedChange={(v) =>
                        setForm({ ...form, is_required: v })
                      }
                    />
                    <Label>Required</Label>
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
                <Button className="w-full" onClick={handleAdd}>
                  Add Question
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <p className="text-sm text-gray-500">
        Drag the grip handle to reorder questions within each category.
      </p>

      {Object.entries(grouped).map(([category, qs]) => (
        <Card key={category}>
          <CardHeader>
            <CardTitle className="text-lg">{category}</CardTitle>
          </CardHeader>
          <CardContent>
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={(e) => handleDragEnd(category, e)}
            >
              <table className="w-full">
                <thead>
                  <tr className="border-b text-sm text-gray-500">
                    <th className="p-2 w-8"></th>
                    <th className="text-left p-2 w-12">Order</th>
                    <th className="text-left p-2">Question</th>
                    <th className="text-left p-2">Type</th>
                    <th className="text-center p-2">Required</th>
                    <th className="text-center p-2">Active</th>
                    <th className="text-center p-2">Conds</th>
                    <th className="text-right p-2">Actions</th>
                  </tr>
                </thead>
                <SortableContext
                  items={qs.map((q) => q.id)}
                  strategy={verticalListSortingStrategy}
                >
                  <tbody>
                    {qs.map((q) => (
                      <SortableRow
                        key={q.id}
                        q={q}
                        onToggle={toggleActive}
                      />
                    ))}
                  </tbody>
                </SortableContext>
              </table>
            </DndContext>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
