"use client";

import React, { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { useTranslations } from "next-intl";
import {
  Printer,
  Layers,
  Activity,
  DollarSign,
  Play,
  Plus,
  ShoppingBag,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Cpu
} from "lucide-react";

// Mock fallbacks if backend is empty / not running
const MOCK_PRINTERS = [
  {
    id: "p1",
    name: "Bambu Lab X1-Carbon",
    status: "PRINTING",
    model: "X1C",
    jobName: "Organizer_Drawer_V2.3mf",
    progress: 74,
    timeLeft: "1h 14m",
    tempNozzle: 220,
    tempBed: 55,
    amsStatus: "Slot 1: PLA Green"
  },
  {
    id: "p2",
    name: "Bambu Lab P1S",
    status: "IDLE",
    model: "P1S",
    jobName: "-",
    progress: 0,
    timeLeft: "-",
    tempNozzle: 23,
    tempBed: 21,
    amsStatus: "Slot 2: PLA Black"
  },
  {
    id: "p3",
    name: "Bambu Lab A1 Mini",
    status: "OFFLINE",
    model: "A1M",
    jobName: "-",
    progress: 0,
    timeLeft: "-",
    tempNozzle: 0,
    tempBed: 0,
    amsStatus: "-"
  }
];

const MOCK_ACTIVITIES = [
  { id: 1, type: "spool", message: "New Draft Filament Spool detected via AMS (Auto-Discovery)", time: "10 minutes ago", tag: "Discovery" },
  { id: 2, type: "print", message: "Print project 'Speedy Benchy' completed on Bambu P1S", time: "2 hours ago", tag: "Print Job" },
  { id: 3, type: "order", message: "Joint Order #321 cost split calculated between 3 users", time: "1 day ago", tag: "Split Billing" },
  { id: 4, type: "spool", message: "User 'Edward' enriched Draft Filament spool (PLA Red, 19.99 €)", time: "2 days ago", tag: "Enrichment" }
];

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const [stats, setStats] = useState({
    activePrinters: 2,
    activeJobs: 1,
    filamentCount: 14,
    pendingSplitCosts: 48.75
  });

  const [printers, setPrinters] = useState(MOCK_PRINTERS);
  const [activities, setActivities] = useState(MOCK_ACTIVITIES);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRealData = async () => {
      try {
        // Try fetching filaments to see if backend is responsive
        const filRes = await apiClient.get("/filaments/");
        const projRes = await apiClient.get("/projects/");

        // Update stats if we receive successful responses
        setStats(prev => ({
          ...prev,
          filamentCount: filRes.data?.length || prev.filamentCount,
          activeJobs: projRes.data?.filter((p: any) => p.status === "PRINTING").length || prev.activeJobs
        }));
      } catch (err) {
        console.log(t("backendFallback"));
      }
    };

    fetchRealData();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">

      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            {t("title")}
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            {t("subtitle")}
          </p>
        </div>

        {/* Quick action buttons */}
        <div className="flex flex-wrap gap-3">
          <button className="flex items-center gap-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 px-4.5 py-2.5 text-xs font-semibold text-slate-200 hover:text-white transition-all cursor-pointer">
            <Plus className="h-4 w-4 text-emerald-400" />
            <span>{t("enrichSpool")}</span>
          </button>
          <button className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:brightness-110 px-4.5 py-2.5 text-xs font-bold text-slate-950 shadow-md shadow-emerald-500/10 transition-all cursor-pointer">
            <Play className="h-4 w-4 fill-slate-950 stroke-none" />
            <span>{t("newProject")}</span>
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

        {/* KPI 1 */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-6 backdrop-blur-xl shadow-lg">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-emerald-500/5 blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t("activeFleet")}</span>
            <div className="rounded-xl bg-emerald-500/10 p-2.5 text-emerald-400">
              <Printer className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline space-x-1.5">
              <span className="text-3xl font-extrabold text-white">{stats.activePrinters}</span>
              <span className="text-sm font-semibold text-slate-500">/ {printers.length} {t("online")}</span>
            </div>
            <p className="mt-1.5 flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
              <TrendingUp className="h-3.5 w-3.5" />
              <span>{t("telemetryUptime")}</span>
            </p>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-6 backdrop-blur-xl shadow-lg">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-cyan-500/5 blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t("currentJobs")}</span>
            <div className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-400">
              <Activity className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline space-x-1.5">
              <span className="text-3xl font-extrabold text-white">{stats.activeJobs}</span>
              <span className="text-sm font-semibold text-slate-500">{t("printing")}</span>
            </div>
            <p className="mt-1.5 flex items-center gap-1.5 text-xs text-slate-500">
              <span>{t("avgLoad")}</span>
            </p>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-6 backdrop-blur-xl shadow-lg">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-purple-500/5 blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t("filamentSpools")}</span>
            <div className="rounded-xl bg-purple-500/10 p-2.5 text-purple-400">
              <Layers className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline space-x-1.5">
              <span className="text-3xl font-extrabold text-white">{stats.filamentCount}</span>
              <span className="text-sm font-semibold text-slate-500">{t("available")}</span>
            </div>
            <p className="mt-1.5 flex items-center gap-1.5 text-xs text-purple-400 font-medium">
              <span>{t("draftsEnrichment")}</span>
            </p>
          </div>
        </div>

        {/* KPI 4 */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-6 backdrop-blur-xl shadow-lg">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-yellow-500/5 blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t("splitCosts")}</span>
            <div className="rounded-xl bg-yellow-500/10 p-2.5 text-yellow-400">
              <DollarSign className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline space-x-1.5">
              <span className="text-3xl font-extrabold text-white">{stats.pendingSplitCosts.toFixed(2)} €</span>
            </div>
            <p className="mt-1.5 flex items-center gap-1.5 text-xs text-slate-500">
              <span>{t("calcRecentOrders")}</span>
            </p>
          </div>
        </div>

      </div>

      {/* Main Grid: Telemetry & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Telemetry Panel */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-2xl border border-slate-900 bg-slate-950/20 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-2.5">
                <Cpu className="h-5 w-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-white">{t("liveTelemetry")}</h3>
              </div>
              <span className="text-xs text-slate-500">{t("updatesDynamic")}</span>
            </div>

            {/* Printers Loop */}
            <div className="space-y-4">
              {printers.map((printer) => (
                <div
                  key={printer.id}
                  className="rounded-xl border border-slate-900 bg-slate-950/60 p-5 transition-all hover:border-slate-800"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

                    {/* Printer Info */}
                    <div className="flex items-start space-x-4">
                      <div className={`rounded-xl p-2.5 ${
                        printer.status === "PRINTING"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : printer.status === "IDLE"
                          ? "bg-cyan-500/10 text-cyan-400"
                          : "bg-slate-900 text-slate-550"
                      }`}>
                        <Printer className="h-6 w-6" />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-200 text-base">{printer.name}</h4>
                        <div className="flex items-center space-x-2.5 mt-1">
                          <span className="text-xs font-semibold text-slate-500">{printer.model}</span>
                          <span className="h-1.5 w-1.5 rounded-full bg-slate-800"></span>
                          <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-2xs font-bold tracking-wide uppercase ${
                            printer.status === "PRINTING"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : printer.status === "IDLE"
                              ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                              : "bg-slate-900 text-slate-500 border border-slate-800"
                          }`}>
                            {printer.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Printer Temps (AMS status/etc.) */}
                    {printer.status !== "OFFLINE" && (
                      <div className="flex items-center gap-6 text-xs text-slate-400 sm:justify-end">
                        <div className="flex flex-col sm:items-end">
                          <span className="text-2xs font-semibold text-slate-550 uppercase tracking-wider">{t("nozzle")}</span>
                          <span className="font-semibold text-slate-200 mt-0.5">{printer.tempNozzle} °C</span>
                        </div>
                        <div className="flex flex-col sm:items-end">
                          <span className="text-2xs font-semibold text-slate-550 uppercase tracking-wider">{t("bed")}</span>
                          <span className="font-semibold text-slate-200 mt-0.5">{printer.tempBed} °C</span>
                        </div>
                        <div className="flex flex-col sm:items-end hidden sm:flex">
                          <span className="text-2xs font-semibold text-slate-550 uppercase tracking-wider">{t("activeSpool")}</span>
                          <span className="font-semibold text-emerald-400 mt-0.5">{printer.amsStatus}</span>
                        </div>
                      </div>
                    )}

                  </div>

                  {/* Printing Progress */}
                  {printer.status === "PRINTING" && (
                    <div className="mt-5 border-t border-slate-900/60 pt-4.5">
                      <div className="flex items-center justify-between text-xs font-medium mb-2">
                        <span className="text-slate-400 truncate max-w-[280px]">{t("job")} {printer.jobName}</span>
                        <span className="text-slate-500">{t("estRemaining")} <strong className="text-emerald-400 font-semibold">{printer.timeLeft}</strong></span>
                      </div>

                      {/* Bar indicator */}
                      <div className="flex items-center space-x-4">
                        <div className="h-2 flex-1 rounded-full bg-slate-900 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-500"
                            style={{ width: `${printer.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-extrabold text-white text-right w-10">{printer.progress}%</span>
                      </div>
                    </div>
                  )}

                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity Log */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-900 bg-slate-950/20 p-6 flex flex-col h-full justify-between">
            <div>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2.5">
                  <Activity className="h-5 w-5 text-cyan-400" />
                  <h3 className="text-lg font-bold text-white">{t("recentActivity")}</h3>
                </div>
              </div>

              {/* Activities Loop */}
              <div className="space-y-4">
                {activities.map((act) => (
                  <div key={act.id} className="flex gap-3">
                    <div className="mt-1 flex h-2 w-2 shrink-0 rounded-full bg-emerald-500"></div>
                    <div className="space-y-0.5">
                      <p className="text-xs text-slate-300 font-medium leading-relaxed">{act.message}</p>
                      <div className="flex items-center space-x-2 text-2xs font-semibold text-slate-550">
                        <span>{act.time}</span>
                        <span>•</span>
                        <span className="text-slate-500 uppercase tracking-wide">{act.tag}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* View Details link */}
            <div className="border-t border-slate-900/60 pt-4 mt-6">
              <a
                href="/dashboard/analytics"
                className="group flex items-center justify-between text-xs font-bold text-slate-400 hover:text-emerald-400 transition-colors"
              >
                <span>{t("viewAudits")}</span>
                <ChevronRight className="h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
              </a>
            </div>
          </div>

          {/* Quick Info Box */}
          <div className="rounded-2xl border border-slate-900 bg-gradient-to-tr from-slate-950/80 to-[#0e171b] p-6 shadow-md shadow-emerald-950/5 relative overflow-hidden">
            <div className="absolute -bottom-6 -right-6 h-24 w-24 rounded-full bg-emerald-500/5 blur-xl pointer-events-none"></div>
            <div className="flex items-center space-x-2 text-emerald-400 mb-2">
              <ShoppingBag className="h-5 w-5" />
              <h4 className="font-bold text-sm text-slate-200">{t("jointOrdering")}</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              {t("jointOrderingDesc")}
            </p>
            <a
              href="/dashboard/orders"
              className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 hover:bg-slate-850 px-3.5 py-2 text-2xs font-semibold text-emerald-400 border border-slate-800"
            >
              <span>{t("manageCart")}</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>

        </div>

      </div>

    </div>
  );
}
