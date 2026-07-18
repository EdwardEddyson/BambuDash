import React, { useState } from 'react';
import { makerworldApi } from '@/lib/api-client';
import { Search, Loader2 } from 'lucide-react';

export function MakerWorldSearchDialog({ onSelect, onClose }: { onSelect: (model: any) => void, onClose: () => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const data = await makerworldApi.search(query);
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-[#0b0c0e] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-200">Search MakerWorld</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white">&times;</button>
        </div>
        <div className="p-4 border-b border-slate-800">
          <form onSubmit={handleSearch} className="relative">
            <input
              type="text"
              placeholder="Search for models..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-slate-200 focus:outline-none focus:border-emerald-500"
            />
            <Search className="absolute left-3 top-3.5 h-5 w-5 text-slate-500" />
            <button type="submit" className="hidden" />
          </form>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="flex justify-center items-center py-10"><Loader2 className="h-8 w-8 animate-spin text-emerald-500"/></div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {results.map((r, i) => (
                <div key={i} onClick={() => onSelect(r)} className="cursor-pointer group relative rounded-xl overflow-hidden border border-slate-800 hover:border-emerald-500 transition-colors bg-slate-900">
                  <div className="aspect-square bg-slate-800 relative">
                    {r.image_url ? (
                      <img src={r.image_url} alt={r.title} className="object-cover w-full h-full opacity-80 group-hover:opacity-100 transition-opacity" />
                    ) : (
                      <div className="flex items-center justify-center h-full text-slate-600">No Image</div>
                    )}
                  </div>
                  <div className="p-3">
                    <h3 className="text-sm font-medium text-slate-300 truncate">{r.title}</h3>
                  </div>
                </div>
              ))}
              {!loading && results.length === 0 && query && (
                <div className="col-span-full text-center text-slate-500 py-10">No results found</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
