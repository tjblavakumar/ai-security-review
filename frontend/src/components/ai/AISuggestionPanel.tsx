"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, RefreshCw, Copy, Check, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { AISuggestion } from "@/lib/types";

interface AISuggestionPanelProps {
  questionId: number;
  submissionId: string;
  onUseSuggestion?: (suggestion: string) => void;
}

const confidenceColors: Record<string, string> = {
  high: "bg-green-100 text-green-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-gray-100 text-gray-600",
};

export default function AISuggestionPanel({
  questionId,
  submissionId,
  onUseSuggestion,
}: AISuggestionPanelProps) {
  const [suggestion, setSuggestion] = useState<AISuggestion | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchSuggestion = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<AISuggestion>("/ai/suggest", {
        question_id: questionId,
        submission_id: parseInt(submissionId, 10),
      });
      setSuggestion(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get suggestion");
    } finally {
      setLoading(false);
    }
  }, [questionId, submissionId]);

  useEffect(() => {
    fetchSuggestion();
  }, [fetchSuggestion]);

  const handleCopy = async () => {
    if (!suggestion?.suggestion) return;
    await navigator.clipboard.writeText(suggestion.suggestion);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <Card className="border-blue-200 bg-blue-50/50">
        <CardContent className="py-4">
          <div className="flex items-center gap-3">
            <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
            <span className="text-sm text-blue-600">
              Generating AI suggestion...
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50/50">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-600">{error}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={fetchSuggestion}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!suggestion || !suggestion.enabled) {
    return (
      <Card className="border-dashed bg-gray-50">
        <CardContent className="py-4">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Lightbulb className="h-4 w-4" />
            <span>
              {suggestion?.explanation ||
                "AI suggestions require an OpenAI API key. Set OPENAI_API_KEY in your .env file."}
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-blue-200 bg-blue-50/30">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-blue-600" />
            <CardTitle className="text-sm font-medium text-blue-800">
              AI Suggestion
            </CardTitle>
            <Badge
              className={`text-xs ${confidenceColors[suggestion.confidence] || confidenceColors.low}`}
            >
              {suggestion.confidence} confidence
            </Badge>
          </div>
          <Button variant="ghost" size="sm" onClick={fetchSuggestion}>
            <RefreshCw className="h-3 w-3" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="rounded-md bg-white p-3 border border-blue-100">
          <p className="text-sm font-medium text-gray-900">
            {suggestion.suggestion}
          </p>
        </div>
        {suggestion.explanation && (
          <p className="text-xs text-gray-600">{suggestion.explanation}</p>
        )}
        {suggestion.policy_references && suggestion.policy_references.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {suggestion.policy_references.map((ref, i) => (
              <Badge key={i} variant="outline" className="text-xs">
                {ref}
              </Badge>
            ))}
          </div>
        )}
        <div className="flex gap-2 pt-1">
          {onUseSuggestion && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onUseSuggestion(suggestion.suggestion)}
              className="text-blue-700 border-blue-300 hover:bg-blue-50"
            >
              Use this suggestion
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={handleCopy}>
            {copied ? (
              <Check className="h-3 w-3 mr-1" />
            ) : (
              <Copy className="h-3 w-3 mr-1" />
            )}
            {copied ? "Copied" : "Copy"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
