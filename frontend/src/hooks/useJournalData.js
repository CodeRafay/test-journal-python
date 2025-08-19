import { useState, useEffect, useCallback } from 'react';
import { journalAPI } from '../services/api';

export const useJournalData = (isSharedOnly = false) => {
  const [entries, setEntries] = useState({});
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load entries and categories
  const loadData = useCallback(async (search = '', category = 'all') => {
    setLoading(true);
    setError(null);
    
    try {
      const [entriesData, categoriesData] = await Promise.all([
        journalAPI.getEntries(search, category),
        journalAPI.getCategories()
      ]);
      
      setEntries(entriesData);
      setCategories(categoriesData);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load journal data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Create entry
  const createEntry = useCallback(async (entryData) => {
    try {
      await journalAPI.createEntry(entryData);
      await loadData(); // Reload data
      return true;
    } catch (err) {
      setError(err.message);
      console.error('Failed to create entry:', err);
      return false;
    }
  }, [loadData]);

  // Update entry
  const updateEntry = useCallback(async (entryId, entryData) => {
    try {
      await journalAPI.updateEntry(entryId, entryData);
      await loadData(); // Reload data
      return true;
    } catch (err) {
      setError(err.message);
      console.error('Failed to update entry:', err);
      return false;
    }
  }, [loadData]);

  // Delete entry
  const deleteEntry = useCallback(async (entryId) => {
    try {
      await journalAPI.deleteEntry(entryId);
      await loadData(); // Reload data
      return true;
    } catch (err) {
      setError(err.message);
      console.error('Failed to delete entry:', err);
      return false;
    }
  }, [loadData]);

  // Search entries
  const searchEntries = useCallback(async (query) => {
    setLoading(true);
    setError(null);
    
    try {
      const entriesData = await journalAPI.searchEntries(query, isSharedOnly);
      setEntries(entriesData);
    } catch (err) {
      setError(err.message);
      console.error('Failed to search entries:', err);
    } finally {
      setLoading(false);
    }
  }, [isSharedOnly]);

  // Get statistics from already loaded entries (no additional API call)
  const getStats = useCallback(() => {
    try {
      // Calculate stats from already loaded entries instead of making API call
      let total = 0;
      let shared = 0;
      
      // Count entries from the loaded data
      Object.values(entries).forEach(categoryEntries => {
        categoryEntries.forEach(entry => {
          total++;
          if (entry.isShared) {
            shared++;
          }
        });
      });
      
      const privateCount = total - shared;
      return { total, shared, private: privateCount };
    } catch (err) {
      console.error('Failed to calculate stats:', err);
      return { total: 0, shared: 0, private: 0 };
    }
  }, [entries]);

  // Initial load - use useEffect with stable dependency
  useEffect(() => {
    const initialLoad = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const [entriesData, categoriesData] = await Promise.all([
          journalAPI.getEntries('', 'all'),
          journalAPI.getCategories()
        ]);
        
        setEntries(entriesData);
        setCategories(categoriesData);
      } catch (err) {
        setError(err.message);
        console.error('Failed to load journal data:', err);
      } finally {
        setLoading(false);
      }
    };

    initialLoad();
  }, []); // Empty dependency array - only run once on mount

  return {
    entries,
    categories,
    loading,
    error,
    loadData,
    createEntry,
    updateEntry,
    deleteEntry,
    searchEntries,
    getStats,
    clearError: () => setError(null)
  };
};