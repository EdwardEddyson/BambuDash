import React, { useEffect, useState } from 'react';
import { projectsApi } from '@/lib/api-client';
import { ProjectCard } from './ProjectCard';
import { MakerWorldSearchDialog } from './MakerWorldSearchDialog';
import { ConsumptionForm } from './ConsumptionForm';
import { Plus, Loader2 } from 'lucide-react';

const COLUMNS = [
  { id: 'idea', label: 'Idea', color: 'border-slate-700' },
  { id: 'planned', label: 'Planned', color: 'border-blue-500/50' },
  { id: 'printing', label: 'Printing', color: 'border-amber-500/50' },
  { id: 'completed', label: 'Completed', color: 'border-emerald-500/50' },
  { id: 'archived', label: 'Archived', color: 'border-slate-800' }
];

export function KanbanBoard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [showSearch, setShowSearch] = useState(false);
  const [showConsumption, setShowConsumption] = useState(false);
  const [selectedModel, setSelectedModel] = useState<any>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const data = await projectsApi.getAll();
      setProjects(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (e: React.DragEvent, id: number) => {
    e.dataTransfer.setData('projectId', id.toString());
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent, status: string) => {
    e.preventDefault();
    const projectId = parseInt(e.dataTransfer.getData('projectId'), 10);

    // Optimistic UI update
    setProjects(prev => prev.map(p => p.id === projectId ? { ...p, status } : p));

    try {
      await projectsApi.update(projectId, { status });
    } catch (err) {
      console.error(err);
      // Revert on failure
      fetchProjects();
    }
  };

  const handleModelSelect = (model: any) => {
    setSelectedModel(model);
    setShowSearch(false);
    setShowConsumption(true);
  };

  const handleConsumptionSubmit = async (reqs: any[]) => {
    if (!selectedModel) return;
    try {
      const projectData = {
        name: selectedModel.title,
        description: `Imported from MakerWorld: ${selectedModel.url}`,
        status: 'idea',
        image_stl_url: selectedModel.image_url
      };
      const newProject = await projectsApi.create(projectData);

      // Add requirements
      for (const req of reqs) {
        await projectsApi.addRequirement(newProject.id, req);
      }

      setShowConsumption(false);
      setSelectedModel(null);
      fetchProjects();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Project Board</h1>
          <p className="text-sm text-slate-400 mt-1">Manage your print projects from idea to completion.</p>
        </div>
        <button
          onClick={() => setShowSearch(true)}
          className="flex items-center space-x-2 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white px-4 py-2 rounded-xl font-medium shadow-lg shadow-emerald-500/20 transition-all"
        >
          <Plus className="h-4 w-4" />
          <span>New Project</span>
        </button>
      </div>

      <div className="flex-1 flex space-x-6 overflow-x-auto pb-4">
        {COLUMNS.map(column => {
          const columnProjects = projects.filter(p => p.status === column.id);

          return (
            <div
              key={column.id}
              className="flex-shrink-0 w-80 flex flex-col bg-[#0b0c0e]/50 border border-slate-800/50 rounded-2xl overflow-hidden"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, column.id)}
            >
              <div className={`p-4 border-b ${column.color} border-b-2 bg-[#0b0c0e] flex items-center justify-between`}>
                <h2 className="font-semibold text-slate-300">{column.label}</h2>
                <span className="bg-slate-800 text-slate-400 text-xs font-bold px-2 py-1 rounded-md">
                  {columnProjects.length}
                </span>
              </div>

              <div className="flex-1 p-3 overflow-y-auto space-y-3">
                {columnProjects.map(project => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    onDragStart={handleDragStart}
                  />
                ))}
                {columnProjects.length === 0 && (
                  <div className="h-full flex items-center justify-center border-2 border-dashed border-slate-800 rounded-xl">
                    <span className="text-slate-600 text-sm font-medium">Drop projects here</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {showSearch && (
        <MakerWorldSearchDialog
          onClose={() => setShowSearch(false)}
          onSelect={handleModelSelect}
        />
      )}

      {showConsumption && (
        <ConsumptionForm
          onClose={() => {
            setShowConsumption(false);
            setSelectedModel(null);
          }}
          onSubmit={handleConsumptionSubmit}
        />
      )}
    </div>
  );
}
