import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { StatusBar } from "@/components/layout/StatusBar";

export const AppShell = () => (
  <div className="flex min-h-screen bg-[#121212] text-[#EDEDED]">
    <div className="hidden lg:flex">
      <Sidebar />
    </div>
    <div className="flex flex-1 flex-col overflow-hidden">
      <Navbar />
      <StatusBar />
      <main className="flex-1 overflow-y-auto bg-gradient-to-b from-black/30 to-black/10 p-6">
        <Outlet />
      </main>
    </div>
  </div>
);
