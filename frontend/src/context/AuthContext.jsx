import React, { createContext, useContext, useState, useEffect } from 'react';
import { cyberSound } from '../utils/cyberSound';

export const DEMO_PERSONAS = [
  {
    id: 'analyst_senior',
    reviewer_id: 'REV-00892',
    name: 'Alex Vance',
    email: 'alex.vance@chargeback-guardian.ai',
    role: 'Senior Dispute Specialist',
    tier: 'Tier 3 Reviewer',
    badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    avatarInitials: 'AV',
    clearance: 'FULL_DISPUTE_AUTHORIZATION',
  },
  {
    id: 'lead_fraud',
    reviewer_id: 'REV-00104',
    name: 'Elena Rostova',
    email: 'elena.rostova@chargeback-guardian.ai',
    role: 'Fraud Operations Lead',
    tier: 'Supervisor / Lead',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    avatarInitials: 'ER',
    clearance: 'EXECUTIVE_CLEARANCE',
  },
  {
    id: 'compliance_officer',
    reviewer_id: 'AUDIT-001',
    name: 'Marcus Thorne',
    email: 'marcus.thorne@chargeback-guardian.ai',
    role: 'Compliance & Audit Officer',
    tier: 'Audit Inspector',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    avatarInitials: 'MT',
    clearance: 'AUDIT_SUPERVISOR',
  },
];

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('guardian_auth_user');
      return stored ? JSON.parse(stored) : DEMO_PERSONAS[0];
    } catch {
      return DEMO_PERSONAS[0];
    }
  });

  useEffect(() => {
    try {
      if (user) {
        localStorage.setItem('guardian_auth_user', JSON.stringify(user));
      } else {
        localStorage.removeItem('guardian_auth_user');
      }
    } catch {}
  }, [user]);

  const loginWithPersona = (personaId) => {
    const selected = DEMO_PERSONAS.find((p) => p.id === personaId) || DEMO_PERSONAS[0];
    setUser(selected);
    cyberSound.playSuccess();
    return selected;
  };

  const loginWithCredentials = (email, password) => {
    // Demo credential authentication
    const matched = DEMO_PERSONAS.find((p) => p.email.toLowerCase() === email.trim().toLowerCase());
    const finalUser = matched || {
      id: 'custom_analyst',
      reviewer_id: 'REV-00999',
      name: email.split('@')[0].toUpperCase(),
      email: email,
      role: 'Dispute Analyst',
      tier: 'Standard Reviewer',
      badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
      avatarInitials: email.substring(0, 2).toUpperCase(),
      clearance: 'STANDARD_REVIEWER',
    };
    setUser(finalUser);
    cyberSound.playSuccess();
    return finalUser;
  };

  const logout = () => {
    setUser(null);
    cyberSound.playClick();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        personas: DEMO_PERSONAS,
        loginWithPersona,
        loginWithCredentials,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
