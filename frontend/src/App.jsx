import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Layout from "./components/layout/Layout";

import Dashboard from "./pages/Dashboard";
import Mentions from "./pages/Mentions";
import Insights from "./pages/Insights";
import Competitors from "./pages/Competitors";
import Alerts from "./pages/Alerts";
import Monitoring from "./pages/Monitoring";
import SearchHistory from "./pages/SearchHistory";

import { SearchProvider } from "./context/SearchContext";


function App() {
  return (
    <BrowserRouter>

      <SearchProvider>

        <Routes>

          <Route
            element={<Layout />}
          >

            <Route
              path="/"
              element={
                <Navigate
                  to="/dashboard"
                  replace
                />
              }
            />

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/mentions"
              element={<Mentions />}
            />

            <Route
              path="/insights"
              element={<Insights />}
            />

            <Route
              path="/competitors"
              element={<Competitors />}
            />

            <Route
              path="/alerts"
              element={<Alerts />}
            />

            <Route
              path="/monitoring"
              element={<Monitoring />}
            />

            <Route
              path="/history"
              element={<SearchHistory />}
            />

          </Route>

        </Routes>

      </SearchProvider>

    </BrowserRouter>
  );
}


export default App;