"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
  Plus,
  Pencil,
  Trash2,
  RefreshCw,
  Database,
  FileText,
  Search,
  Upload,
} from "lucide-react";
import type { PolicyDocument, RAGSearchResult } from "@/lib/types";

interface PolicyForm {
  title: string;
  content: string;
  version: string;
  tags: string;
}

const emptyForm: PolicyForm = { title: "", content: "", version: "", tags: "" };

export default function PolicyDocumentsPage() {
  const [policies, setPolicies] = useState<PolicyDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<PolicyForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [indexing, setIndexing] = useState<number | null>(null);
  const [uploadTab, setUploadTab] = useState<"file" | "text">("file");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Search
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<RAGSearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const res = await api.get<PolicyDocument[]>("/policies");
      setPolicies(res.data);
    } catch {
      toast.error("Failed to load policies");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setSelectedFile(null);
    setUploadTab("file");
    setDialogOpen(true);
  };

  const openEdit = (doc: PolicyDocument) => {
    setEditingId(doc.id);
    setForm({
      title: doc.title,
      content: doc.content || "",
      version: doc.version || "",
      tags: doc.tags.join(", "),
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    // File upload mode
    if (!editingId && uploadTab === "file") {
      if (!selectedFile) {
        toast.error("Please select a file");
        return;
      }
      await handleFileUpload();
      return;
    }

    // Manual text mode
    if (!form.title.trim()) {
      toast.error("Title is required");
      return;
    }
    setSaving(true);
    const body = {
      title: form.title,
      content: form.content || null,
      version: form.version || null,
      is_active: true,
      tags: form.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    };
    try {
      if (editingId) {
        await api.put(`/policies/${editingId}`, body);
        toast.success("Policy updated");
      } else {
        await api.post("/policies", body);
        toast.success("Policy created and indexed");
      }
      setDialogOpen(false);
      fetchPolicies();
    } catch {
      toast.error("Failed to save policy");
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setSaving(true);
    const formData = new FormData();
    formData.append("file", selectedFile);
    if (form.title) formData.append("title", form.title);
    if (form.version) formData.append("version", form.version);
    if (form.tags) formData.append("tags", form.tags);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/policies/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Upload failed");
      }

      const result = await res.json();
      toast.success(result.message || "File uploaded and indexed");
      setDialogOpen(false);
      setSelectedFile(null);
      fetchPolicies();
    } catch (error: any) {
      toast.error(error.message || "Failed to upload file");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this policy document? This cannot be undone.")) return;
    try {
      await api.delete(`/policies/${id}`);
      toast.success("Policy deleted");
      fetchPolicies();
    } catch {
      toast.error("Failed to delete");
    }
  };

  const handleReindex = async (id: number) => {
    setIndexing(id);
    try {
      const res = await api.post<{ chunks_indexed: number }>(
        `/policies/${id}/index`
      );
      toast.success(`Indexed ${res.data.chunks_indexed} chunks`);
      fetchPolicies();
    } catch {
      toast.error("Indexing failed — ensure OPENAI_API_KEY is set");
    } finally {
      setIndexing(null);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.post<RAGSearchResult[]>("/policies/search", {
        query: searchQuery,
        top_k: 5,
      });
      setSearchResults(res.data);
    } catch {
      toast.error("Search failed — ensure documents are indexed");
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Policy Documents</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate}>
              <Plus className="h-4 w-4 mr-1" />
              Add Document
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingId ? "Edit Policy Document" : "Add Policy Document"}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              {!editingId && (
                <Tabs value={uploadTab} onValueChange={(v) => setUploadTab(v as "file" | "text")}>
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="file">
                      <Upload className="h-4 w-4 mr-2" />
                      Upload File
                    </TabsTrigger>
                    <TabsTrigger value="text">
                      <FileText className="h-4 w-4 mr-2" />
                      Manual Entry
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="file" className="space-y-4">
                    <div>
                      <Label>Upload PDF or Text File *</Label>
                      <Input
                        type="file"
                        accept=".pdf,.txt,.md"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            setSelectedFile(file);
                            // Auto-fill title from filename if empty
                            if (!form.title) {
                              const name = file.name.split('.').slice(0, -1).join('.');
                              setForm({ ...form, title: name });
                            }
                          }
                        }}
                        className="cursor-pointer"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Supported: PDF, TXT, MD • Content will be automatically extracted and indexed
                      </p>
                      {selectedFile && (
                        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-700">
                          ✓ Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                        </div>
                      )}
                    </div>
                    <div>
                      <Label>Title (optional)</Label>
                      <Input
                        value={form.title}
                        onChange={(e) => setForm({ ...form, title: e.target.value })}
                        placeholder="Leave empty to use filename"
                      />
                    </div>
                    <div>
                      <Label>Version (optional)</Label>
                      <Input
                        value={form.version}
                        onChange={(e) => setForm({ ...form, version: e.target.value })}
                        placeholder="e.g., 2.0"
                      />
                    </div>
                    <div>
                      <Label>Tags (optional, comma-separated)</Label>
                      <Input
                        value={form.tags}
                        onChange={(e) => setForm({ ...form, tags: e.target.value })}
                        placeholder="e.g., privacy, compliance, data-handling"
                      />
                    </div>
                  </TabsContent>

                  <TabsContent value="text" className="space-y-4">
                    <div>
                      <Label>Title *</Label>
                      <Input
                        value={form.title}
                        onChange={(e) => setForm({ ...form, title: e.target.value })}
                        placeholder="e.g., AI Governance Policy v2.0"
                      />
                    </div>
                    <div>
                      <Label>Version</Label>
                      <Input
                        value={form.version}
                        onChange={(e) => setForm({ ...form, version: e.target.value })}
                        placeholder="e.g., 2.0"
                      />
                    </div>
                    <div>
                      <Label>Tags (comma-separated)</Label>
                      <Input
                        value={form.tags}
                        onChange={(e) => setForm({ ...form, tags: e.target.value })}
                        placeholder="e.g., privacy, compliance, data-handling"
                      />
                    </div>
                    <div>
                      <Label>Content *</Label>
                      <Textarea
                        value={form.content}
                        onChange={(e) => setForm({ ...form, content: e.target.value })}
                        placeholder="Paste or type the full policy document content here..."
                        rows={15}
                        className="font-mono text-xs"
                      />
                      <p className="text-xs text-gray-400 mt-1">
                        The content will be chunked and embedded for RAG-powered AI suggestions.
                      </p>
                    </div>
                  </TabsContent>
                </Tabs>
              )}

              {editingId && (
                <>
                  <div>
                    <Label>Title *</Label>
                    <Input
                      value={form.title}
                      onChange={(e) => setForm({ ...form, title: e.target.value })}
                      placeholder="e.g., AI Governance Policy v2.0"
                    />
                  </div>
                  <div>
                    <Label>Version</Label>
                    <Input
                      value={form.version}
                      onChange={(e) => setForm({ ...form, version: e.target.value })}
                      placeholder="e.g., 2.0"
                    />
                  </div>
                  <div>
                    <Label>Tags (comma-separated)</Label>
                    <Input
                      value={form.tags}
                      onChange={(e) => setForm({ ...form, tags: e.target.value })}
                      placeholder="e.g., privacy, compliance, data-handling"
                    />
                  </div>
                  <div>
                    <Label>Content</Label>
                    <Textarea
                      value={form.content}
                      onChange={(e) => setForm({ ...form, content: e.target.value })}
                      placeholder="Paste or type the full policy document content here..."
                      rows={15}
                      className="font-mono text-xs"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      The content will be chunked and embedded for RAG-powered AI suggestions.
                    </p>
                  </div>
                </>
              )}
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "Saving..." : editingId ? "Update" : "Create & Index"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Search className="h-4 w-4" />
            RAG Search
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search indexed policies (e.g. 'PII handling requirements')..."
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={searching}>
              {searching ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                "Search"
              )}
            </Button>
          </div>
          {searchResults.length > 0 && (
            <div className="space-y-2">
              {searchResults.map((r, i) => (
                <div
                  key={i}
                  className="rounded-md border p-3 bg-gray-50 text-sm"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline">{r.document_title}</Badge>
                    <span className="text-xs text-gray-400">
                      Score: {r.score.toFixed(4)}
                    </span>
                  </div>
                  <p className="text-gray-700 whitespace-pre-wrap text-xs">
                    {r.chunk}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Policy list */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : policies.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No policy documents yet.</p>
            <p className="text-sm mt-1">
              Add policy documents so the AI assistant can reference them
              when suggesting answers.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {policies.map((doc) => (
            <Card key={doc.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium truncate">{doc.title}</h3>
                      {doc.version && (
                        <Badge variant="outline" className="text-xs">
                          v{doc.version}
                        </Badge>
                      )}
                      <Badge
                        variant={doc.is_active ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {doc.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {doc.tags.map((tag, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Database className="h-3 w-3" />
                        {doc.chunk_count} chunks indexed
                      </span>
                      <span>
                        {doc.content
                          ? `${doc.content.length.toLocaleString()} chars`
                          : "No content"}
                      </span>
                      <span>
                        Updated:{" "}
                        {new Date(doc.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1 ml-4 shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleReindex(doc.id)}
                      disabled={indexing === doc.id}
                      title="Re-index for RAG"
                    >
                      <RefreshCw
                        className={`h-4 w-4 ${
                          indexing === doc.id ? "animate-spin" : ""
                        }`}
                      />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEdit(doc)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
