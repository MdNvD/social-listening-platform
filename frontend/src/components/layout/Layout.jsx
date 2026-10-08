import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";


function Layout() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <Sidebar />

      <main className="ml-64 min-h-screen">

        <div className="px-8 py-8">
          <Outlet />
        </div>

      </main>

    </div>
  );
}


export default Layout;