import {
  NavLink,
  useLocation,
} from "react-router-dom";

import { useSearch } from "../../context/useSearch";


const navigation = [
  {
    name: "Dashboard",
    path: "/dashboard",
  },
  {
    name: "Mentions",
    path: "/mentions",
  },
  {
    name: "AI Insights",
    path: "/insights",
  },
  {
    name: "Competitors",
    path: "/competitors",
  },
  {
    name: "Alerts",
    path: "/alerts",
  },
  {
    name: "Scheduled Monitoring",
    path: "/monitoring",
  },
  {
    name: "Search History",
    path: "/history",
  },
];


function Sidebar() {
  const location = useLocation();

  const {
    activeSearch,
  } = useSearch();


  // ---------------------------------------------------------
  // Get search_id from the current URL first.
  // If it isn't there, use the active SearchContext.
  // ---------------------------------------------------------

  const currentSearchId =
    new URLSearchParams(
      location.search
    ).get("search_id") ||
    activeSearch?.id ||
    null;


  // ---------------------------------------------------------
  // Build navigation URL.
  //
  // While a search is active:
  //
  // /dashboard?search_id=123
  // /mentions?search_id=123
  // /insights?search_id=123
  //
  // On a fresh dashboard:
  //
  // /dashboard
  //
  // ---------------------------------------------------------

  const getNavigationPath = (path) => {
    if (!currentSearchId) {
      return path;
    }

    return `${path}?search_id=${currentSearchId}`;
  };


  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-slate-800 bg-slate-950">

      {/* Brand */}
      <div className="border-b border-slate-800 px-6 py-6">

        <h1 className="text-xl font-bold tracking-tight text-white">
          Social Listening
        </h1>

        <p className="mt-1 text-xs text-slate-500">
          Open-source intelligence platform
        </p>

      </div>


      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">

        {navigation.map((item) => (

          <NavLink
            key={item.path}
            to={getNavigationPath(item.path)}
            className={({ isActive }) =>
              [
                "block rounded-lg px-4 py-3 text-sm font-medium transition",

                isActive
                  ? "bg-blue-600/15 text-blue-400"
                  : "text-slate-400 hover:bg-slate-900 hover:text-white",

              ].join(" ")
            }
          >
            {item.name}
          </NavLink>

        ))}

      </nav>


      {/* Footer */}
      <div className="border-t border-slate-800 p-4">

        <p className="text-xs text-slate-600">
          Social Listening Platform
        </p>

        <p className="mt-1 text-xs text-slate-700">
          v1.0.0
        </p>

      </div>

    </aside>
  );
}


export default Sidebar;