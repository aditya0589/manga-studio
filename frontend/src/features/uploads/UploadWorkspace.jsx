import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadsApi } from '../../api/uploads';
import { useStudioStore } from '../../stores/studioStore';
import { 
  UploadCloud, 
  FileText, 
  Trash2, 
  Eye, 
  CheckCircle2, 
  Loader2, 
  AlertCircle,
  FileCode,
  BookOpen
} from 'lucide-react';

export default function UploadWorkspace() {
  const { projectId } = useParams();
  const queryClient = useQueryClient();
  const { addNotification } = useStudioStore();

  const [selectedFile, setSelectedFile] = useState(null);
  const [docType, setDocType] = useState('manuscript');
  const [activeDoc, setActiveDoc] = useState(null);

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents', projectId],
    queryFn: () => uploadsApi.listDocuments(projectId),
    enabled: !!projectId,
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, type }) => uploadsApi.uploadDocument(projectId, file, type),
    onSuccess: (newDoc) => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] });
      addNotification(`Document "${newDoc.original_filename}" processed!`, 'success');
      setSelectedFile(null);
      setActiveDoc(newDoc);
    },
    onError: (err) => {
      addNotification(`Upload failed: ${err.message}`, 'error');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (docId) => uploadsApi.deleteDocument(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', projectId] });
      addNotification('Document deleted.', 'info');
      if (activeDoc && activeDoc.id) setActiveDoc(null);
    }
  });

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    uploadMutation.mutate({ file: selectedFile, type: docType });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white font-['Plus_Jakarta_Sans']">
          Manuscript & Asset Uploads
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload existing storylines, world lore, and character briefs in TXT, PDF, or DOCX formats
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Upload Form & Document List */}
        <div className="lg:col-span-5 space-y-6">
          {/* Upload Dropzone Box */}
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#23283a] shadow-lg">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-violet-400" />
              Upload Source Document
            </h3>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Document Purpose</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                >
                  <option value="manuscript">Story Manuscript / Script</option>
                  <option value="character_notes">Character Profiles & Relationships</option>
                  <option value="world_lore">Worldbuilding & Location Lore</option>
                </select>
              </div>

              <div className="border-2 border-dashed border-[#293042] hover:border-violet-500/50 rounded-xl p-6 text-center cursor-pointer transition-colors bg-[#0a0c12]/50 relative">
                <input
                  type="file"
                  accept=".txt,.pdf,.docx,.doc"
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <FileCode className="w-8 h-8 text-violet-400/80 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-200">
                  {selectedFile ? selectedFile.name : "Click or drag document to upload"}
                </p>
                <p className="text-[10px] text-slate-500 mt-1">Supports TXT, PDF, DOCX (Max 20MB)</p>
              </div>

              <button
                type="submit"
                disabled={!selectedFile || uploadMutation.isPending}
                className="w-full py-2.5 px-4 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md shadow-violet-900/30 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
              >
                {uploadMutation.isPending ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Extracting Text & Processing...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-3.5 h-3.5" />
                    <span>Upload & Extract Text</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Document List */}
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#23283a] shadow-lg">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center justify-between">
              <span>Project Documents ({documents.length})</span>
            </h3>

            {isLoading ? (
              <p className="text-xs text-slate-500 py-4">Loading documents...</p>
            ) : documents.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">No documents uploaded yet.</p>
            ) : (
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => setActiveDoc(doc)}
                    className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                      activeDoc?.id === doc.id
                        ? 'bg-violet-950/40 border-violet-600'
                        : 'bg-[#0a0c12] border-[#222736] hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-3 truncate">
                      <FileText className="w-4 h-4 text-violet-400 shrink-0" />
                      <div className="truncate">
                        <p className="text-xs font-semibold text-slate-200 truncate">{doc.original_filename}</p>
                        <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Extracted
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteMutation.mutate(doc.id);
                        }}
                        className="p-1.5 text-slate-500 hover:text-rose-400 rounded transition-colors"
                        title="Delete Document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Extracted Document Inspector */}
        <div className="lg:col-span-7">
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#23283a] shadow-lg flex flex-col min-h-[500px]">
            <div className="flex items-center justify-between pb-4 border-b border-[#212638] mb-4">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-violet-400" />
                <h3 className="text-sm font-semibold text-white">
                  {activeDoc ? activeDoc.original_filename : "Extracted Text Inspector"}
                </h3>
              </div>
              {activeDoc && (
                <span className="text-[11px] text-slate-500">
                  {activeDoc.extracted_text ? `${activeDoc.extracted_text.length} characters` : 'No text'}
                </span>
              )}
            </div>

            {activeDoc ? (
              <div className="flex-1 flex flex-col">
                <p className="text-xs text-slate-400 mb-2">
                  Review the extracted manuscript. This content is analyzed by the Story Ingestion Agent during canon formation.
                </p>
                <textarea
                  readOnly
                  value={activeDoc.extracted_text || "No text extracted from this document."}
                  className="flex-1 w-full min-h-[400px] p-4 rounded-xl bg-[#090b10] border border-[#242938] text-xs font-mono text-slate-200 focus:outline-none resize-none leading-relaxed"
                />
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
                <FileText className="w-10 h-10 mb-3 text-slate-600" />
                <p className="text-xs font-medium">Select a document from the list to preview extracted text</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
