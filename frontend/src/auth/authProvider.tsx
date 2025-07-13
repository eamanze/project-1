'use client';

import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserSession,
  CognitoUserAttribute,
} from 'amazon-cognito-identity-js';
import { createContext, useContext, useEffect, useState } from 'react';
import { userPool } from './cognito';

type AuthContextType = {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (
    email: string,
    password: string,
    firstName: string,
    lastName: string
  ) => Promise<CognitoUser>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const login = async (email: string, password: string) => {
    const user = new CognitoUser({ Username: email, Pool: userPool });
    const authDetails = new AuthenticationDetails({ Username: email, Password: password });

    return new Promise<void>((resolve, reject) => {
      user.authenticateUser(authDetails, {
        onSuccess: async (session: CognitoUserSession) => {
          const idToken = session.getIdToken().getJwtToken();

          const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/login/`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: idToken }),
          });

          if (!res.ok) {
            return reject(new Error('Backend login failed'));
          }

          setIsAuthenticated(true);
          resolve();
        },
        onFailure: reject,
      });
    });
  };

  const signup = async (
    email: string,
    password: string,
    firstName: string,
    lastName: string
  ): Promise<CognitoUser> =>
    new Promise((resolve, reject) => {
      const attributes = [
        new CognitoUserAttribute({ Name: 'given_name', Value: firstName }),
        new CognitoUserAttribute({ Name: 'family_name', Value: lastName }),
      ];

      userPool.signUp(email, password, attributes, [], (err, result) => {
        if (err || !result?.user) return reject(err || new Error('Signup failed'));
        resolve(result.user);
      });
    });

  const logout = () => {
    const currentUser = userPool.getCurrentUser();
    currentUser?.signOut();

    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/logout/`, {
      method: 'POST',
      credentials: 'include',
    });

    setIsAuthenticated(false);
  };

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/session/`, {
          method: 'GET',
          credentials: 'include',
        });
        setIsAuthenticated(res.ok);
      } catch {
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
