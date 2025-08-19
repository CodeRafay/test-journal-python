import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import EntryCard from '../components/EntryCard';
import SearchBar from '../components/SearchBar';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent } from '../components/ui/card';
import { LogOut, Users, Eye, BookOpen, Filter, Loader2 } from 'lucide-react';
import { useJournalData } from '../hooks/useJournalData';
import { journalAPI } from '../services/api';

const ViewerDashboard = () => {
  const navigate = useNavigate();
  const {
    entries,
    categories,
    loading,
    error,
    loadData,
    clearError
  } = useJournalData(true);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Check authentication
  useEffect(() => {
    const userRole = localStorage.getItem('userRole');
    if (userRole !== 'viewer') {
      navigate('/');
    }
  }, [navigate]);

  const handleSearch = (query) => {
    setSearchQuery(query);
    loadData(query, selectedCategory);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    loadData(searchQuery, category);
  };

  const handleLogout = async () => {
    try {
      await journalAPI.logout();
      localStorage.removeItem('userRole');
      navigate('/');
    } catch (err) {
      console.error('Logout error:', err);
      // Force logout even if API call fails
      localStorage.removeItem('userRole');
      navigate('/');
    }
  };

  // Calculate total entries count with useMemo
  const totalEntries = useMemo(() => {
    return Object.values(entries).reduce((total, categoryEntries) => {
      return total + categoryEntries.length;
    }, 0);
  }, [entries]);

  // Clear error after some time
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-green-600/20 rounded-lg">
              <Users className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-100">Shared Journal</h1>
              <p className="text-gray-400 text-sm">View shared entries</p>
            </div>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="border-gray-600 hover:bg-red-600/20 hover:border-red-600/50 text-gray-300 hover:text-red-400"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-600/20 rounded-lg">
                  <Eye className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-100">{totalEntries}</p>
                  <p className="text-gray-400 text-sm">Shared Entries</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-600/20 rounded-lg">
                  <BookOpen className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-100">{categories.length}</p>
                  <p className="text-gray-400 text-sm">Categories</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1">
            <SearchBar onSearch={handleSearch} placeholder="Search shared entries..." />
          </div>
          
          {categories.length > 0 && (
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={selectedCategory}
                onChange={(e) => handleCategoryChange(e.target.value)}
                className="px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-gray-100 focus:border-red-600 focus:ring-1 focus:ring-red-600/20"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-green-500" />
            <span className="ml-2 text-gray-400">Loading entries...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card className="bg-red-900/20 border-red-700 mb-6">
            <CardContent className="p-4">
              <p className="text-red-400">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Entries by Category */}
        {!loading && (
          <div className="space-y-8">
            {Object.keys(entries).length === 0 ? (
              <Card className="bg-gray-800/30 border-gray-700">
                <CardContent className="p-12 text-center">
                  <Users className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-300 mb-2">
                    {searchQuery ? 'No entries found' : 'No shared entries'}
                  </h3>
                  <p className="text-gray-500">
                    {searchQuery 
                      ? 'Try adjusting your search terms or filters'
                      : 'The admin hasn\'t shared any entries yet'
                    }
                  </p>
                </CardContent>
              </Card>
            ) : (
              Object.entries(entries).map(([category, categoryEntries]) => (
                <div key={category}>
                  <div className="flex items-center space-x-3 mb-4">
                    <h2 className="text-xl font-semibold text-gray-100">{category}</h2>
                    <Badge variant="outline" className="border-gray-600 text-gray-400">
                      {categoryEntries.length} {categoryEntries.length === 1 ? 'entry' : 'entries'}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {categoryEntries.map(entry => (
                      <EntryCard
                        key={entry.id}
                        entry={entry}
                        isAdmin={false}
                      />
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ViewerDashboard;