import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Delete, ArrowRight } from 'lucide-react';
import { mockAuth } from '../mock';

const NumericKeypad = ({ onLogin, error }) => {
  const [password, setPassword] = useState('');

  const handleNumberClick = (number) => {
    if (password.length < 8) {
      setPassword(prev => prev + number);
    }
  };

  const handleDelete = () => {
    setPassword(prev => prev.slice(0, -1));
  };

  const handleClear = () => {
    setPassword('');
  };

  const handleEnter = () => {
    if (password.length === 8) {
      if (password === mockAuth.adminPassword) {
        onLogin('admin');
      } else if (password === mockAuth.viewerPassword) {
        onLogin('viewer');
      } else {
        onLogin(null); // Invalid password
      }
    }
  };

  const renderPasswordBoxes = () => {
    return Array.from({ length: 8 }, (_, index) => (
      <div
        key={index}
        className={`w-10 h-10 border-2 rounded-lg flex items-center justify-center text-lg font-bold
          ${password.length > index 
            ? 'border-red-600 bg-red-600/10 text-red-400' 
            : 'border-gray-700 bg-gray-800/50'
          }`}
      >
        {password.length > index ? '●' : ''}
      </div>
    ));
  };

  const numbers = [
    [1, 2, 3],
    [4, 5, 6], 
    [7, 8, 9],
    ['C', 0, 'DEL']
  ];

  return (
    <div className="flex flex-col items-center space-y-6">
      {/* Numeric Keypad Card */}
      <Card className="p-6 bg-gray-800/50 border-gray-700 w-full max-w-sm">
        {/* Password Input Boxes */}
        <div className="flex justify-center space-x-2 mb-6">
          {renderPasswordBoxes()}
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-red-500 text-sm font-medium text-center mb-4">
            {error}
          </div>
        )}

        {/* Numeric Keypad Grid */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {numbers.flat().map((item, index) => {
            if (item === 'C') {
              return (
                <Button
                  key={index}
                  variant="outline"
                  size="lg"
                  onClick={handleClear}
                  className="h-14 w-14 text-lg font-bold bg-gray-700 border-gray-600 hover:bg-gray-600 text-gray-300"
                >
                  C
                </Button>
              );
            }
            
            if (item === 'DEL') {
              return (
                <Button
                  key={index}
                  variant="outline"
                  size="lg"
                  onClick={handleDelete}
                  className="h-14 w-14 bg-gray-700 border-gray-600 hover:bg-red-600/20 text-gray-300 hover:text-red-400"
                >
                  <Delete className="w-5 h-5" />
                </Button>
              );
            }

            return (
              <Button
                key={index}
                variant="outline"
                size="lg"
                onClick={() => handleNumberClick(item.toString())}
                className="h-14 w-14 text-lg font-bold bg-gray-800 border-gray-600 hover:bg-red-600/20 hover:border-red-600/50 text-gray-300 hover:text-red-400 transition-all duration-200"
              >
                {item}
              </Button>
            );
          })}
        </div>
        
        {/* Enter Button */}
        <div className="flex justify-center">
          <Button
            onClick={handleEnter}
            disabled={password.length !== 8}
            className="w-full h-14 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-bold text-lg transition-all duration-200"
          >
            <ArrowRight className="w-5 h-5 mr-2" />
            ENTER
          </Button>
        </div>
      </Card>

      {/* Hints */}
      <div className="text-center text-gray-500 text-sm space-y-1">
        <p>Admin: {mockAuth.adminPassword}</p>
        <p>Viewer: {mockAuth.viewerPassword}</p>
      </div>
    </div>
  );
};

export default NumericKeypad;