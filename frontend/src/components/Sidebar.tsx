import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MapIcon from '@mui/icons-material/Map';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AssessmentIcon from '@mui/icons-material/Assessment';
import SettingsIcon from '@mui/icons-material/Settings';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon /> },
  { text: 'Zones', icon: <MapIcon /> },
  { text: 'Alarms/Events', icon: <NotificationsIcon /> },
  { text: 'Analytics', icon: <AssessmentIcon /> },
  { text: 'Notifications', icon: <NotificationsIcon /> },
  { text: 'System Health', icon: <HealthAndSafetyIcon /> },
  { text: 'Settings', icon: <SettingsIcon /> },
];

const Sidebar: React.FC = () => (
  <Drawer variant="permanent" anchor="left">
    <List>
      {menuItems.map((item) => (
        <ListItem button key={item.text}>
          <ListItemIcon>{item.icon}</ListItemIcon>
          <ListItemText primary={item.text} />
        </ListItem>
      ))}
    </List>
  </Drawer>
);

export default Sidebar;
