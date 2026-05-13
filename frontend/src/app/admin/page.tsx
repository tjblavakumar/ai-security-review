"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { FileQuestion, ClipboardCheck, FileText, Bot, Shield } from "lucide-react";
import type { Question, Submission, AIStatus, PolicyDocument } from "@/lib/types";

export default function AdminDashboardPage() {
  const [questionCount, setQuestionCount] = useState(0);
  const [pendingCount, setPendingCount] = useState(0);
  const [policyCount, setPolicyCount] = useState(0);
  const [aiStatus, setAIStatus] = useState<AIStatus | null>(null);

  useEffect(() => {
    api.get<Question[]>("/questions").then((res) => setQuestionCount(res.data.length));
    api.get<Submission[]>("/reviews/queue").then((res) => setPendingCount(res.data.length));
    api.get<PolicyDocument[]>("/policies").then((res) => setPolicyCount(res.data.length)).catch(() => {});
    api.get<AIStatus>("/ai/status").then((res) => setAIStatus(res.data)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>

      {aiStatus && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <Bot className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">AI Status:</span>
              <Badge variant={aiStatus.enabled ? "default" : "secondary"}>
                {aiStatus.enabled ? "Enabled" : "Not Configured"}
              </Badge>
              {aiStatus.enabled && (
                <>
                  <span className="text-xs text-gray-500">Model: {aiStatus.model}</span>
                  <span className="text-xs text-gray-500">
                    RAG: {aiStatus.rag_indexed_documents} docs / {aiStatus.rag_total_chunks} chunks
                  </span>
                </>
              )}
              {!aiStatus.enabled && (
                <span className="text-xs text-gray-400">
                  Set OPENAI_API_KEY in .env to enable AI suggestions
                </span>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <FileQuestion className="h-8 w-8 text-blue-600 mb-2" />
            <CardTitle>Manage Questions</CardTitle>
            <CardDescription>
              Add, edit, and organize security review questions.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <span className="text-2xl font-bold text-gray-700">
              {questionCount} questions
            </span>
            <Link href="/admin/questions">
              <Button>Manage</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <ClipboardCheck className="h-8 w-8 text-green-600 mb-2" />
            <CardTitle>Review Submissions</CardTitle>
            <CardDescription>
              Review and approve pending security review submissions.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <span className="text-2xl font-bold text-gray-700">
              {pendingCount} pending
            </span>
            <Link href="/admin/submissions">
              <Button variant="outline">Review</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <FileText className="h-8 w-8 text-purple-600 mb-2" />
            <CardTitle>Policy Documents</CardTitle>
            <CardDescription>
              Manage policy documents for AI-powered RAG suggestions.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <span className="text-2xl font-bold text-gray-700">
              {policyCount} documents
            </span>
            <Link href="/admin/policies">
              <Button variant="outline">Manage</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow border-2 border-orange-200">
          <CardHeader>
            <Shield className="h-8 w-8 text-orange-600 mb-2" />
            <CardTitle>Risk Configuration</CardTitle>
            <CardDescription>
              Configure risk scoring rules, thresholds, and question weights.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <span className="text-sm font-medium text-orange-600">
              AI-Powered
            </span>
            <Link href="/admin/risk-config">
              <Button variant="outline">Configure</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
