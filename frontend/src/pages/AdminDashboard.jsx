import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import EntryCard from '../components/EntryCard';
import EntryForm from '../components/EntryForm';
import SearchBar from '../components/SearchBar';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { 
  Plus, 
  LogOut, 
  BookOpen, 
  Users, 
  Eye,
  EyeOff,
  Filter,
  Grid3X3
} from 'lucide-react';
import {
  getMockEntries,
  addMockEntry,
  updateMockEntry,
  deleteMockEntry,
  searchMockEntries,
  getCategories,
  getEntriesByCategory
} from '../mock';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [filteredEntries, setFilteredEntries] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    shared: 0,
    private: 0
  });

  // Check authentication
  useEffect(() => {
    const userRole = localStorage.getItem('userRole');
    if (userRole !== 'admin') {
      navigate('/');
    }
  }, [navigate]);

  // Load initial data
  useEffect(() => {
    loadEntries();
  }, []);

  // Update filtered entries when search query or category changes
  useEffect(() => {
    filterEntries();
  }, [entries, searchQuery, selectedCategory]);

  const loadEntries = () => {
    const allEntries = getMockEntries();
    setEntries(allEntries);
    setCategories(getCategories());
    
    // Update stats
    const shared = allEntries.filter(entry => entry.isShared).length;
    setStats({
      total: allEntries.length,
      shared,
      private: allEntries.length - shared
    });
  };

  const filterEntries = () => {
    let filtered = searchQuery 
      ? searchMockEntries(searchQuery, false)
      : entries;

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(entry => entry.category === selectedCategory);
    }

    setFilteredEntries(filtered);
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleCreateEntry = () => {
    setEditingEntry(null);
    setShowForm(true);
  };

  const handleEditEntry = (entry) => {
    setEditingEntry(entry);
    setShowForm(true);
  };

  const handleSaveEntry = (formData) => {
    if (editingEntry) {
      updateMockEntry(editingEntry.id, formData);
    } else {
      addMockEntry(formData);
    }
    
    setShowForm(false);
    setEditingEntry(null);
    loadEntries();
  };

  const handleDeleteEntry = (entryId) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      deleteMockEntry(entryId);
      loadEntries();
    }
  };

  const handleToggleVisibility = (entryId) => {
    const entry = entries.find(e => e.id === entryId);
    if (entry) {
      updateMockEntry(entryId, { isShared: !entry.isShared });
      loadEntries();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    navigate('/');
  };

  const groupedEntries = () => {
    const grouped = getEntriesByCategory(false);
    const result = {};
    
    Object.keys(grouped).forEach(category => {
      if (selectedCategory === 'all' || category === selectedCategory) {
        const categoryEntries = grouped[category].filter(entry => {
          if (!searchQuery) return true;
          return entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                 entry.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                 entry.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
        });
        
        if (categoryEntries.length > 0) {
          result[category] = categoryEntries;
        }
      }
    });
    
    return result;
  };

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
                onChange={(e) => setSelectedCategory(e.target.value)}
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

        {/* Entries by Category */}
        <div className="space-y-8">
          {Object.keys(groupedEntries()).length === 0 ? (
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
            Object.entries(groupedEntries()).map(([category, categoryEntries]) => (
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
      </div>
    </div>
  );
};

export default AdminDashboard;