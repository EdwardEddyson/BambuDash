import React, { useState } from 'react';

export function ConsumptionForm({ onSubmit, onClose }: { onSubmit: (reqs: any[]) => void, onClose: () => void }) {
  const [reqs, setReqs] = useState([{ material_type: 'PLA', color_hex: '#000000', estimated_consumption_g: 50 }]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(reqs);
  };

  const updateReq = (index: number, field: string, value: any) => {
    const newReqs = [...reqs];
    newReqs[index] = { ...newReqs[index], [field]: value };
    setReqs(newReqs);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-[#0b0c0e] border border-slate-800 rounded-2xl shadow-2xl p-6">
        <h2 className="text-xl font-bold text-slate-200 mb-4">Filament Requirements</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {reqs.map((req, i) => (
            <div key={i} className="flex space-x-3 items-end">
              <div className="flex-1">
                <label className="block text-xs text-slate-400 mb-1">Material</label>
                <input type="text" value={req.material_type} onChange={e => updateReq(i, 'material_type', e.target.value)} className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-emerald-500" required />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Color</label>
                <div className="w-12 h-10 rounded-lg overflow-hidden border border-slate-800 focus-within:border-emerald-500 relative cursor-pointer">
                  <input type="color" value={req.color_hex} onChange={e => updateReq(i, 'color_hex', e.target.value)} className="w-[150%] h-[150%] -top-2 -left-2 absolute cursor-pointer" required />
                </div>
              </div>
              <div className="flex-1">
                <label className="block text-xs text-slate-400 mb-1">Weight (g)</label>
                <input type="number" value={req.estimated_consumption_g} onChange={e => updateReq(i, 'estimated_consumption_g', parseFloat(e.target.value))} className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-emerald-500" required min="1" />
              </div>
              {reqs.length > 1 && (
                <button type="button" onClick={() => setReqs(reqs.filter((_, idx) => idx !== i))} className="p-2.5 text-rose-500 hover:bg-slate-800 rounded-lg mb-0.5">✕</button>
              )}
            </div>
          ))}
          <button type="button" onClick={() => setReqs([...reqs, { material_type: 'PLA', color_hex: '#ffffff', estimated_consumption_g: 50 }])} className="text-sm font-medium text-emerald-500 hover:text-emerald-400">
            + Add another filament
          </button>

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-slate-200 font-medium">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-colors">
              Save Requirements
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
