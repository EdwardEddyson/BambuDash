import React from 'react';
import { User, CheckCircle2, AlertCircle } from 'lucide-react';

export function ProjectCard({ project, onDragStart }: { project: any, onDragStart: (e: React.DragEvent, id: number) => void }) {
  const reqs = project.filament_requirements || [];

  // To strictly check if it's feasible, we would need the current filament inventory.
  // For the sake of UI right now, we assume if we have requirements, it might be feasible.
  // If no requirements are present, it's neutral.
  // In a full implementation, the board would pass down an `availableFilaments` prop.
  const isPrintable = reqs.length > 0; // Mocked feasibility
  const borderColor = isPrintable ? "border-emerald-500/50" : "border-slate-800";

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, project.id)}
      className={`bg-slate-900 border ${borderColor} rounded-xl p-3 shadow-md cursor-grab active:cursor-grabbing hover:shadow-lg hover:border-emerald-500/80 transition-all`}
    >
      {project.image_stl_url && (
        <div className="w-full h-32 rounded-lg overflow-hidden mb-3 bg-slate-800">
          <img src={project.image_stl_url} alt={project.name} className="w-full h-full object-cover" />
        </div>
      )}

      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-slate-200 leading-tight">{project.name}</h3>
        {isPrintable ? (
          <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
        ) : (
          <AlertCircle className="h-4 w-4 text-rose-500 shrink-0 mt-0.5" />
        )}
      </div>

      {project.description && (
        <p className="text-xs text-slate-400 mb-3 line-clamp-2">{project.description}</p>
      )}

      {reqs.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {reqs.map((req: any, i: number) => (
            <div key={i} className="flex items-center space-x-1.5 bg-slate-800/80 border border-emerald-500/30 rounded-full px-2 py-0.5">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: req.color_hex }}></span>
              <span className="text-[10px] font-medium text-emerald-400">
                {req.material_type} [{req.estimated_consumption_g}g]
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/80">
        <div className="flex items-center space-x-1.5">
          <div className="bg-slate-800 rounded-full p-1">
            <User className="h-3 w-3 text-slate-400" />
          </div>
          <span className="text-[10px] text-slate-500">Creator {project.creator_id}</span>
        </div>
        <span className="text-[10px] font-medium text-slate-500 bg-slate-800 px-2 py-0.5 rounded-md uppercase tracking-wider">
          {project.status}
        </span>
      </div>
    </div>
  );
}
