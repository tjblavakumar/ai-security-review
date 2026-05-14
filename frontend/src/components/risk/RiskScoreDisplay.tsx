"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { AlertTriangle, Shield, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { RiskScore, RiskLevel } from "@/lib/types";

interface RiskScoreDisplayProps {
  submissionId: string | number;
  autoRefresh?: boolean;
  className?: string;
}

const getRiskColor = (level: RiskLevel | null): string => {
  switch (level) {
    case "low":
      return "bg-green-500";
    case "medium":
      return "bg-yellow-500";
    case "high":
      return "bg-orange-500";
    case "critical":
      return "bg-red-500";
    default:
      return "bg-gray-400";
  }
};

const getRiskBadgeVariant = (level: RiskLevel | null): "default" | "secondary" | "destructive" | "outline" => {
  switch (level) {
    case "low":
      return "secondary";
    case "medium":
      return "default";
    case "high":
    case "critical":
      return "destructive";
    default:
      return "outline";
  }
};

const getRiskIcon = (level: RiskLevel | null) => {
  if (level === "low") {
    return <Shield className="h-5 w-5 text-green-600" />;
  }
  return <AlertTriangle className="h-5 w-5 text-orange-600" />;
};

export default function RiskScoreDisplay({
  submissionId,
  autoRefresh = false,
  className = "",
}: RiskScoreDisplayProps) {
  const [riskData, setRiskData] = useState<RiskScore | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRiskScore = async () => {
    try {
      setError(null);
      const response = await api.get<RiskScore>(`/risk/submission/${submissionId}`);
      setRiskData(response.data);
    } catch (err) {
      console.error("Failed to fetch risk score:", err);
      setError("Unable to load risk score");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskScore();
  }, [submissionId]);

  // Auto-refresh every 3 seconds when enabled
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchRiskScore();
    }, 3000);

    return () => clearInterval(interval);
  }, [submissionId, autoRefresh]);

  if (loading) {
    return (
      <Card className={`${className} animate-pulse`}>
        <CardContent className="pt-6">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
        </CardContent>
      </Card>
    );
  }

  if (error || !riskData) {
    return (
      <Card className={`${className} border-gray-300`}>
        <CardContent className="pt-6">
          <p className="text-sm text-gray-500">
            {error || "Risk score not available"}
          </p>
        </CardContent>
      </Card>
    );
  }

  const { risk_score, risk_level, answered_questions, total_questions, risk_factors } = riskData;

  return (
    <Card className={`${className} sticky top-4 z-10 shadow-md border-2 ${
      risk_level === "critical" ? "border-red-300" :
      risk_level === "high" ? "border-orange-300" :
      risk_level === "medium" ? "border-yellow-300" :
      "border-green-300"
    }`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getRiskIcon(risk_level)}
            <div>
              <CardTitle className="text-lg">Risk Assessment</CardTitle>
              <p className="text-xs text-gray-500 mt-1">
                Based on {answered_questions} of {total_questions} questions answered
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right">
              <div className="text-2xl font-bold">
                {risk_score.toFixed(1)}
                <span className="text-sm text-gray-500 ml-1">/ 100</span>
              </div>
            </div>
            <Badge variant={getRiskBadgeVariant(risk_level)} className="text-sm">
              {risk_level?.toUpperCase() || "N/A"}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="relative h-3 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className={`h-full transition-all ${getRiskColor(risk_level)}`}
              style={{ width: `${risk_score}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>Low Risk</span>
            <span>Critical Risk</span>
          </div>
        </div>

        {/* Risk Factors */}
        {risk_factors && risk_factors.length > 0 && (
          <div className="border-t pt-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
              className="w-full justify-between p-2 h-auto"
            >
              <span className="text-sm font-medium">
                High Risk Factors ({risk_factors.length})
              </span>
              {expanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
            
            {expanded && (
              <div className="mt-3 space-y-2">
                {risk_factors.map((factor, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {factor.question}
                        </p>
                        <Badge variant="outline" className="text-xs mt-1">
                          {factor.category}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-red-600">
                          {factor.risk_value}/10
                        </div>
                        <div className="text-xs text-gray-500">
                          Weight: {factor.weight}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* No risk factors message */}
        {(!risk_factors || risk_factors.length === 0) && answered_questions > 0 && (
          <div className="text-center py-2 text-sm text-green-600">
            <Shield className="h-4 w-4 inline mr-1" />
            No high-risk factors identified
          </div>
        )}
      </CardContent>
    </Card>
  );
}
