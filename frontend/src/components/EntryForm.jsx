import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { X, Plus, Save, ArrowLeft } from 'lucide-react';

const EntryForm = ({ entry, onSave, onCancel, categories }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    tags: [],
    isShared: false
  });
  
  const [tagInput, setTagInput] = useState('');
  const [isNewCategory, setIsNewCategory] = useState(false);

  useEffect(() => {
    if (entry) {
      setFormData({
        title: entry.title,
        content: entry.content,
        category: entry.category,
        tags: [...entry.tags],
        isShared: entry.isShared
      });
    }
  }, [entry]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleCategoryChange = (value) => {
    if (value === '__new__') {
      setIsNewCategory(true);
      handleInputChange('category', '');
    } else {
      setIsNewCategory(false);
      handleInputChange('category', value);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.title.trim() && formData.content.trim() && formData.category.trim()) {
      onSave(formData);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl font-bold text-gray-100">
              {entry ? 'Edit Entry' : 'Create New Entry'}
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onCancel}
              className="hover:bg-red-600/20 hover:text-red-400"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title" className="text-gray-300 font-medium">Title</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter entry title..."
                className="bg-gray-800 border-gray-600 text-gray-100 focus:border-red-600 focus:ring-red-600/20"
                required
              />
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category" className="text-gray-300 font-medium">Category</Label>
              {!isNewCategory ? (
                <select
                  value={formData.category}
                  onChange={(e) => handleCategoryChange(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-gray-100 focus:border-red-600 focus:ring-1 focus:ring-red-600/20"
                  required
                >
                  <option value="">Select category...</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                  <option value="__new__">+ Create new category</option>
                </select>
              ) : (
                <div className="flex space-x-2">
                  <Input
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    placeholder="Enter new category name..."
                    className="bg-gray-800 border-gray-600 text-gray-100 focus:border-red-600 focus:ring-red-600/20"
                    required
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsNewCategory(false)}
                    className="border-gray-600 hover:bg-gray-700"
                  >
                    Cancel
                  </Button>
                </div>
              )}
            </div>

            {/* Content */}
            <div className="space-y-2">
              <Label htmlFor="content" className="text-gray-300 font-medium">Content</Label>
              <Textarea
                id="content"
                value={formData.content}
                onChange={(e) => handleInputChange('content', e.target.value)}
                placeholder="Write your journal entry here..."
                className="min-h-40 bg-gray-800 border-gray-600 text-gray-100 focus:border-red-600 focus:ring-red-600/20 resize-vertical"
                required
              />
            </div>

            {/* Tags */}
            <div className="space-y-2">
              <Label className="text-gray-300 font-medium">Tags</Label>
              <div className="flex space-x-2">
                <Input
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Add a tag..."
                  className="bg-gray-800 border-gray-600 text-gray-100 focus:border-red-600 focus:ring-red-600/20"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleAddTag}
                  className="border-gray-600 hover:bg-red-600/20 hover:border-red-600/50"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {formData.tags.map((tag, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className="bg-red-600/10 text-red-400 border-red-600/30 pr-1"
                    >
                      {tag}
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveTag(tag)}
                        className="h-4 w-4 p-0 ml-1 hover:bg-red-600/20"
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Visibility Toggle */}
            <div className="flex items-center justify-between p-4 bg-gray-800/30 rounded-lg border border-gray-700">
              <div>
                <Label className="text-gray-300 font-medium">Share with viewers</Label>
                <p className="text-sm text-gray-500 mt-1">
                  Allow viewers to see this entry
                </p>
              </div>
              <Switch
                checked={formData.isShared}
                onCheckedChange={(checked) => handleInputChange('isShared', checked)}
                className="data-[state=checked]:bg-red-600"
              />
            </div>

            {/* Actions */}
            <div className="flex space-x-3 pt-4">
              <Button
                type="submit"
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium"
              >
                <Save className="w-4 h-4 mr-2" />
                {entry ? 'Update Entry' : 'Create Entry'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                className="border-gray-600 hover:bg-gray-700 text-gray-300"
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default EntryForm;