"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle } from "lucide-react";

export default function ConfirmationPage() {
  const params = useParams();
  const submissionId = params.id as string;

  return (
    <div className="max-w-lg mx-auto py-12">
      <Card className="text-center">
        <CardHeader>
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <CardTitle className="text-2xl">Submission Sent for Review</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            Your security review submission has been successfully submitted.
            Your submission ID is:
          </p>
          <p className="text-lg font-mono font-bold text-blue-600">
            #{submissionId}
          </p>
          <p className="text-sm text-gray-500">
            You will receive a notification when a reviewer takes action on your
            submission.
          </p>
          <div className="flex gap-4 justify-center pt-4">
            <Link href="/my-submissions">
              <Button>View My Submissions</Button>
            </Link>
            <Link href="/">
              <Button variant="outline">Back to Home</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
