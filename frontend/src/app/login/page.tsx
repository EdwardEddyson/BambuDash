"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { authApi } from "@/lib/api-client";
import { Lock, User, Mail, Printer, AlertCircle, Loader2 } from "lucide-react";

export default function LoginPage() {
  const t = useTranslations("login");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Form Fields
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      if (isLogin) {
        // Login flow
        const data = await authApi.login(username, password);
        localStorage.setItem("token", data.access_token);
        setSuccess(t("loginSuccess"));
        setTimeout(() => {
          router.push("/dashboard");
        }, 1000);
      } else {
        // Registration flow
        await authApi.register(username, email, fullName, password);
        setSuccess(t("registerSuccess"));
        // Auto-login after registration
        const loginData = await authApi.login(username, password);
        localStorage.setItem("token", loginData.access_token);
        setTimeout(() => {
          router.push("/dashboard");
        }, 1000);
      }
    } catch (err: any) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
        t("authFailed")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-[#0d0f12] px-4 py-12 text-slate-200 overflow-hidden">
      {/* Decorative background glows */}
      <div className="absolute top-1/4 left-1/4 -z-10 h-96 w-96 rounded-full bg-emerald-500/10 blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-96 w-96 rounded-full bg-cyan-500/10 blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-md space-y-8 z-10">
        {/* Header Branding */}
        <div className="flex flex-col items-center text-center space-y-3">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/20">
            <div className="flex h-full w-full items-center justify-center rounded-[14px] bg-[#0d0f12]">
              <Printer className="h-8 w-8 text-emerald-400 animate-pulse" />
            </div>
          </div>
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              {t("brandName")}
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              {t("subtitle")}
            </p>
          </div>
        </div>

        {/* Card Container */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-xl p-8 shadow-2xl shadow-black/40">
          {/* Tabs header */}
          <div className="mb-8 flex rounded-xl bg-slate-950 p-1 border border-slate-800/80">
            <button
              onClick={() => {
                setIsLogin(true);
                setError("");
                setSuccess("");
              }}
              className={`flex-1 rounded-lg py-2.5 text-sm font-semibold transition-all duration-200 ${
                isLogin
                  ? "bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-400 shadow border border-emerald-500/20"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t("signIn")}
            </button>
            <button
              onClick={() => {
                setIsLogin(false);
                setError("");
                setSuccess("");
              }}
              className={`flex-1 rounded-lg py-2.5 text-sm font-semibold transition-all duration-200 ${
                !isLogin
                  ? "bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-400 shadow border border-emerald-500/20"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t("register")}
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Error & Success Alert Area */}
            {error && (
              <div className="flex items-start space-x-2.5 rounded-xl border border-rose-500/20 bg-rose-500/10 p-3.5 text-sm text-rose-400">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
            {success && (
              <div className="flex items-start space-x-2.5 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3.5 text-sm text-emerald-400">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <span>{success}</span>
              </div>
            )}

            {/* Inputs */}
            {!isLogin && (
              <>
                <div className="space-y-1.5">
                  <label htmlFor="fullName" className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {t("fullName")}
                  </label>
                  <div className="relative rounded-xl border border-slate-800 bg-slate-950 transition-all focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/30">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                      <User className="h-5 w-5 text-slate-500" />
                    </div>
                    <input
                      id="fullName"
                      type="text"
                      required
                      placeholder={t("fullNamePlaceholder")}
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-transparent py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {t("emailAddress")}
                  </label>
                  <div className="relative rounded-xl border border-slate-800 bg-slate-950 transition-all focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/30">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                      <Mail className="h-5 w-5 text-slate-500" />
                    </div>
                    <input
                      id="email"
                      type="email"
                      required
                      placeholder={t("emailPlaceholder")}
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-transparent py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none"
                    />
                  </div>
                </div>
              </>
            )}

            <div className="space-y-1.5">
              <label htmlFor="username" className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {t("username")}
              </label>
              <div className="relative rounded-xl border border-slate-800 bg-slate-950 transition-all focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/30">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <User className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="username"
                  type="text"
                  required
                  placeholder={t("usernamePlaceholder")}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-transparent py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {t("authCodeText")}
              </label>
              <div className="relative rounded-xl border border-slate-800 bg-slate-950 transition-all focus-within:border-emerald-500/50 focus-within:ring-1 focus-within:ring-emerald-500/30">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Lock className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  placeholder={t("authCodePlaceholder")}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-transparent py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="relative mt-2 w-full select-none overflow-hidden rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 py-3 text-sm font-bold text-slate-950 shadow-md shadow-emerald-500/25 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
                  {tCommon("processing")}
                </span>
              ) : isLogin ? (
                t("signIn")
              ) : (
                t("createAccount")
              )}
            </button>
          </form>
        </div>

        {/* Demo Mode / Quick Sandbox Credentials */}
        <div className="text-center text-xs text-slate-600 bg-slate-900/10 p-4 border border-slate-850 rounded-xl">
          <p className="font-semibold text-slate-500 mb-1">{t("demoTitle")}</p>
          <p>{t("demoText")}</p>
        </div>
      </div>
    </div>
  );
}
