"use client";

import React, { useEffect, useState } from "react";
import { User, Bell, Globe } from "lucide-react";
import { useTranslations } from "next-intl";

export default function SettingsPage() {
  const t = useTranslations("settings");
  const [locale, setLocale] = useState("en");

  useEffect(() => {
    // Read the NEXT_LOCALE cookie on mount
    const cookies = document.cookie.split("; ");
    const localeCookie = cookies.find((row) => row.startsWith("NEXT_LOCALE="));
    if (localeCookie) {
      setLocale(localeCookie.split("=")[1]);
    }
  }, []);

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = e.target.value;
    setLocale(newLocale);

    // Set cookie for persistence
    document.cookie = `NEXT_LOCALE=${newLocale}; path=/; max-age=31536000`;

    // Trigger full page reload to apply new locale
    window.location.reload();
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">{t("title")}</h1>
        <p className="text-slate-400 mt-1">{t("description")}</p>
      </div>

      <div className="space-y-6">
        {/* Language & Region */}
        <section className="rounded-2xl border border-slate-800/60 bg-[#0b0c0e]/80 p-6 backdrop-blur-md shadow-sm">
          <div className="flex items-center space-x-3 mb-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Globe className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-200">{t("languageAndRegion")}</h2>
              <p className="text-sm text-slate-500">{t("languageDescription")}</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl bg-slate-900/50 p-4 border border-slate-800/50">
            <div>
              <label htmlFor="language-select" className="block text-sm font-medium text-slate-300">
                {t("displayLanguage")}
              </label>
              <p className="text-xs text-slate-500 mt-0.5">{t("displayLanguageDesc")}</p>
            </div>
            <div className="relative">
              <select
                id="language-select"
                value={locale}
                onChange={handleLanguageChange}
                className="appearance-none rounded-xl border border-slate-700 bg-slate-800 px-4 py-2 pr-10 text-sm font-medium text-slate-200 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 cursor-pointer min-w-[160px] transition-colors"
              >
                <option value="en">{t("english")}</option>
                <option value="de">{t("german")}</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                <svg className="h-4 w-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>
        </section>

        {/* Profile Settings (Placeholder) */}
        <section className="rounded-2xl border border-slate-800/60 bg-[#0b0c0e]/80 p-6 backdrop-blur-md opacity-75 shadow-sm">
          <div className="flex items-center space-x-3 mb-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800 border border-slate-700 text-slate-400">
              <User className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-200">{t("profileSettings")}</h2>
              <p className="text-sm text-slate-500">{t("profileDescription")}</p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-800/50 border-dashed p-8 text-center bg-slate-900/20">
            <p className="text-slate-500 text-sm">{t("profileFuture")}</p>
          </div>
        </section>

        {/* Notifications (Placeholder) */}
        <section className="rounded-2xl border border-slate-800/60 bg-[#0b0c0e]/80 p-6 backdrop-blur-md opacity-75 shadow-sm">
          <div className="flex items-center space-x-3 mb-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800 border border-slate-700 text-slate-400">
              <Bell className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-200">{t("notifications")}</h2>
              <p className="text-sm text-slate-500">{t("notificationsDescription")}</p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-800/50 border-dashed p-8 text-center bg-slate-900/20">
            <p className="text-slate-500 text-sm">{t("notificationsFuture")}</p>
          </div>
        </section>
      </div>
    </div>
  );
}
