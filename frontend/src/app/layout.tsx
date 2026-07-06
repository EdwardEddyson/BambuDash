import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BambuDash - 3D Printer Management",
  description: "Comprehensive management system for Bambu Lab 3D printers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
