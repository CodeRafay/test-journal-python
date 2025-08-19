import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import EntryCard from '../components/EntryCard';
import SearchBar from '../components/SearchBar';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent } from '../components/ui/card';
import { LogOut, Users, Eye, BookOpen, Filter } from 'lucide-react';
import {
  getMockSharedEntries,
  searchMockEntries,
  getEntriesByCategory
} from '../mock';

const ViewerDashboard = () => {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categories, setCategories] = useState([]);

  // Check authentication
  useEffect(() => {
    const userRole = localStorage.getItem('userRole');
    if (userRole !== 'viewer') {
      navigate('/');
    }
  }, [navigate]);

  // Load shared entries
  useEffect(() => {
    const sharedEntries = getMockSharedEntries();
    setEntries(sharedEntries);
    
    // Get categories from shared entries only
    const sharedCategories = [...new Set(sharedEntries.map(entry => entry.category))];
    setCategories(sharedCategories);
  }, []);

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    navigate('/');
  };

  const groupedEntries = () => {
    const grouped = getEntriesByCategory(true); // Only shared entries
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
                  <p className="text-2xl font-bold text-gray-100">{entries.length}</p>
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
                onChange={(e) => setSelectedCategory(e.target.value)}
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

        {/* Entries by Category */}
        <div className="space-y-8">
          {Object.keys(groupedEntries()).length === 0 ? (
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
                      isAdmin={false}
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

export default ViewerDashboard;