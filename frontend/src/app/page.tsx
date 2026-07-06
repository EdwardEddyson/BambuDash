import React from "react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-[#0d0f12] text-white">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-sm flex flex-col space-y-6">
        <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
          BambuDash
        </h1>
        <p className="text-xl text-slate-400 max-w-lg text-center">
          The ultimate 3D print fleet management and split-billing order workspace for Bambu Lab printers.
        </p>
        <div className="flex space-x-4">
          <span className="px-6 py-3 bg-slate-800 hover:bg-slate-700 transition rounded-xl font-medium cursor-pointer border border-slate-700">
            Frontend Boilerplate Ready
          </span>
        </div>
      </div>
    </main>
  );
}
