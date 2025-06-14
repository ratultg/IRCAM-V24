import React from 'react';
import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';

const Topbar: React.FC = () => (
  <AppBar position="static" color="default" elevation={1}>
    <Toolbar>
      <Typography variant="h6" sx={{ flexGrow: 1 }}>
        IR Thermal Monitoring System
      </Typography>
      <Box>
        <Button color="primary" variant="outlined" sx={{ mr: 1 }}>
          Acknowledge All
        </Button>
        <Button color="primary" variant="contained">
          Export
        </Button>
      </Box>
    </Toolbar>
  </AppBar>
);

export default Topbar;
