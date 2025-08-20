import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Edit, Trash2, Eye, EyeOff, Calendar, Tag } from 'lucide-react';

const EntryCard = ({ entry, isAdmin = false, onEdit, onDelete, onToggleVisibility }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card className="bg-gray-800/50 border-gray-700 hover:border-red-600/30 transition-all duration-300 group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-100 group-hover:text-red-400 transition-colors">
              {entry.title}
            </CardTitle>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400">
              <div className="flex items-center space-x-1">
                <Calendar className="w-4 h-4" />
                <span>{formatDate(entry.dateCreated)}</span>
              </div>
              <Badge variant="outline" className="text-xs border-gray-600 text-gray-300">
                {entry.category}
              </Badge>
            </div>
          </div>
          
          {isAdmin && (
            <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onToggleVisibility?.(entry.id)}
                className="h-8 w-8 p-0 hover:bg-red-600/20 hover:text-red-400"
              >
                {entry.isShared ? (
                  <Eye className="w-4 h-4" />
                ) : (
                  <EyeOff className="w-4 h-4" />
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onEdit?.(entry)}
                className="h-8 w-8 p-0 hover:bg-red-600/20 hover:text-red-400"
              >
                <Edit className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onDelete?.(entry.id)}
                className="h-8 w-8 p-0 hover:bg-red-600/20 hover:text-red-400"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-gray-300 text-sm leading-relaxed mb-4 line-clamp-3">
          {entry.content}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Tag className="w-4 h-4 text-gray-500" />
            <div className="flex flex-wrap gap-1">
              {entry.tags.map((tag, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="text-xs bg-red-600/10 text-red-400 border-red-600/30"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {entry.isShared ? (
              <Badge className="text-xs bg-green-600/20 text-green-400 border-green-600/30">
                Shared
              </Badge>
            ) : (
              <Badge variant="outline" className="text-xs border-gray-600 text-gray-400">
                Private
              </Badge>
            )}
          </div>
        </div>
        
        {entry.dateModified !== entry.dateCreated && (
          <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
            Modified: {formatDate(entry.dateModified)}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EntryCard;