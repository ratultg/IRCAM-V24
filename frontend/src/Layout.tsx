import React from 'react';
import { Box, CssBaseline } from '@mui/material';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Box sx={{ display: 'flex', minHeight: '100vh' }}>
    <CssBaseline />
    <Sidebar />
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <Topbar />
      <Box component="main" sx={{ flex: 1, p: 2, bgcolor: '#f5f5f5' }}>
        {children}
      </Box>
    </Box>
  </Box>
);

export default Layout;
