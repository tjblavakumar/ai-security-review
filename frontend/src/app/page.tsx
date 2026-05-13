import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, FileText, Settings } from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center gap-8 py-12">
      <div className="text-center max-w-2xl">
        <Shield className="h-16 w-16 text-blue-600 mx-auto mb-4" />
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI/GenAI Security Review
        </h1>
        <p className="text-lg text-gray-600">
          Submit your AI and Generative AI projects for information security
          review. Our structured questionnaire helps ensure your project meets
          security, privacy, and compliance requirements.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <FileText className="h-8 w-8 text-blue-600 mb-2" />
            <CardTitle>Start New Submission</CardTitle>
            <CardDescription>
              Begin the security review process for your AI/GenAI project.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/submit">
              <Button className="w-full">Start New Submission</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Settings className="h-8 w-8 text-gray-600 mb-2" />
            <CardTitle>Admin Panel</CardTitle>
            <CardDescription>
              Manage questions, review submissions, and configure the
              questionnaire.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/admin">
              <Button variant="outline" className="w-full">
                Admin Panel
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
