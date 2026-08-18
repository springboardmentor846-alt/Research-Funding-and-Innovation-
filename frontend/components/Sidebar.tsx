"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { logout } from "@/lib/api";

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  const [collapsed, setCollapsed] = useState(false);

  const navigation = [
    {
      section: "MAIN",
      items: [
        {
          name: "Dashboard",
          path: "/dashboard",
          icon: "⌂",
        },
      ],
    },

    {
      section: "WORKSPACE",
      items: [
        {
          name: "User Profile",
          path: "/profile",
          icon: "👤",
        },
        {
          name: "Innovation Portfolio",
          path: "/innovation-portfolio",
          icon: "📁",
        },
        {
          name: "Project Details",
          path: "/projects",
          icon: "📋",
        },
        {
    name: "Patent Details",
    path: "/patents/details",
    icon: "📜",
  },
       {
  name: "Research Paper Details",
  path: "/research-paper-details",
  icon: "📄",
},
        {
  name: "Prototype Details",
  path: "/prototypes/details",
  icon: "🧪",
},
        {
          name: "Innovation Vault",
          path: "/innovation-vault",
          icon: "🔐",
        },
      ],
    },

    {
      section: "INTELLIGENCE",
      items: [
        {
          name: "Research Intelligence",
          path: "/research-intelligence",
          icon: "🔬",
        },
        {
          name: "Patent Intelligence",
          path: "/patent-intelligence",
          icon: "⚡",
        },
        {
          name: "Funding Intelligence",
          path: "/funding-intelligence",
          icon: "💰",
        },
      ],
    },
  ];

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <aside
      className={`
        fixed
        left-0
        top-0
        z-50
        h-screen
        border-r
        border-slate-800
        bg-[#071321]
        text-white
        transition-all
        duration-300
        ${collapsed ? "w-20" : "w-72"}
      `}
    >
      {/* Logo */}
      <div className="flex h-20 items-center justify-between border-b border-slate-800 px-5">

        {!collapsed && (
          <button
            onClick={() => router.push("/dashboard")}
            className="text-xl font-bold tracking-tight"
          >
            <span className="text-cyan-400">
              Inno
            </span>

            <span className="text-white">
              Bridge
            </span>

            <span className="text-indigo-400">
              -AI
            </span>
          </button>
        )}

        {/* Collapse Button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="
            flex
            h-9
            w-9
            items-center
            justify-center
            rounded-lg
            border
            border-slate-700
            text-slate-400
            transition
            hover:border-cyan-400
            hover:text-cyan-400
          "
        >
          {collapsed ? "→" : "←"}
        </button>

      </div>

      {/* Navigation */}
      <div className="flex h-[calc(100vh-5rem)] flex-col">

        <nav className="flex-1 overflow-y-auto px-3 py-6">

          {navigation.map((group) => (
            <div
              key={group.section}
              className="mb-7"
            >

              {/* Section title */}
              {!collapsed && (
                <p className="mb-3 px-3 text-xs font-semibold tracking-[0.2em] text-slate-500">
                  {group.section}
                </p>
              )}

              {/* Items */}
              <div className="space-y-1">

                {group.items.map((item) => {

                  const isActive =
                    pathname === item.path ||
                    pathname.startsWith(
                      `${item.path}/`
                    );

                  return (
                    <button
                      key={item.path}
                      onClick={() =>
                        handleNavigation(item.path)
                      }
                      title={
                        collapsed
                          ? item.name
                          : undefined
                      }
                      className={`
                        group
                        flex
                        w-full
                        items-center
                        gap-3
                        rounded-xl
                        px-3
                        py-3
                        text-left
                        transition-all
                        duration-200

                        ${
                          isActive
                            ? "border border-cyan-400/30 bg-cyan-400/10 text-cyan-400"
                            : "text-slate-400 hover:bg-slate-800/70 hover:text-white"
                        }

                        ${
                          collapsed
                            ? "justify-center"
                            : ""
                        }
                      `}
                    >

                      {/* Icon */}
                      <span
                        className={`
                          flex
                          h-9
                          w-9
                          shrink-0
                          items-center
                          justify-center
                          rounded-lg
                          text-lg

                          ${
                            isActive
                              ? "bg-cyan-400/10"
                              : "bg-slate-800/60"
                          }
                        `}
                      >
                        {item.icon}
                      </span>

                      {/* Name */}
                      {!collapsed && (
                        <span className="text-sm font-medium">
                          {item.name}
                        </span>
                      )}

                    </button>
                  );
                })}

              </div>
            </div>
          ))}

        </nav>

        {/* Bottom */}
        <div className="border-t border-slate-800 p-3">

          <button
            onClick={handleLogout}
            title={
              collapsed
                ? "Logout"
                : undefined
            }
            className={`
              flex
              w-full
              items-center
              gap-3
              rounded-xl
              px-3
              py-3
              text-left
              text-slate-400
              transition
              hover:bg-red-500/10
              hover:text-red-400

              ${
                collapsed
                  ? "justify-center"
                  : ""
              }
            `}
          >

            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-800/60">
              🚪
            </span>

            {!collapsed && (
              <span className="text-sm font-medium">
                Logout
              </span>
            )}

          </button>

        </div>

      </div>

    </aside>
  );
}