import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import EntryCard from '../components/EntryCard';
import EntryForm from '../components/EntryForm';
import SearchBar from '../components/SearchBar';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent } from '../components/ui/card';
import { useToast } from '../hooks/use-toast';
import { 
  Plus, 
  LogOut, 
  BookOpen, 
  Eye,
  EyeOff,
  Filter,
  Grid3X3,
  Loader2
} from 'lucide-react';
import { useJournalData } from '../hooks/useJournalData';
import { journalAPI } from '../services/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const {
    entries,
    categories,
    loading,
    error,
    loadData,
    createEntry,
    updateEntry,
    deleteEntry,
    getStats,
    clearError
  } = useJournalData(false);

  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Check authentication
  useEffect(() => {
    const userRole = localStorage.getItem('userRole');
    if (userRole !== 'admin') {
      navigate('/');
    }
  }, [navigate]);

  // Load stats - use useMemo to prevent excessive recalculations
  const stats = useMemo(() => {
    return getStats();
  }, [entries, getStats]);

  // Handle search with debouncing
  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    loadData(query, selectedCategory);
  }, [loadData, selectedCategory]);

  // Handle category filter
  const handleCategoryChange = useCallback((category) => {
    setSelectedCategory(category);
    loadData(searchQuery, category);
  }, [loadData, searchQuery]);

  const handleCreateEntry = () => {
    setEditingEntry(null);
    setShowForm(true);
  };

  const handleEditEntry = (entry) => {
    setEditingEntry(entry);
    setShowForm(true);
  };

  const handleSaveEntry = async (formData) => {
    let success = false;
    
    if (editingEntry) {
      success = await updateEntry(editingEntry.id, formData);
      if (success) {
        toast({
          title: "Success",
          description: "Entry updated successfully",
        });
      }
    } else {
      success = await createEntry(formData);
      if (success) {
        toast({
          title: "Success", 
          description: "Entry created successfully",
        });
      }
    }
    
    if (success) {
      setShowForm(false);
      setEditingEntry(null);
    } else {
      toast({
        title: "Error",
        description: error || "Operation failed",
        variant: "destructive",
      });
    }
  };

  const handleDeleteEntry = async (entryId) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      const success = await deleteEntry(entryId);
      if (success) {
        toast({
          title: "Success",
          description: "Entry deleted successfully",
        });
      } else {
        toast({
          title: "Error", 
          description: error || "Failed to delete entry",
          variant: "destructive",
        });
      }
    }
  };

  const handleToggleVisibility = async (entryId) => {
    // Find the entry in current entries
    let targetEntry = null;
    Object.values(entries).forEach(categoryEntries => {
      const found = categoryEntries.find(e => e.id === entryId);
      if (found) targetEntry = found;
    });

    if (targetEntry) {
      const success = await updateEntry(entryId, { isShared: !targetEntry.isShared });
      if (success) {
        toast({
          title: "Success",
          description: `Entry ${targetEntry.isShared ? 'made private' : 'shared'} successfully`,
        });
      } else {
        toast({
          title: "Error",
          description: error || "Failed to update entry visibility",
          variant: "destructive", 
        });
      }
    }
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

  // Clear error when component unmounts or error changes
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  if (showForm) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <EntryForm
          entry={editingEntry}
          categories={categories}
          onSave={handleSaveEntry}
          onCancel={() => {
            setShowForm(false);
            setEditingEntry(null);
          }}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-red-600/20 rounded-lg">
              <BookOpen className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-100">Admin Dashboard</h1>
              <p className="text-gray-400 text-sm">Manage your journal entries</p>
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
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-600/20 rounded-lg">
                  <Grid3X3 className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-100">{stats.total}</p>
                  <p className="text-gray-400 text-sm">Total Entries</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-600/20 rounded-lg">
                  <Eye className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-100">{stats.shared}</p>
                  <p className="text-gray-400 text-sm">Shared Entries</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gray-600/20 rounded-lg">
                  <EyeOff className="w-5 h-5 text-gray-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-100">{stats.private}</p>
                  <p className="text-gray-400 text-sm">Private Entries</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1">
            <SearchBar onSearch={handleSearch} />
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Category Filter */}
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
            
            <Button
              onClick={handleCreateEntry}
              className="bg-red-600 hover:bg-red-700 text-white font-medium"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Entry
            </Button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-red-500" />
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
                  <BookOpen className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-300 mb-2">
                    {searchQuery ? 'No entries found' : 'No entries yet'}
                  </h3>
                  <p className="text-gray-500 mb-6">
                    {searchQuery 
                      ? 'Try adjusting your search terms or filters'
                      : 'Create your first journal entry to get started'
                    }
                  </p>
                  {!searchQuery && (
                    <Button
                      onClick={handleCreateEntry}
                      className="bg-red-600 hover:bg-red-700 text-white"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create Entry
                    </Button>
                  )}
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
                        isAdmin={true}
                        onEdit={handleEditEntry}
                        onDelete={handleDeleteEntry}
                        onToggleVisibility={handleToggleVisibility}
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

export default AdminDashboard;