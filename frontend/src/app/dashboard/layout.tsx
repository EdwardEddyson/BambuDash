"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { authApi } from "@/lib/api-client";
import {
  Printer,
  LayoutDashboard,
  Layers,
  Trello,
  ShoppingBag,
  BarChart3,
  Settings,
  LogOut,
  User,
  Bell,
  Search,
  Menu,
  X,
  CheckCircle2
} from "lucide-react";

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
}

const navigation: SidebarItem[] = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Filament Inventory", href: "/dashboard/inventory", icon: Layers },
  { name: "Project Board", href: "/dashboard/projects", icon: Trello },
  { name: "Orders & Cart", href: "/dashboard/orders", icon: ShoppingBag },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        router.replace("/login");
        return;
      }
      try {
        const userData = await authApi.me();
        setCurrentUser(userData);
      } catch (err) {
        console.error("Failed to load user session, redirecting to login:", err);
        localStorage.removeItem("token");
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0d0f12] text-slate-200">
        <div className="flex flex-col items-center space-y-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
          <p className="text-slate-400 font-medium">Restoring secure session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#0d0f12] text-slate-100 overflow-hidden font-sans">

      {/* Mobile Sidebar overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
        ></div>
      )}

      {/* Sidebar Navigation */}
      <aside className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-900 bg-[#0b0c0e]/95 backdrop-blur-md transition-transform duration-300 ease-in-out lg:translate-x-0 ${
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      } lg:static lg:z-auto`}>
        {/* Sidebar Header / Brand */}
        <div className="flex h-20 items-center justify-between px-6 border-b border-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/10">
              <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#0b0c0e]">
                <Printer className="h-5 w-5 text-emerald-400" />
              </div>
            </div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-350 bg-clip-text text-transparent">
              BambuDash
            </span>
          </div>
          {/* Close button on mobile */}
          <button
            onClick={() => setSidebarOpen(false)}
            className="rounded-lg p-1.5 hover:bg-slate-900 lg:hidden text-slate-400"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Sidebar Navigation Items */}
        <nav className="flex-1 space-y-1.5 px-4 py-6 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <a
                key={item.name}
                href={item.href}
                className={`group flex items-center space-x-3.5 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? "bg-gradient-to-r from-emerald-500/10 to-cyan-500/5 text-emerald-400 border border-emerald-500/15"
                    : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200 border border-transparent"
                }`}
              >
                <Icon className={`h-5 w-5 shrink-0 transition-colors duration-250 ${
                  isActive ? "text-emerald-400" : "text-slate-500 group-hover:text-slate-300"
                }`} />
                <span>{item.name}</span>
              </a>
            );
          })}
        </nav>

        {/* User profile footer */}
        <div className="border-t border-slate-900/60 p-4 bg-[#090a0b]/60">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 max-w-[180px]">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
                <User className="h-5 w-5" />
              </div>
              <div className="overflow-hidden">
                <p className="text-sm font-semibold text-slate-250 truncate">
                  {currentUser?.full_name || currentUser?.username || "Guest User"}
                </p>
                <p className="text-xs text-slate-500 truncate">
                  {currentUser?.email || "User Account"}
                </p>
              </div>
            </div>
            {/* Logout Trigger */}
            <button
              onClick={handleLogout}
              className="rounded-lg p-2 text-slate-500 hover:bg-rose-500/10 hover:text-rose-400 transition-colors"
              title="Sign Out"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <div className="flex flex-1 flex-col overflow-hidden">

        {/* Top Header */}
        <header className="flex h-20 items-center justify-between border-b border-slate-900 px-6 lg:px-8 bg-[#0c0d10]/40 backdrop-blur-md">
          {/* Burger menu trigger on mobile */}
          <div className="flex items-center space-x-4 lg:space-x-0">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-xl border border-slate-850 p-2 text-slate-400 hover:bg-slate-900 lg:hidden"
            >
              <Menu className="h-6 w-6" />
            </button>

            {/* Quick search input */}
            <div className="relative hidden sm:block w-72">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                <Search className="h-4.5 w-4.5 text-slate-500" />
              </div>
              <input
                type="text"
                placeholder="Search models, projects..."
                className="w-full rounded-xl border border-slate-900 bg-slate-950/60 py-2 pl-10 pr-4 text-xs text-slate-200 placeholder-slate-600 outline-none focus:border-emerald-500/50 transition-colors"
              />
            </div>
          </div>

          {/* Quick Info & Notifications */}
          <div className="flex items-center space-x-4">

            {/* MQTT Live Connection Indicator */}
            <div className="flex items-center space-x-2 rounded-full border border-slate-900 bg-emerald-500/5 px-3.5 py-1.5 text-xs font-semibold text-emerald-400 shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
              </span>
              <span className="hidden sm:inline">MQTT: Connected</span>
            </div>

            {/* Notification trigger */}
            <button className="relative rounded-xl border border-slate-900 p-2.5 text-slate-400 hover:bg-slate-900 hover:text-slate-250 transition-colors">
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-cyan-500"></span>
            </button>

            {/* Separator */}
            <div className="h-6 w-[1px] bg-slate-850"></div>

            {/* Workspace status */}
            <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span>Fleet Online</span>
            </div>
          </div>
        </header>

        {/* Content Injector */}
        <main className="flex-1 overflow-y-auto bg-[#0d0f12] p-6 lg:p-8">
          {children}
        </main>
      </div>

    </div>
  );
}
