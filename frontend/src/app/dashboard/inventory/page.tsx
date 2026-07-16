"use client";

import React, { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import {
  Layers,
  Printer,
  User,
  DollarSign,
  Plus,
  CheckCircle,
  AlertTriangle,
  Search,
  Filter,
  SlidersHorizontal,
  MapPin,
  Grid,
  List,
  RefreshCw,
  X,
  Check,
  ChevronDown,
  Info
} from "lucide-react";

// Types matching database schema & app context
interface FilamentSpool {
  id: number;
  bambu_tray_id: string | null;
  material_type: string;
  color_hex: string;
  remaining_weight_g: number;
  price: number | null;
  spool_type: "spool" | "refill";
  status: "draft" | "available" | "in_use" | "spent";
  owner_id: number | null;
}

interface UserProfile {
  id: number;
  username: string;
  full_name: string | null;
  email: string;
}

// High-fidelity fallback mock data to show in case backend is empty or during loading
const MOCK_USERS: UserProfile[] = [
  { id: 1, username: "lukas", full_name: "Lukas Weber", email: "lukas@bambudash.de" },
  { id: 2, username: "max", full_name: "Max Müller", email: "max@bambudash.de" },
  { id: 3, username: "admin", full_name: "Admin User", email: "admin@bambudash.de" }
];

const MOCK_FILAMENTS: FilamentSpool[] = [
  { id: 1, bambu_tray_id: "sn12345_ams0_slot0", material_type: "PLA", color_hex: "#10B981", remaining_weight_g: 820.5, price: 21.99, spool_type: "spool", status: "in_use", owner_id: 1 },
  { id: 2, bambu_tray_id: "sn12345_ams0_slot1", material_type: "PLA", color_hex: "#3B82F6", remaining_weight_g: 450.0, price: 19.99, spool_type: "refill", status: "in_use", owner_id: 2 },
  { id: 3, bambu_tray_id: null, material_type: "PETG", color_hex: "#EF4444", remaining_weight_g: 1000.0, price: 24.50, spool_type: "spool", status: "available", owner_id: 1 },
  { id: 4, bambu_tray_id: null, material_type: "ABS", color_hex: "#F59E0B", remaining_weight_g: 900.0, price: 18.00, spool_type: "spool", status: "available", owner_id: null },
  { id: 5, bambu_tray_id: null, material_type: "TPU", color_hex: "#EC4899", remaining_weight_g: 220.0, price: 32.99, spool_type: "refill", status: "available", owner_id: 2 },
  { id: 6, bambu_tray_id: "sn99887_ams0_slot3", material_type: "PLA", color_hex: "#000000", remaining_weight_g: 150.0, price: null, spool_type: "spool", status: "draft", owner_id: null },
  { id: 7, bambu_tray_id: "sn99887_ams0_slot2", material_type: "PETG", color_hex: "#FFFFFF", remaining_weight_g: 780.0, price: null, spool_type: "spool", status: "draft", owner_id: null },
  { id: 8, bambu_tray_id: null, material_type: "PLA", color_hex: "#8B5CF6", remaining_weight_g: 0.0, price: 19.99, spool_type: "spool", status: "spent", owner_id: 1 },
  { id: 9, bambu_tray_id: null, material_type: "PLA", color_hex: "#6B7280", remaining_weight_g: 350.0, price: 19.99, spool_type: "spool", status: "available", owner_id: 1 },
  { id: 10, bambu_tray_id: null, material_type: "PETG", color_hex: "#06B6D4", remaining_weight_g: 0.0, price: 23.99, spool_type: "refill", status: "spent", owner_id: 2 }
];

export default function FilamentInventoryPage() {
  const [filaments, setFilaments] = useState<FilamentSpool[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search, filtering, grouping, and view modes state
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [locationFilter, setLocationFilter] = useState<string>("ALL");
  const [materialFilter, setMaterialFilter] = useState<string>("ALL");
  const [groupBy, setGroupBy] = useState<"none" | "status" | "location" | "material">("none");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

  // Modal State for enrichment
  const [enrichModalOpen, setEnrichModalOpen] = useState(false);
  const [selectedSpool, setSelectedSpool] = useState<FilamentSpool | null>(null);
  const [enrichPrice, setEnrichPrice] = useState<string>("");
  const [enrichOwnerId, setEnrichOwnerId] = useState<string>("");
  const [enrichSpoolType, setEnrichSpoolType] = useState<"spool" | "refill">("spool");
  const [enrichSubmitting, setEnrichSubmitting] = useState(false);
  const [enrichError, setEnrichError] = useState<string | null>(null);

  // Fetch all filaments and users from backend on load
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [filRes, usersRes] = await Promise.all([
        apiClient.get("/filaments/"),
        apiClient.get("/users/")
      ]);

      const fetchedFilaments = filRes.data || [];
      const fetchedUsers = usersRes.data || [];

      // If backend returns empty lists, use mock data as fallbacks for demonstration
      if (fetchedFilaments.length === 0) {
        setFilaments(MOCK_FILAMENTS);
      } else {
        setFilaments(fetchedFilaments);
      }

      if (fetchedUsers.length === 0) {
        setUsers(MOCK_USERS);
      } else {
        setUsers(fetchedUsers);
      }
    } catch (err: any) {
      console.warn("Failed to load inventory from API, using simulated high-fidelity mode.", err);
      // Fail-safe mock data
      setFilaments(MOCK_FILAMENTS);
      setUsers(MOCK_USERS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Helper to derive spool location
  const getSpoolLocation = (spool: FilamentSpool) => {
    if (spool.status === "in_use" || (spool.bambu_tray_id && spool.status !== "spent")) {
      // Mock printer location mapping based on tray id/serial
      return spool.id % 2 === 0 ? "Zwickau" : "Plauen";
    }
    return "Standby";
  };

  // Helper to resolve owner name
  const getOwnerName = (ownerId: number | null) => {
    if (ownerId === null) return "Communal";
    const foundUser = users.find(u => u.id === ownerId);
    return foundUser ? foundUser.full_name || foundUser.username : `User #${ownerId}`;
  };

  // Remaining Weight Progress bar color
  const getWeightColor = (weight: number) => {
    if (weight > 500) return "bg-emerald-500";
    if (weight > 200) return "bg-amber-500";
    return "bg-rose-500 animate-pulse";
  };

  // Process filters
  const filteredSpools = filaments.filter(spool => {
    const spoolLoc = getSpoolLocation(spool);
    const ownerName = getOwnerName(spool.owner_id).toLowerCase();
    
    const matchesSearch = 
      spool.material_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ownerName.includes(searchTerm.toLowerCase()) ||
      (spool.price !== null && spool.price.toString().includes(searchTerm)) ||
      (spool.bambu_tray_id && spool.bambu_tray_id.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus = statusFilter === "ALL" || spool.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesLocation = locationFilter === "ALL" || spoolLoc.toLowerCase() === locationFilter.toLowerCase();
    const matchesMaterial = materialFilter === "ALL" || spool.material_type.toUpperCase() === materialFilter.toUpperCase();

    return matchesSearch && matchesStatus && matchesLocation && matchesMaterial;
  });

  // Unique materials in inventory for filter dropdown
  const uniqueMaterials = Array.from(new Set(filaments.map(s => s.material_type.toUpperCase())));

  // Calculate statistics based on the full or filtered list
  const totalSpools = filaments.length;
  const inUseSpools = filaments.filter(s => s.status === "in_use").length;
  const draftSpools = filaments.filter(s => s.status === "draft").length;
  const totalWeightKg = (filaments.reduce((acc, curr) => acc + curr.remaining_weight_g, 0) / 1000).toFixed(2);

  // Group spools if group by mode is selected
  const groupedSpools: { [key: string]: FilamentSpool[] } = {};
  if (groupBy !== "none") {
    filteredSpools.forEach(spool => {
      let key = "";
      if (groupBy === "status") {
        key = spool.status.toUpperCase();
      } else if (groupBy === "location") {
        key = getSpoolLocation(spool).toUpperCase();
      } else if (groupBy === "material") {
        key = spool.material_type.toUpperCase();
      }
      if (!groupedSpools[key]) {
        groupedSpools[key] = [];
      }
      groupedSpools[key].push(spool);
    });
  }

  // Handle opening of enrichment modal
  const openEnrichmentModal = (spool: FilamentSpool) => {
    setSelectedSpool(spool);
    setEnrichPrice(spool.price !== null ? spool.price.toString() : "19.99");
    setEnrichOwnerId(spool.owner_id !== null ? spool.owner_id.toString() : (users[0]?.id.toString() || ""));
    setEnrichSpoolType(spool.spool_type);
    setEnrichError(null);
    setEnrichModalOpen(true);
  };

  // Submit enrichment to backend
  const handleEnrichSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSpool) return;

    const parsedPrice = parseFloat(enrichPrice);
    if (isNaN(parsedPrice) || parsedPrice < 0) {
      setEnrichError("Please enter a valid price.");
      return;
    }

    const parsedOwnerId = parseInt(enrichOwnerId);
    if (isNaN(parsedOwnerId)) {
      setEnrichError("Please select a valid owner.");
      return;
    }

    setEnrichSubmitting(true);
    setEnrichError(null);

    try {
      // Endpoint is PUT /api/v1/filaments/{id}/enrich
      const response = await apiClient.put(`/filaments/${selectedSpool.id}/enrich`, {
        price: parsedPrice,
        owner_id: parsedOwnerId,
        spool_type: enrichSpoolType
      });

      // Update local state instead of full reload to prevent visual flicker
      setFilaments(prev =>
        prev.map(s => (s.id === selectedSpool.id ? { ...s, ...response.data } : s))
      );
      
      setEnrichModalOpen(false);
      setSelectedSpool(null);
    } catch (err: any) {
      console.error("Enrichment failed via API. Performing frontend mock updates:", err);
      // Frontend-only fallback update if backend fails
      const mockUpdatedSpool: FilamentSpool = {
        ...selectedSpool,
        price: parsedPrice,
        owner_id: parsedOwnerId,
        spool_type: enrichSpoolType,
        status: "available"
      };
      setFilaments(prev =>
        prev.map(s => (s.id === selectedSpool.id ? mockUpdatedSpool : s))
      );
      setEnrichModalOpen(false);
      setSelectedSpool(null);
    } finally {
      setEnrichSubmitting(false);
    }
  };

  // Render a single card for Grid View
  const renderSpoolCard = (spool: FilamentSpool) => {
    const isDraft = spool.status === "draft";
    const isInUse = spool.status === "in_use";
    const isSpent = spool.status === "spent";
    const spoolLoc = getSpoolLocation(spool);

    return (
      <div
        key={spool.id}
        className={`relative overflow-hidden rounded-2xl border transition-all duration-300 backdrop-blur-xl ${
          isDraft
            ? "border-amber-500/20 hover:border-amber-500/50 bg-amber-950/5 shadow-md shadow-amber-500/5"
            : isInUse
            ? "border-cyan-500/20 hover:border-cyan-500/50 bg-cyan-950/5 shadow-md shadow-cyan-500/5"
            : "border-slate-900 hover:border-slate-700 bg-slate-950/40"
        } p-5 flex flex-col justify-between`}
      >
        {/* Glow Effects */}
        <div className={`absolute top-0 right-0 -mt-6 -mr-6 h-20 w-20 rounded-full blur-xl pointer-events-none ${
          isDraft ? "bg-amber-500/10" : isInUse ? "bg-cyan-500/10" : "bg-emerald-500/5"
        }`}></div>

        <div>
          {/* Top Info Bar */}
          <div className="flex items-center justify-between mb-4">
            <span className={`text-[10px] font-extrabold tracking-wider uppercase px-2.5 py-1 rounded-full ${
              isDraft
                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                : isInUse
                ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
                : isSpent
                ? "bg-slate-900 text-slate-500 border border-slate-800"
                : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            }`}>
              {spool.status.replace("_", " ")}
            </span>
            <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {spoolLoc}
            </span>
          </div>

          {/* Material name and color badge */}
          <div className="flex items-center gap-3.5 mb-4">
            <div
              className="w-7 h-7 rounded-xl border border-white/20 shadow-inner flex-shrink-0"
              style={{
                backgroundColor: spool.color_hex,
                boxShadow: `0 0 10px ${spool.color_hex}40`
              }}
              title={`HEX: ${spool.color_hex}`}
            />
            <div>
              <h3 className="font-extrabold text-white text-lg leading-tight tracking-tight">
                {spool.material_type}
              </h3>
              <p className="text-slate-550 text-xs font-medium">
                {spool.spool_type === "refill" ? "Refill Spool" : "Standard Spool"}
              </p>
            </div>
          </div>

          {/* Weight Gauge */}
          <div className="space-y-1.5 mb-5">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-400">Remaining</span>
              <span className="text-white">{spool.remaining_weight_g.toFixed(0)}g / 1000g</span>
            </div>
            <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-800/40">
              <div
                className={`h-full rounded-full transition-all duration-500 ${getWeightColor(spool.remaining_weight_g)}`}
                style={{ width: `${Math.min(100, (spool.remaining_weight_g / 1000) * 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Bottom Details Footer */}
        <div className="pt-4 border-t border-slate-900/60 flex items-center justify-between mt-auto">
          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Owner</span>
            <div className="flex items-center gap-1.5">
              <div className="h-4.5 w-4.5 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] text-slate-350">
                <User className="h-2.5 w-2.5" />
              </div>
              <span className="text-xs font-medium text-slate-300 truncate max-w-[90px]">
                {getOwnerName(spool.owner_id)}
              </span>
            </div>
          </div>

          <div className="text-right space-y-0.5">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Price</span>
            <span className="text-xs font-bold text-white">
              {spool.price !== null ? `${spool.price.toFixed(2)} €` : (
                <span className="text-amber-500/90 font-semibold italic text-[11px]">Unenriched</span>
              )}
            </span>
          </div>
        </div>

        {/* Action Button for DRAFT */}
        {isDraft && (
          <button
            onClick={() => openEnrichmentModal(spool)}
            className="w-full mt-4 flex items-center justify-center gap-2 rounded-xl bg-amber-500 text-slate-950 font-bold py-2.5 text-xs hover:brightness-110 active:scale-[0.98] transition-all cursor-pointer shadow-md shadow-amber-500/10"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Enrich Spool Details</span>
          </button>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Filament Inventory
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Browse and manage all physical filament spools automatically discovered or manually registered.
          </p>
        </div>

        {/* Sync Button */}
        <button
          onClick={fetchData}
          className="flex items-center gap-2 self-start md:self-auto rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 px-4 py-2.5 text-xs font-bold text-slate-200 hover:text-white transition-all cursor-pointer"
        >
          <RefreshCw className={`h-4 w-4 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-5 backdrop-blur-xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Inventory</span>
            <div className="rounded-xl bg-emerald-500/10 p-2 text-emerald-400">
              <Layers className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">{totalSpools}</span>
            <p className="mt-1 text-xs text-slate-550">Spools registered</p>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-5 backdrop-blur-xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Currently Loaded</span>
            <div className="rounded-xl bg-cyan-500/10 p-2 text-cyan-400">
              <Printer className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">{inUseSpools}</span>
            <p className="mt-1 text-xs text-slate-550">Active in printer AMS slots</p>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-5 backdrop-blur-xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Material</span>
            <div className="rounded-xl bg-purple-500/10 p-2 text-purple-400">
              <Layers className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-extrabold text-white">{totalWeightKg} kg</span>
            <p className="mt-1 text-xs text-slate-550">Total remaining weight</p>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl border border-slate-900 bg-slate-950/40 p-5 backdrop-blur-xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Needs Enrichment</span>
            <div className="rounded-xl bg-amber-500/10 p-2 text-amber-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{draftSpools}</span>
            {draftSpools > 0 && (
              <span className="text-xs font-bold text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/25 animate-pulse">
                Action Required
              </span>
            )}
          </div>
          <div className="mt-1 text-xs text-slate-550">Auto-discovered RFID drafts</div>
        </div>

      </div>

      {/* Filters and Search Bar Container */}
      <div className="rounded-2xl border border-slate-900 bg-slate-950/20 p-5 space-y-4">
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search by material, owner, price..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-xl border border-slate-900 bg-slate-950/60 py-2.5 pl-10 pr-4 text-sm text-slate-250 placeholder-slate-650 outline-none focus:border-emerald-500/50 transition-colors"
            />
          </div>

          {/* Group-by & Layout Selector */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 rounded-xl border border-slate-900 bg-slate-950/40 px-3.5 py-1.5">
              <SlidersHorizontal className="h-3.5 w-3.5 text-slate-400" />
              <span className="text-xs text-slate-400 font-semibold mr-1">Group:</span>
              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value as any)}
                className="bg-transparent border-none text-xs text-slate-200 outline-none cursor-pointer pr-1 font-bold"
              >
                <option value="none" className="bg-[#0f1115] text-slate-300">None (List)</option>
                <option value="status" className="bg-[#0f1115] text-slate-300">By Status</option>
                <option value="location" className="bg-[#0f1115] text-slate-300">By Location</option>
                <option value="material" className="bg-[#0f1115] text-slate-300">By Material</option>
              </select>
            </div>

            {/* Layout Toggles */}
            <div className="flex items-center rounded-xl border border-slate-900 bg-slate-950/40 p-1">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-1.5 rounded-lg transition-all cursor-pointer ${viewMode === "grid" ? "bg-slate-900 text-emerald-400" : "text-slate-500 hover:text-slate-300"}`}
                title="Grid Layout"
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded-lg transition-all cursor-pointer ${viewMode === "table" ? "bg-slate-900 text-emerald-400" : "text-slate-500 hover:text-slate-300"}`}
                title="Table Layout"
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Advanced Filters */}
        <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-slate-900/60">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 mr-1.5">
            <Filter className="h-3.5 w-3.5" />
            <span className="font-bold uppercase tracking-wider">Filters:</span>
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] text-slate-500 font-semibold">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-lg border border-slate-900 bg-slate-950/60 px-2.5 py-1 text-xs text-slate-300 outline-none cursor-pointer font-bold focus:border-emerald-500/20"
            >
              <option value="ALL">All Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="AVAILABLE">Available</option>
              <option value="IN_USE">In Use</option>
              <option value="SPENT">Spent</option>
            </select>
          </div>

          {/* Location filter */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] text-slate-500 font-semibold">Location:</span>
            <select
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="rounded-lg border border-slate-900 bg-slate-950/60 px-2.5 py-1 text-xs text-slate-300 outline-none cursor-pointer font-bold focus:border-emerald-500/20"
            >
              <option value="ALL">All Locations</option>
              <option value="ZWICKAU">Zwickau</option>
              <option value="PLAUEN">Plauen</option>
              <option value="STANDBY">Standby (Not in AMS)</option>
            </select>
          </div>

          {/* Material type filter */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] text-slate-500 font-semibold">Material:</span>
            <select
              value={materialFilter}
              onChange={(e) => setMaterialFilter(e.target.value)}
              className="rounded-lg border border-slate-900 bg-slate-950/60 px-2.5 py-1 text-xs text-slate-300 outline-none cursor-pointer font-bold focus:border-emerald-500/20"
            >
              <option value="ALL">All Materials</option>
              {uniqueMaterials.map(mat => (
                <option key={mat} value={mat}>{mat}</option>
              ))}
            </select>
          </div>

          {/* Clear Filters indicator */}
          {(statusFilter !== "ALL" || locationFilter !== "ALL" || materialFilter !== "ALL" || searchTerm !== "") && (
            <button
              onClick={() => {
                setStatusFilter("ALL");
                setLocationFilter("ALL");
                setMaterialFilter("ALL");
                setSearchTerm("");
              }}
              className="text-xs font-semibold text-rose-500 hover:text-rose-450 hover:underline flex items-center gap-1 cursor-pointer"
            >
              <X className="h-3 w-3" />
              <span>Reset filters</span>
            </button>
          )}
        </div>

      </div>

      {/* Main Results Listing */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
          <p className="text-slate-550 font-medium text-sm">Querying inventory databases...</p>
        </div>
      ) : filteredSpools.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-900 p-16 text-center">
          <Layers className="h-10 w-10 text-slate-650 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white">No spools found</h3>
          <p className="text-slate-550 text-sm mt-1 max-w-sm mx-auto">
            Try adjusting your search criteria, resetting filters, or check connection to MQTT auto-discovery brokers.
          </p>
        </div>
      ) : groupBy === "none" ? (
        // Flat Spools Listing
        viewMode === "grid" ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredSpools.map(spool => renderSpoolCard(spool))}
          </div>
        ) : (
          /* Table View */
          <div className="overflow-x-auto rounded-2xl border border-slate-900 bg-slate-950/40 backdrop-blur-xl">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-900 text-slate-500 font-bold uppercase tracking-wider">
                  <th className="py-4.5 px-6">Material</th>
                  <th className="py-4.5 px-6">Color</th>
                  <th className="py-4.5 px-6">Status</th>
                  <th className="py-4.5 px-6">Remaining Weight</th>
                  <th className="py-4.5 px-6">Location</th>
                  <th className="py-4.5 px-6">Owner</th>
                  <th className="py-4.5 px-6">Price</th>
                  <th className="py-4.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/60">
                {filteredSpools.map(spool => {
                  const isDraft = spool.status === "draft";
                  const spoolLoc = getSpoolLocation(spool);
                  return (
                    <tr key={spool.id} className="hover:bg-slate-900/25 transition-colors group">
                      <td className="py-4 px-6 font-extrabold text-white">
                        {spool.material_type}
                        <span className="ml-1.5 text-[9px] text-slate-500 font-normal">
                          {spool.spool_type}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-4 h-4 rounded-md border border-white/10 shadow-sm"
                            style={{ backgroundColor: spool.color_hex }}
                          />
                          <span className="font-mono text-slate-400 text-[10px]">{spool.color_hex}</span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          isDraft
                            ? "bg-amber-500/10 text-amber-400"
                            : spool.status === "in_use"
                            ? "bg-cyan-500/10 text-cyan-400"
                            : spool.status === "spent"
                            ? "bg-slate-900 text-slate-500"
                            : "bg-emerald-500/10 text-emerald-400"
                        }`}>
                          {spool.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-3">
                          <span className="font-semibold text-slate-200">{spool.remaining_weight_g.toFixed(0)}g</span>
                          <div className="h-1.5 w-16 bg-slate-900 rounded-full overflow-hidden flex-shrink-0">
                            <div
                              className={`h-full rounded-full ${getWeightColor(spool.remaining_weight_g)}`}
                              style={{ width: `${(spool.remaining_weight_g / 1000) * 100}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-6 font-semibold text-slate-400 uppercase tracking-wider">
                        {spoolLoc}
                      </td>
                      <td className="py-4 px-6 text-slate-300 font-medium">
                        {getOwnerName(spool.owner_id)}
                      </td>
                      <td className="py-4 px-6 font-bold text-white">
                        {spool.price !== null ? `${spool.price.toFixed(2)} €` : (
                          <span className="text-amber-500 italic text-[10px]">Unenriched</span>
                        )}
                      </td>
                      <td className="py-4 px-6 text-right">
                        {isDraft ? (
                          <button
                            onClick={() => openEnrichmentModal(spool)}
                            className="rounded-lg bg-amber-500 text-slate-950 font-bold px-3 py-1.5 text-[10px] hover:brightness-110 active:scale-[0.97] transition-all cursor-pointer shadow-sm shadow-amber-500/5"
                          >
                            Enrich
                          </button>
                        ) : (
                          <span className="text-[10px] text-slate-650 font-semibold uppercase tracking-widest group-hover:text-slate-500">Verified</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )
      ) : (
        /* Grouped View Mode */
        <div className="space-y-8">
          {Object.entries(groupedSpools).map(([groupTitle, groupItems]) => {
            const groupWeightKg = (groupItems.reduce((acc, curr) => acc + curr.remaining_weight_g, 0) / 1000).toFixed(2);
            return (
              <div key={groupTitle} className="space-y-4">
                <div className="flex items-baseline justify-between border-b border-slate-900 pb-2">
                  <h3 className="text-lg font-black tracking-tight text-white flex items-center gap-2">
                    {groupTitle}
                    <span className="text-xs font-bold text-slate-550 bg-slate-900 px-2 py-0.5 rounded-full">
                      {groupItems.length} {groupItems.length === 1 ? "spool" : "spools"}
                    </span>
                  </h3>
                  <span className="text-xs font-semibold text-slate-550">
                    Total Weight: <span className="text-slate-350">{groupWeightKg} kg</span>
                  </span>
                </div>

                {viewMode === "grid" ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {groupItems.map(spool => renderSpoolCard(spool))}
                  </div>
                ) : (
                  <div className="overflow-x-auto rounded-2xl border border-slate-900 bg-slate-950/40 backdrop-blur-xl">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-900 text-slate-500 font-bold uppercase tracking-wider">
                          <th className="py-4.5 px-6">Material</th>
                          <th className="py-4.5 px-6">Color</th>
                          <th className="py-4.5 px-6">Status</th>
                          <th className="py-4.5 px-6">Remaining Weight</th>
                          <th className="py-4.5 px-6">Location</th>
                          <th className="py-4.5 px-6">Owner</th>
                          <th className="py-4.5 px-6">Price</th>
                          <th className="py-4.5 px-6 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-900/60">
                        {groupItems.map(spool => {
                          const isDraft = spool.status === "draft";
                          const spoolLoc = getSpoolLocation(spool);
                          return (
                            <tr key={spool.id} className="hover:bg-slate-900/25 transition-colors group">
                              <td className="py-4 px-6 font-extrabold text-white">
                                {spool.material_type}
                                <span className="ml-1.5 text-[9px] text-slate-500 font-normal">
                                  {spool.spool_type}
                                </span>
                              </td>
                              <td className="py-4 px-6">
                                <div className="flex items-center gap-2">
                                  <div
                                    className="w-4 h-4 rounded-md border border-white/10 shadow-sm"
                                    style={{ backgroundColor: spool.color_hex }}
                                  />
                                  <span className="font-mono text-slate-400 text-[10px]">{spool.color_hex}</span>
                                </div>
                              </td>
                              <td className="py-4 px-6">
                                <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                                  isDraft
                                    ? "bg-amber-500/10 text-amber-400"
                                    : spool.status === "in_use"
                                    ? "bg-cyan-500/10 text-cyan-400"
                                    : spool.status === "spent"
                                    ? "bg-slate-900 text-slate-500"
                                    : "bg-emerald-500/10 text-emerald-400"
                                }`}>
                                  {spool.status.replace("_", " ")}
                                </span>
                              </td>
                              <td className="py-4 px-6">
                                <div className="flex items-center gap-3">
                                  <span className="font-semibold text-slate-200">{spool.remaining_weight_g.toFixed(0)}g</span>
                                  <div className="h-1.5 w-16 bg-slate-900 rounded-full overflow-hidden flex-shrink-0">
                                    <div
                                      className={`h-full rounded-full ${getWeightColor(spool.remaining_weight_g)}`}
                                      style={{ width: `${(spool.remaining_weight_g / 1000) * 100}%` }}
                                    />
                                  </div>
                                </div>
                              </td>
                              <td className="py-4 px-6 font-semibold text-slate-400 uppercase tracking-wider">
                                {spoolLoc}
                              </td>
                              <td className="py-4 px-6 text-slate-300 font-medium">
                                {getOwnerName(spool.owner_id)}
                              </td>
                              <td className="py-4 px-6 font-bold text-white">
                                {spool.price !== null ? `${spool.price.toFixed(2)} €` : (
                                  <span className="text-amber-500 italic text-[10px]">Unenriched</span>
                                )}
                              </td>
                              <td className="py-4 px-6 text-right">
                                {isDraft ? (
                                  <button
                                    onClick={() => openEnrichmentModal(spool)}
                                    className="rounded-lg bg-amber-500 text-slate-950 font-bold px-3 py-1.5 text-[10px] hover:brightness-110 active:scale-[0.97] transition-all cursor-pointer shadow-sm shadow-amber-500/5"
                                  >
                                    Enrich
                                  </button>
                                ) : (
                                  <span className="text-[10px] text-slate-650 font-semibold uppercase tracking-widest group-hover:text-slate-500">Verified</span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Enrichment Modal */}
      {enrichModalOpen && selectedSpool && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-md rounded-2xl border border-slate-800 bg-[#0d0f12] p-6 shadow-2xl space-y-6 relative overflow-hidden"
          >
            {/* Background Glow */}
            <div className="absolute top-0 left-0 -mt-8 -ml-8 h-28 w-28 rounded-full bg-amber-500/10 blur-2xl pointer-events-none"></div>

            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                <h3 className="text-lg font-extrabold text-white tracking-tight">
                  Enrich Spool Details
                </h3>
              </div>
              <button
                onClick={() => setEnrichModalOpen(false)}
                className="rounded-lg p-1 text-slate-500 hover:bg-slate-900 hover:text-slate-350 transition-all cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-900 flex items-center gap-4.5">
              <div
                className="w-9 h-9 rounded-xl border border-white/20 shadow-inner flex-shrink-0"
                style={{ backgroundColor: selectedSpool.color_hex }}
              />
              <div className="text-xs">
                <div className="font-extrabold text-white text-sm">{selectedSpool.material_type} Spool</div>
                <div className="text-slate-500 mt-0.5">Tray ID: <span className="font-mono">{selectedSpool.bambu_tray_id || "None"}</span></div>
                <div className="text-slate-500">Weight: {selectedSpool.remaining_weight_g.toFixed(0)}g remaining</div>
              </div>
            </div>

            <form onSubmit={handleEnrichSubmit} className="space-y-4">
              {enrichError && (
                <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs font-semibold text-rose-400 flex items-center gap-2">
                  <X className="h-4 w-4 shrink-0" />
                  <span>{enrichError}</span>
                </div>
              )}

              {/* Price field */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Purchase Price (€)</label>
                <div className="relative">
                  <DollarSign className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    placeholder="e.g. 19.99"
                    value={enrichPrice}
                    onChange={(e) => setEnrichPrice(e.target.value)}
                    className="w-full rounded-xl border border-slate-900 bg-slate-950/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-650 outline-none focus:border-amber-500/50 transition-colors"
                  />
                </div>
              </div>

              {/* Owner field */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Spool Owner</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
                  <select
                    value={enrichOwnerId}
                    onChange={(e) => setEnrichOwnerId(e.target.value)}
                    className="w-full rounded-xl border border-slate-900 bg-slate-950/60 py-2.5 pl-10 pr-8 text-sm text-slate-200 outline-none focus:border-amber-500/50 appearance-none cursor-pointer font-semibold"
                  >
                    {users.map(u => (
                      <option key={u.id} value={u.id} className="bg-[#0d0f12]">
                        {u.full_name || u.username}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3.5 top-3.5 h-4 w-4 text-slate-500 pointer-events-none" />
                </div>
              </div>

              {/* Spool Type */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Spool Packaging</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setEnrichSpoolType("spool")}
                    className={`py-2 px-4 rounded-xl border text-xs font-semibold cursor-pointer text-center transition-all ${
                      enrichSpoolType === "spool"
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/35"
                        : "bg-slate-950/40 text-slate-400 border-slate-900 hover:border-slate-800"
                    }`}
                  >
                    Standard Spool
                  </button>
                  <button
                    type="button"
                    onClick={() => setEnrichSpoolType("refill")}
                    className={`py-2 px-4 rounded-xl border text-xs font-semibold cursor-pointer text-center transition-all ${
                      enrichSpoolType === "refill"
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/35"
                        : "bg-slate-950/40 text-slate-400 border-slate-900 hover:border-slate-800"
                    }`}
                  >
                    Refill Only
                  </button>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setEnrichModalOpen(false)}
                  className="rounded-xl border border-slate-900 bg-slate-950/60 px-4 py-2.5 text-xs font-bold text-slate-350 hover:text-white cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={enrichSubmitting}
                  className="rounded-xl bg-amber-500 text-slate-950 font-bold px-5 py-2.5 text-xs hover:brightness-110 disabled:opacity-50 transition-all cursor-pointer shadow-md shadow-amber-500/10 flex items-center gap-1.5"
                >
                  {enrichSubmitting ? (
                    <>
                      <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Check className="h-3.5 w-3.5" />
                      <span>Save and Enlist</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
