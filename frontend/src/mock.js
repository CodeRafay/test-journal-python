// Mock data for journal entries
export const mockEntries = [
  {
    id: "1",
    title: "My First Day at Work",
    content: "Today was an amazing first day at my new job. Met incredible colleagues and learned about exciting projects ahead. The office culture seems very welcoming and collaborative.",
    category: "Work",
    tags: ["work", "first-day", "excitement"],
    isShared: true,
    dateCreated: "2024-01-15T09:00:00Z",
    dateModified: "2024-01-15T09:00:00Z"
  },
  {
    id: "2", 
    title: "Weekend Hiking Adventure",
    content: "Explored the mountain trails today. The views were breathtaking and the weather was perfect. Managed to reach the summit just as the sun was setting. Need to do this more often.",
    category: "Personal",
    tags: ["hiking", "nature", "adventure"],
    isShared: false,
    dateCreated: "2024-01-20T16:30:00Z",
    dateModified: "2024-01-20T16:30:00Z"
  },
  {
    id: "3",
    title: "Project Presentation Success",
    content: "The quarterly presentation went better than expected. The client loved our proposal and we secured the contract. Team celebration afterwards was well deserved.",
    category: "Work",
    tags: ["presentation", "success", "client"],
    isShared: true,
    dateCreated: "2024-01-25T14:00:00Z",
    dateModified: "2024-01-25T14:00:00Z"
  },
  {
    id: "4",
    title: "Learning React Hooks",
    content: "Spent the day diving deep into React hooks. useState and useEffect are becoming second nature, but useContext and useReducer still need more practice.",
    category: "Learning",
    tags: ["react", "programming", "hooks"],
    isShared: true,
    dateCreated: "2024-01-28T11:15:00Z",
    dateModified: "2024-01-28T11:15:00Z"
  },
  {
    id: "5",
    title: "Family Dinner Thoughts",
    content: "Had dinner with family tonight. Mom's cooking never fails to bring back childhood memories. These moments remind me what truly matters in life.",
    category: "Personal",
    tags: ["family", "memories", "gratitude"],
    isShared: false,
    dateCreated: "2024-02-01T19:45:00Z",
    dateModified: "2024-02-01T19:45:00Z"
  }
];

// Mock authentication data
export const mockAuth = {
  adminPassword: "12345678",
  viewerPassword: "87654321"
};

// Mock utility functions
export const getMockEntries = () => [...mockEntries];

export const getMockSharedEntries = () => mockEntries.filter(entry => entry.isShared);

export const addMockEntry = (entry) => {
  const newEntry = {
    ...entry,
    id: Date.now().toString(),
    dateCreated: new Date().toISOString(),
    dateModified: new Date().toISOString()
  };
  mockEntries.push(newEntry);
  return newEntry;
};

export const updateMockEntry = (id, updates) => {
  const index = mockEntries.findIndex(entry => entry.id === id);
  if (index !== -1) {
    mockEntries[index] = {
      ...mockEntries[index],
      ...updates,
      dateModified: new Date().toISOString()
    };
    return mockEntries[index];
  }
  return null;
};

export const deleteMockEntry = (id) => {
  const index = mockEntries.findIndex(entry => entry.id === id);
  if (index !== -1) {
    return mockEntries.splice(index, 1)[0];
  }
  return null;
};

export const searchMockEntries = (query, isSharedOnly = false) => {
  let entries = isSharedOnly ? getMockSharedEntries() : getMockEntries();
  
  if (!query.trim()) return entries;
  
  const searchTerm = query.toLowerCase();
  return entries.filter(entry => 
    entry.title.toLowerCase().includes(searchTerm) ||
    entry.content.toLowerCase().includes(searchTerm) ||
    entry.tags.some(tag => tag.toLowerCase().includes(searchTerm))
  );
};

export const getCategories = () => {
  const categories = new Set(mockEntries.map(entry => entry.category));
  return Array.from(categories);
};

export const getEntriesByCategory = (isSharedOnly = false) => {
  const entries = isSharedOnly ? getMockSharedEntries() : getMockEntries();
  const grouped = {};
  
  entries.forEach(entry => {
    if (!grouped[entry.category]) {
      grouped[entry.category] = [];
    }
    grouped[entry.category].push(entry);
  });
  
  return grouped;
};