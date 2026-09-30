import React, { useState, useCallback } from 'react';
import { SearchQuery, SearchResult, ExperienceLevel, EmploymentType, ScheduleType } from '../types';
import { searchJobs } from '../api/client';

interface SearchBarProps {
  onSearch: (result: SearchResult) => void;
  onLoading: (loading: boolean) => void;
}

const EXPERIENCE_OPTIONS: { value: ExperienceLevel; label: string }[] = [
  { value: 'noExperience', label: 'No experience' },
  { value: 'between1And3', label: '1-3 years' },
  { value: 'between3And6', label: '3-6 years' },
  { value: 'moreThan6', label: '6+ years' },
];

const EMPLOYMENT_OPTIONS: { value: EmploymentType; label: string }[] = [
  { value: 'full', label: 'Full-time' },
  { value: 'part', label: 'Part-time' },
  { value: 'temporary', label: 'Temporary' },
  { value: 'proj', label: 'Project' },
  { value: 'volunteer', label: 'Volunteer' },
  { value: 'probation', label: 'Probation' },
];

const SCHEDULE_OPTIONS: { value: ScheduleType; label: string }[] = [
  { value: 'fullDay', label: 'Full day' },
  { value: 'shift', label: 'Shift' },
  { value: 'flexible', label: 'Flexible' },
  { value: 'remote', label: 'Remote' },
  { value: 'travel', label: 'Travel' },
  { value: 'external', label: 'External' },
];

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, onLoading }) => {
  const [q, setQ] = useState('');
  const [location, setLocation] = useState('');
  const [experience, setExperience] = useState<ExperienceLevel | ''>('');
  const [employmentType, setEmploymentType] = useState<EmploymentType | ''>('');
  const [scheduleType, setScheduleType] = useState<ScheduleType | ''>('');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [skills, setSkills] = useState('');

  const handleSearch = useCallback(async () => {
    onLoading(true);
    try {
      const result = await searchJobs({
        q,
        location: location || null,
        experience: experience || null,
        employment_type: employmentType || null,
        schedule_type: scheduleType || null,
        salary_min: salaryMin ? Number(salaryMin) : null,
        salary_max: salaryMax ? Number(salaryMax) : null,
        skills: skills ? skills.split(',').map(s => s.trim()).filter(Boolean) : [],
        page: 0,
        size: 20,
      });
      onSearch(result);
    } catch (err) {
      console.error('Search failed:', err);
      alert('Search failed. Check that the backend is running.');
    } finally {
      onLoading(false);
    }
  }, [q, location, experience, employmentType, scheduleType, salaryMin, salaryMax, skills, onSearch, onLoading]);

  return (
    <div className="search-bar">
      <h1>Job Aggregator</h1>
      <div className="search-row">
        <input
          type="text"
          placeholder="Job title, keyword..."
          value={q}
          onChange={e => setQ(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
        />
        <input
          type="text"
          placeholder="Location (e.g. Moscow)"
          value={location}
          onChange={e => setLocation(e.target.value)}
        />
        <input
          type="text"
          placeholder="Skills (comma-separated)"
          value={skills}
          onChange={e => setSkills(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      <div className="filters-row">
        <select value={experience} onChange={e => setExperience(e.target.value as ExperienceLevel | '')}>
          <option value="">Any experience</option>
          {EXPERIENCE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select value={employmentType} onChange={e => setEmploymentType(e.target.value as EmploymentType | '')}>
          <option value="">Any employment</option>
          {EMPLOYMENT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select value={scheduleType} onChange={e => setScheduleType(e.target.value as ScheduleType | '')}>
          <option value="">Any schedule</option>
          {SCHEDULE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <input
          type="number"
          placeholder="Salary min"
          value={salaryMin}
          onChange={e => setSalaryMin(e.target.value)}
        />
        <input
          type="number"
          placeholder="Salary max"
          value={salaryMax}
          onChange={e => setSalaryMax(e.target.value)}
        />
      </div>
    </div>
  );
};
