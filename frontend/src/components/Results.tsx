import React from 'react';
import { JobOffer, SearchResult } from '../types';

interface ResultsProps {
  result: SearchResult;
}

export const Results: React.FC<ResultsProps> = ({ result }) => {
  if (result.results.length === 0) {
    return (
      <div className="results">
        <p>No jobs found (total: {result.total}).</p>
      </div>
    );
  }

  return (
    <div className="results">
      <p className="summary">
        Found <strong>{result.total}</strong> jobs (page {result.page + 1}, cached: {result.cached ? 'yes' : 'no'})
      </p>
      <ul className="job-list">
        {result.results.map(job => (
          <li key={job.id} className="job-card">
            <h3>
              <a href={job.alternate_url} target="_blank" rel="noopener noreferrer">
                {job.title}
              </a>
            </h3>
            <p className="company">{job.company} — {job.location}</p>
            <p className="salary">
              {job.salary_from && job.salary_to
                ? `${job.salary_from} – ${job.salary_to} ${job.currency}`
                : job.salary_from
                ? `From ${job.salary_from} ${job.currency}`
                : job.salary_to
                ? `Up to ${job.salary_to} ${job.currency}`
                : 'Not specified'}
            </p>
            <div className="meta">
              {job.experience_required && <span>{job.experience_required}</span>}
              {job.employment_type && <span>{job.employment_type}</span>}
              {job.schedule_type && <span>{job.schedule_type}</span>}
            </div>
            {job.key_skills.length > 0 && (
              <div className="skills">
                {job.key_skills.map(skill => (
                  <span key={skill} className="skill-tag">{skill}</span>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
