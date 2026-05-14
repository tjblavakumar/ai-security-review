"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
  Plus,
  Edit2,
  Trash2,
  Save,
  AlertTriangle,
  Shield,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import type {
  RiskRule,
  RiskRuleCreate,
  RiskThreshold,
  RiskConfigSummary,
  Question,
  AIRiskSuggestion,
} from "@/lib/types";

export default function RiskConfigPage() {
  const [summary, setSummary] = useState<RiskConfigSummary | null>(null);
  const [rules, setRules] = useState<RiskRule[]>([]);
  const [thresholds, setThresholds] = useState<RiskThreshold[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);

  // Rule dialog state
  const [ruleDialogOpen, setRuleDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<RiskRule | null>(null);
  const [ruleForm, setRuleForm] = useState<RiskRuleCreate>({
    name: "",
    description: "",
    keywords: [],
    high_risk_answers: [],
    risk_value: 5,
    is_active: true,
  });
  const [keywordInput, setKeywordInput] = useState("");
  const [answerInput, setAnswerInput] = useState("");

  // AI suggestion state
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<AIRiskSuggestion | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      console.log('Loading risk configuration...');
      
      const [summaryRes, rulesRes, thresholdsRes, questionsRes] = await Promise.all([
        api.get<RiskConfigSummary>("/risk/config/summary"),
        api.get<RiskRule[]>("/risk/rules"),
        api.get<RiskThreshold[]>("/risk/thresholds"),
        api.get<Question[]>("/questions/preview"),
      ]);

      console.log('Summary:', summaryRes.data);
      console.log('Rules:', rulesRes.data);
      console.log('Thresholds:', thresholdsRes.data);
      console.log('Questions:', questionsRes.data);

      setSummary(summaryRes.data);
      setRules(rulesRes.data);
      setThresholds(thresholdsRes.data);
      setQuestions(questionsRes.data);
    } catch (error) {
      console.error('Failed to load risk configuration:', error);
      toast.error("Failed to load risk configuration");
    } finally {
      setLoading(false);
    }
  };

  // ---------- Risk Rules Functions ----------

  const openRuleDialog = (rule?: RiskRule) => {
    if (rule) {
      setEditingRule(rule);
      setRuleForm({
        name: rule.name,
        description: rule.description || "",
        keywords: rule.keywords,
        high_risk_answers: rule.high_risk_answers,
        risk_value: rule.risk_value,
        is_active: rule.is_active,
      });
    } else {
      setEditingRule(null);
      setRuleForm({
        name: "",
        description: "",
        keywords: [],
        high_risk_answers: [],
        risk_value: 5,
        is_active: true,
      });
    }
    setRuleDialogOpen(true);
  };

  const saveRule = async () => {
    // Validation
    if (!ruleForm.name.trim()) {
      toast.error("Rule name is required");
      return;
    }
    if (ruleForm.keywords.length === 0) {
      toast.error("At least one keyword is required");
      return;
    }
    if (ruleForm.high_risk_answers.length === 0) {
      toast.error("At least one high-risk answer pattern is required");
      return;
    }
    
    try {
      if (editingRule) {
        await api.put(`/risk/rules/${editingRule.id}`, ruleForm);
        toast.success("Risk rule updated");
      } else {
        await api.post("/risk/rules", ruleForm);
        toast.success("Risk rule created");
      }
      setRuleDialogOpen(false);
      setAiSuggestion(null); // Clear AI suggestion
      loadData();
    } catch (error: any) {
      console.error('Save rule error:', error);
      
      // Handle duplicate name error
      if (error?.response?.status === 500 && error?.response?.data?.message?.includes('UNIQUE constraint')) {
        toast.error(`A rule with the name "${ruleForm.name}" already exists. Please choose a different name.`);
      } else if (error?.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error("Failed to save risk rule");
      }
    }
  };

  const deleteRule = async (id: number) => {
    if (!confirm("Are you sure you want to delete this rule?")) return;
    try {
      await api.delete(`/risk/rules/${id}`);
      toast.success("Risk rule deleted");
      loadData();
    } catch (error) {
      toast.error("Failed to delete risk rule");
    }
  };

  const toggleRuleActive = async (rule: RiskRule) => {
    try {
      await api.put(`/risk/rules/${rule.id}`, { is_active: !rule.is_active });
      toast.success(`Rule ${rule.is_active ? "disabled" : "enabled"}`);
      loadData();
    } catch (error) {
      toast.error("Failed to update rule");
    }
  };

  const addKeyword = () => {
    if (keywordInput.trim() && !ruleForm.keywords.includes(keywordInput.trim())) {
      setRuleForm({
        ...ruleForm,
        keywords: [...ruleForm.keywords, keywordInput.trim()],
      });
      setKeywordInput("");
    }
  };

  const removeKeyword = (keyword: string) => {
    setRuleForm({
      ...ruleForm,
      keywords: ruleForm.keywords.filter((k) => k !== keyword),
    });
  };

  const addAnswer = () => {
    if (answerInput.trim() && !ruleForm.high_risk_answers.includes(answerInput.trim())) {
      setRuleForm({
        ...ruleForm,
        high_risk_answers: [...ruleForm.high_risk_answers, answerInput.trim()],
      });
      setAnswerInput("");
    }
  };

  const removeAnswer = (answer: string) => {
    setRuleForm({
      ...ruleForm,
      high_risk_answers: ruleForm.high_risk_answers.filter((a) => a !== answer),
    });
  };

  // ---------- AI Suggestions ----------

  const getAISuggestion = async (type: string, context: string) => {
    setAiLoading(true);
    try {
      const response = await api.post<AIRiskSuggestion>("/risk/ai/suggest", {
        context,
        suggestion_type: type,
      });
      setAiSuggestion(response.data);
      toast.success("AI suggestion generated");
    } catch (error) {
      toast.error("Failed to generate AI suggestion");
    } finally {
      setAiLoading(false);
    }
  };

  const applyAISuggestion = () => {
    if (!aiSuggestion?.data) return;
    
    if (aiSuggestion.data.name) {
      // Rule suggestion
      setRuleForm({
        name: aiSuggestion.data.name || ruleForm.name,
        description: aiSuggestion.data.description || ruleForm.description,
        keywords: aiSuggestion.data.keywords || ruleForm.keywords,
        high_risk_answers: aiSuggestion.data.high_risk_answers || ruleForm.high_risk_answers,
        risk_value: aiSuggestion.data.risk_value || ruleForm.risk_value,
        is_active: true,
      });
      toast.success("AI suggestion applied to form");
    }
  };

  // ---------- Question Weight Update ----------

  const updateQuestionWeight = async (questionId: number, weight: number) => {
    try {
      await api.put("/risk/questions/weight", {
        question_id: questionId,
        risk_weight: weight,
      });
      toast.success("Question weight updated");
      loadData();
    } catch (error) {
      toast.error("Failed to update weight");
    }
  };

  const updateCategoryWeights = async (categoryId: number, weight: number) => {
    try {
      await api.put(`/risk/questions/weight/category/${categoryId}?risk_weight=${weight}`);
      toast.success("Category weights updated");
      loadData();
    } catch (error) {
      toast.error("Failed to update category weights");
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Risk Configuration</h1>
        <p className="text-gray-500 mt-1">
          Manage risk scoring rules, thresholds, and question weights
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Rules</p>
                <p className="text-2xl font-bold">{summary?.total_rules || 0}</p>
              </div>
              <Shield className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Rules</p>
                <p className="text-2xl font-bold">{summary?.active_rules || 0}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Thresholds</p>
                <p className="text-2xl font-bold">{summary?.thresholds.length || 0}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Question Weight</p>
                <p className="text-2xl font-bold">
                  {summary?.average_question_weight.toFixed(1) || "5.0"}
                </p>
              </div>
              <Shield className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="rules" className="space-y-6">
        <TabsList>
          <TabsTrigger value="rules">Risk Rules</TabsTrigger>
          <TabsTrigger value="thresholds">Thresholds</TabsTrigger>
          <TabsTrigger value="weights">Question Weights</TabsTrigger>
        </TabsList>

        {/* Risk Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Risk Scoring Rules</h2>
            <Button onClick={() => openRuleDialog()}>
              <Plus className="h-4 w-4 mr-2" />
              Add Rule
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {rules.length === 0 ? (
              <div className="col-span-2 text-center py-12 text-gray-500">
                <Shield className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">No risk rules configured</p>
                <p className="text-sm mt-2">Click "Add Rule" to create your first risk scoring rule</p>
              </div>
            ) : (
              rules.map((rule) => (
              <Card key={rule.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{rule.name}</CardTitle>
                      <p className="text-sm text-gray-500 mt-1">
                        {rule.description || "No description"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={rule.is_active}
                        onCheckedChange={() => toggleRuleActive(rule)}
                      />
                      <Badge variant={rule.is_active ? "default" : "secondary"}>
                        {rule.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-700">Risk Value</p>
                    <Badge variant="destructive" className="text-lg">
                      {rule.risk_value} / 10
                    </Badge>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Keywords</p>
                    <div className="flex flex-wrap gap-1">
                      {rule.keywords.map((keyword, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      High Risk Answers
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {rule.high_risk_answers.map((answer, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {answer}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openRuleDialog(rule)}
                    >
                      <Edit2 className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteRule(rule.id)}
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Thresholds Tab */}
        <TabsContent value="thresholds" className="space-y-4">
          <h2 className="text-xl font-semibold">Risk Level Thresholds</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {thresholds.map((threshold) => (
              <Card key={threshold.id}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: threshold.color }}
                    />
                    {threshold.level.toUpperCase()}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm">
                    <span className="font-medium">Range:</span> {threshold.min_score} -{" "}
                    {threshold.max_score}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">Color:</span> {threshold.color}
                  </p>
                  <div className="h-4 rounded-full" style={{ backgroundColor: threshold.color }} />
                </CardContent>
              </Card>
            ))}
          </div>

          <p className="text-sm text-gray-500">
            Note: Threshold editing will be available in a future update
          </p>
        </TabsContent>

        {/* Question Weights Tab */}
        <TabsContent value="weights" className="space-y-4">
          <h2 className="text-xl font-semibold">Question Risk Weights</h2>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {questions.map((question) => (
                  <div
                    key={question.id}
                    className="flex items-center justify-between border-b pb-3 last:border-0"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-sm">{question.question_text}</p>
                      <p className="text-xs text-gray-500">
                        {question.category?.name || "Uncategorized"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        min="1"
                        max="10"
                        value={question.risk_weight || 5}
                        onChange={(e) =>
                          updateQuestionWeight(question.id, parseInt(e.target.value))
                        }
                        className="w-20"
                      />
                      <span className="text-sm text-gray-500">/ 10</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Rule Dialog */}
      <Dialog open={ruleDialogOpen} onOpenChange={setRuleDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingRule ? "Edit Risk Rule" : "Create Risk Rule"}
            </DialogTitle>
            <DialogDescription>
              Configure how risk is calculated for specific question patterns
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* AI Suggestion Panel */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4">
                <div className="flex items-start gap-3">
                  <Sparkles className="h-5 w-5 text-blue-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-medium text-blue-900">AI Assistant</h3>
                    <p className="text-sm text-blue-700 mb-3">
                      Get AI-powered suggestions for risk rules
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        getAISuggestion("rule", "Suggest a risk rule for data security")
                      }
                      disabled={aiLoading}
                    >
                      {aiLoading ? "Generating..." : "Get AI Suggestion"}
                    </Button>

                    {aiSuggestion && (
                      <div className="mt-3 p-3 bg-white rounded border">
                        <p className="text-sm font-medium mb-2">Suggestion:</p>
                        <p className="text-sm text-gray-700 mb-2">
                          {aiSuggestion.explanation}
                        </p>
                        <Button size="sm" onClick={applyAISuggestion}>
                          Apply Suggestion
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Form Fields */}
            <div className="space-y-2">
              <Label htmlFor="name">Rule Name *</Label>
              <Input
                id="name"
                value={ruleForm.name}
                onChange={(e) => setRuleForm({ ...ruleForm, name: e.target.value })}
                placeholder="e.g., pii, encryption"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={ruleForm.description || ""}
                onChange={(e) =>
                  setRuleForm({ ...ruleForm, description: e.target.value })
                }
                placeholder="What does this rule check for?"
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="risk_value">Risk Value (1-10) *</Label>
              <Input
                id="risk_value"
                type="number"
                min="1"
                max="10"
                value={ruleForm.risk_value}
                onChange={(e) =>
                  setRuleForm({ ...ruleForm, risk_value: parseInt(e.target.value) })
                }
              />
            </div>

            <div className="space-y-2">
              <Label>Keywords *</Label>
              <div className="flex gap-2">
                <Input
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && addKeyword()}
                  placeholder="Add keyword and press Enter"
                />
                <Button type="button" onClick={addKeyword}>
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {ruleForm.keywords.map((keyword, idx) => (
                  <Badge
                    key={idx}
                    variant="secondary"
                    className="cursor-pointer"
                    onClick={() => removeKeyword(keyword)}
                  >
                    {keyword} ×
                  </Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label>High Risk Answer Patterns *</Label>
              <div className="flex gap-2">
                <Input
                  value={answerInput}
                  onChange={(e) => setAnswerInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && addAnswer()}
                  placeholder="Add answer pattern and press Enter"
                />
                <Button type="button" onClick={addAnswer}>
                  Add
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {ruleForm.high_risk_answers.map((answer, idx) => (
                  <Badge
                    key={idx}
                    variant="secondary"
                    className="cursor-pointer"
                    onClick={() => removeAnswer(answer)}
                  >
                    {answer} ×
                  </Badge>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Switch
                checked={ruleForm.is_active}
                onCheckedChange={(checked) =>
                  setRuleForm({ ...ruleForm, is_active: checked })
                }
              />
              <Label>Active</Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setRuleDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={saveRule}>
              <Save className="h-4 w-4 mr-2" />
              Save Rule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
