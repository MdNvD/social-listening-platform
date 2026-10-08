import {
  useState,
} from "react";

import { SearchContext } from "./SearchContextValue";

// =========================================================
// STORAGE KEY
// =========================================================

const STORAGE_KEY = "activeSearch";

// =========================================================
// GET INITIAL SEARCH
// =========================================================
//
// Do NOT automatically restore the previous search when the
// application starts.
//
// Historical searches can still be loaded explicitly through
// Search History or a URL containing ?search_id=...
//
// =========================================================

function getInitialSearch() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error(
      "[SearchContext] Failed to clear stored search:",
      error
    );
  }

  return null;
}

// =========================================================
// SEARCH PROVIDER
// =========================================================

export function SearchProvider({ children }) {
  const [
    activeSearch,
    setActiveSearchState,
  ] = useState(getInitialSearch);

  // =======================================================
  // SET ACTIVE SEARCH
  // =======================================================

  const setActiveSearch = (search) => {
    if (!search) {
      console.warn(
        "[SearchContext] Ignoring empty search."
      );

      return;
    }

    const id = Number(search.id);

    const keyword = String(
      search.keyword || ""
    ).trim();

    if (
      !Number.isInteger(id) ||
      id <= 0 ||
      !keyword
    ) {
      console.error(
        "[SearchContext] Invalid search provided:",
        search
      );

      return;
    }

    const newSearch = {
      id,
      keyword,
    };

    console.log(
      "[SearchContext] Active search changed:",
      newSearch
    );

    setActiveSearchState(newSearch);

    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(newSearch)
      );
    } catch (error) {
      console.error(
        "[SearchContext] Failed to save active search:",
        error
      );
    }
  };

  // =======================================================
  // CLEAR ACTIVE SEARCH
  // =======================================================

  const clearActiveSearch = () => {
    console.log(
      "[SearchContext] Clearing active search."
    );

    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error(
        "[SearchContext] Failed to clear stored search:",
        error
      );
    }

    setActiveSearchState(null);
  };

  // =======================================================
  // PROVIDER
  // =======================================================

  return (
    <SearchContext.Provider
      value={{
        activeSearch,
        setActiveSearch,
        clearActiveSearch,
      }}
    >
      {children}
    </SearchContext.Provider>
  );
}