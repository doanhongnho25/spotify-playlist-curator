import { NavLink } from "react-router-dom";
import {
  GaugeCircle,
  Headphones,
  Disc3,
  LibraryBig,
  Settings,
  Timer,
  MessageCircle,
  LogOut
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: GaugeCircle },
  { to: "/accounts", label: "Accounts", icon: Headphones },
  { to: "/playlists", label: "Playlists", icon: Disc3 },
  { to: "/library", label: "Library", icon: LibraryBig },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/automation", label: "Automation", icon: Timer },
  { to: "/assistant", label: "Assistant", icon: MessageCircle }
];

export const Sidebar = () => {
  const { logout } = useAuth();

  return (
    <aside className="flex h-full w-64 flex-col bg-black/40 p-6 backdrop-blur-lg">
      <div className="mb-10 space-y-2">
        <p className="text-xs uppercase tracking-[0.3em] text-white/40">
          Vibe Engine
        </p>
        <h1 className="text-2xl font-bold text-white">Control Center</h1>
      </div>
      <nav className="flex flex-1 flex-col gap-2">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive
                  ? "bg-gradient-to-r from-accent to-accent-soft text-white shadow-glow"
                  : "text-white/60 hover:bg-white/10 hover:text-white"
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
      <Button
        className="mt-auto"
        onClick={logout}
        variant="ghost"
      >
        <LogOut className="h-4 w-4" />
        Logout
      </Button>
    </aside>
  );
};
