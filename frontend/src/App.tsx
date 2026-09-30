import React, { useState } from 'react';
import { SearchBar } from './components/Search';
import { Results } from './components/Results';
import { SearchResult } from './types';
import './App.css';

const App: React.FC = () => {
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <SearchBar onSearch={setResult} onLoading={setLoading} />
      {loading && <p className="loading">Searching...</p>}
      {result && <Results result={result} />}
    </div>
  );
};

export default App;
