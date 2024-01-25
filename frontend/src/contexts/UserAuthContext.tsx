import React, { createContext, useState, useContext, FunctionComponent, ReactNode } from 'react';

// Define user context type
interface UserAuthContextType {
    isAuthenticated: boolean;
    login: () => void;
    logout: () => void;
};

// Define default values and create the context
const defaultAuthContext: UserAuthContextType = {
    isAuthenticated: false,
    login: () => {},
    logout: () => {}
};

// Initialize context with default values
export const UserAuthContext = createContext<UserAuthContextType>(defaultAuthContext);

// Create custom hook for easy access
export const useUserAuth = () => useContext(UserAuthContext);

interface UserAuthProviderProps {
    children: ReactNode;
}

// Create context provider
export const UserAuthProvider: FunctionComponent<UserAuthProviderProps> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    
    const login = () => {
        setIsAuthenticated(true);
        // Additional login logic
    };

    const logout = () => {
        setIsAuthenticated(false);
        // Additional logout logic
    };

    return (
        <UserAuthContext.Provider value={{ isAuthenticated, login, logout }}>
            {children}
        </UserAuthContext.Provider>
    );
};
