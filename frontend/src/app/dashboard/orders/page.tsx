"use client";

import React, { useState } from "react";
import { Plus, ShoppingBag, Search, Check, AlertCircle } from "lucide-react";
import { storeApi } from "@/lib/api-client";

export default function OrdersPage() {
  const [cartItems, setCartItems] = useState<any[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Active Cart & Orders
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Manage your store items and coordinate joint orders.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setIsDialogOpen(true)}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:brightness-110 px-4.5 py-2.5 text-xs font-bold text-slate-950 shadow-md shadow-emerald-500/10 transition-all cursor-pointer"
          >
            <Plus className="h-4 w-4" />
            <span>Add Item</span>
          </button>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-900 bg-slate-950/20 p-6">
        <div className="flex items-center space-x-2.5 mb-6">
          <ShoppingBag className="h-5 w-5 text-emerald-400" />
          <h3 className="text-lg font-bold text-white">Current Cart</h3>
        </div>

        {cartItems.length === 0 ? (
          <div className="text-center py-10 text-slate-500">
            <p>Your cart is empty. Click "Add Item" to lookup products.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {cartItems.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center rounded-xl border border-slate-900 bg-slate-950/60 p-5">
                <div>
                  <h4 className="font-bold text-slate-200">{item.name}</h4>
                  <div className="text-xs text-slate-500 mt-1">
                    SKU: {item.sku} &bull; Variant: {item.variantName}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-white">{item.price} € x {item.quantity}</div>
                  <div className="text-xs text-slate-500 mt-1">Splits: {item.splits}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {isDialogOpen && (
        <AddItemDialog
          onClose={() => setIsDialogOpen(false)}
          onAdd={(item) => {
            setCartItems([...cartItems, item]);
            setIsDialogOpen(false);
          }}
        />
      )}
    </div>
  );
}

function AddItemDialog({ onClose, onAdd }: { onClose: () => void, onAdd: (item: any) => void }) {
  const [lookupValue, setLookupValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [productData, setProductData] = useState<any>(null);
  const [selectedVariantId, setSelectedVariantId] = useState<string>("");
  const [quantity, setQuantity] = useState(1);
  const [splits, setSplits] = useState("");

  const handleLookup = async () => {
    if (!lookupValue) return;

    setIsLoading(true);
    setError(null);
    setProductData(null);

    try {
      // Extract slug from URL if a URL was pasted
      let slug = lookupValue.trim();
      try {
        const url = new URL(slug);
        const pathParts = url.pathname.split("/").filter(p => p.length > 0);
        const productIndex = pathParts.indexOf("products");
        if (productIndex !== -1 && productIndex + 1 < pathParts.length) {
          slug = pathParts[productIndex + 1];
        } else {
          // If it's a Bambu Lab URL without /products/ somehow, try last part
          slug = pathParts[pathParts.length - 1] || slug;
        }
      } catch (e) {
        // Not a URL, treat as slug directly
      }

      const data = await storeApi.lookup(slug);
      setProductData(data);
      if (data.variants && data.variants.length > 0) {
        setSelectedVariantId(data.variants[0].sku);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Product not found or store API error.");
    } finally {
      setIsLoading(false);
    }
  };

  const selectedVariant = productData?.variants?.find((v: any) => v.sku === selectedVariantId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!productData || !selectedVariant) return;

    onAdd({
      name: productData.name,
      sku: selectedVariant.sku,
      variantName: selectedVariant.name,
      price: selectedVariant.price,
      quantity,
      splits: splits || "100% User"
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl overflow-hidden flex flex-col">
        <div className="p-6 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-xl font-bold text-white">Add Store Item</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            ✕
          </button>
        </div>

        <div className="p-6 overflow-y-auto">
          {!productData ? (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">
                  Product Slug or Bambu Lab Store URL
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={lookupValue}
                    onChange={(e) => setLookupValue(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleLookup()}
                    placeholder="e.g. pla-basic or https://store.bambulab.com/products/pla-basic"
                    className="flex-1 rounded-xl bg-slate-950 border border-slate-800 p-3 text-sm text-white placeholder-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                  />
                  <button
                    onClick={handleLookup}
                    disabled={isLoading || !lookupValue}
                    className="rounded-xl bg-slate-800 hover:bg-slate-700 px-4 py-3 text-emerald-400 font-bold transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {isLoading ? <div className="h-4 w-4 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" /> : <Search className="h-4 w-4" />}
                    Lookup
                  </button>
                </div>
              </div>
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-start gap-4">
                <div className="rounded-lg bg-emerald-500/10 p-2 text-emerald-400 shrink-0">
                  <Check className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="text-white font-bold">{productData.name}</h4>
                  <p className="text-xs text-slate-400 mt-1">Successfully fetched from store</p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Variant</label>
                <select
                  value={selectedVariantId}
                  onChange={(e) => setSelectedVariantId(e.target.value)}
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-sm text-white focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                >
                  {productData.variants?.map((v: any) => (
                    <option key={v.sku} value={v.sku}>
                      {v.name} - {v.price} {productData.currency || "€"} (SKU: {v.sku})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Quantity</label>
                  <input
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-sm text-white focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Price</label>
                  <div className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-sm text-slate-300">
                    {selectedVariant ? `${selectedVariant.price} ${productData.currency || "€"}` : "-"}
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">User Split Percentage</label>
                <input
                  type="text"
                  value={splits}
                  onChange={(e) => setSplits(e.target.value)}
                  placeholder="e.g. 50% Edward, 50% User2"
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-sm text-white placeholder-slate-600 focus:border-emerald-500 outline-none"
                />
              </div>

              <div className="pt-2 flex gap-3">
                <button
                  type="button"
                  onClick={() => setProductData(null)}
                  className="flex-1 rounded-xl bg-slate-800 hover:bg-slate-700 p-3 text-sm font-bold text-white transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="flex-1 rounded-xl bg-emerald-500 hover:bg-emerald-400 p-3 text-sm font-bold text-slate-950 transition-colors"
                >
                  Add to Cart
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
