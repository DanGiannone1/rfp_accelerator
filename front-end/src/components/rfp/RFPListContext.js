import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';

const RFPListContext = createContext();

export const useRFPList = () => useContext(RFPListContext);

export const RFPListProvider = ({ children }) => {
  const [rfps, setRFPs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchRFPs = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:5000/available-rfps');
      const data = await response.json();
      setRFPs(data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching RFPs:', error);
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRFPs();
  }, [fetchRFPs]);

  return (
    <RFPListContext.Provider value={{ rfps, setRFPs, isLoading, fetchRFPs }}>
      {children}
    </RFPListContext.Provider>
  );
};