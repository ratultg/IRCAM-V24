# IR Thermal Monitoring System Frontend: Single Source of Truth (SSOT)

> **Note:** This application is intended for single-user, local, or secure network deployment. No login/authentication will be implemented, and accessibility features (such as ARIA roles, keyboard navigation, and screen reader support) are not a requirement for this project.

---

## 1. Overview & Goals
- Single-user (engineer/operator), no concurrent users
- Local or secure network deployment
- Power-user features prioritized over multi-user support

---

## 2. Requirements & Constraints
- No login/authentication
- Accessibility not required, but UI should degrade gracefully on smaller screens
- Desktop is primary target; tablet basic support; mobile not officially supported

---

## 3. Technology Stack & Environment
- React (with TypeScript)
- UI Library: MUI (Material-UI) or Ant Design
- Charting: Recharts, Chart.js, or Plotly
- State Management: Redux Toolkit (with RTK Query)
- HTTP: Axios or Fetch API
- Styling: CSS-in-JS (styled-components, emotion) or CSS Modules
- Storybook: For UI component development and documentation (optional, use only during development; not required in production or on the Pi)

---

## 4. Deployment & Environment Setup
### Local Development
1. Install Node.js (LTS version) and npm or yarn.
2. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd IRCAM V24/frontend
   ```
3. Install dependencies:
   ```sh
   npm install
   # or
   yarn install
   ```
4. Set environment variables:
   - Create a `.env` file in the `frontend` directory if needed.
   - Example variables:
     ```env
     REACT_APP_API_BASE_URL=http://127.0.0.1:8000
     # Add other frontend-specific variables as needed
     ```
5. Start the development server:
   ```sh
   npm start
   # or
   yarn start
   ```
6. Access the app:
   - Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Deployment
1. Build the frontend:
   ```sh
   npm run build
   # or
   yarn build
   ```
2. Deploy the `build/` directory to your web server or static hosting (e.g., Nginx, Apache, Netlify, Vercel).
3. Set environment variables for production as needed (e.g., API base URL).
4. Ensure the backend API is accessible from the deployed frontend (CORS, network/firewall settings).

---

## 5. UI/UX Design
### 5.1 Navigation & Layout
- Sidebar Navigation (persistent on desktop, collapsible for smaller screens, icons + labels)
- Top bar: App name, current time, quick actions (e.g., acknowledge all alarms, export)
- Main content area: Displays selected page/component
- Optional: Breadcrumbs for deep navigation (e.g., Event > Frame Review)

#### Navigation Example (Sidebar)
```
| Dashboard        |
| Zones           |
| Alarms/Events   |
| Analytics       |
| Notifications   |
| System Health   |
```

### 5.2 Main Pages & Features
- Dashboard: Real-time monitoring, alarm status, quick actions, customizable widgets, data retention warnings
- Zones: Zone editor, list, configuration, multi-zone comparison
- Alarms/Events: Alarm/event history, acknowledge/reset, event review, batch export, annotation tools
- Analytics: Charts, heatmaps, export tools, automated report generation
- Notifications/Settings: Notification config, system settings, configuration backup/restore
- System Health: Health status, resource monitoring, live logs, maintenance tools

### 5.3 Feature-to-Component Mapping
- **Dashboard:**
  - **ThermalImageDisplay** (`/api/v1/thermal/real-time`, `/api/v1/zones`)
  - **ZoneOverlay** (`/api/v1/zones`, `/api/v1/zones/{zone_id}/average`)
  - **AlarmStatusIndicator** (`/api/v1/alarms/history`)
  - **WidgetContainer** (customizable widgets)
  - **DataRetentionWarning** (`/api/v1/health`)

- **Zones:**
  - **ZoneListTable** (`/api/v1/zones`)
  - **ZoneEditor** (`/api/v1/zones` GET/POST/DELETE)
  - **ZoneDetailsPanel** (`/api/v1/zones`, `/api/v1/zones/{zone_id}/average`)
  - **MultiZoneComparisonChart** (`/api/v1/analytics/trends`, `/api/v1/analytics/heatmap`, `/api/v1/analytics/anomalies`)

- **Alarms & Events:**
  - **AlarmHistoryTable** (`/api/v1/alarms/history`)
  - **AlarmDetailsDialog** (`/api/v1/alarms/history`, `/api/v1/alarms/acknowledge`)
  - **AcknowledgeAlarmButton** (`/api/v1/alarms/acknowledge`)
  - **EventListTable** (`/api/v1/events/{event_id}/frames`)
  - **EventFramePlayer** (`/api/v1/events/{event_id}/frames`, `/api/v1/events/{event_id}/frames.png`, `/api/v1/events/{event_id}/frames/blobs`)
  - **BatchExportDialog** (`/api/v1/frames/export`, `/api/v1/events/{event_id}/frames.png`)
  - **AnnotationTool** (frontend only)

- **Analytics:**
  - **AnalyticsChart** (`/api/v1/analytics/heatmap`, `/api/v1/analytics/trends`, `/api/v1/analytics/anomalies`)
  - **AnalyticsControls** (frontend only)
  - **AutomatedReportScheduler** (`/api/v1/reports`, `/api/v1/frames/export?overlay=stats`)

- **Notifications & Settings:**
  - **NotificationSettingsForm** (`/api/v1/notifications/settings`)
  - **SystemSettingsForm** (`/api/v1/settings`)
  - **ConfigBackupRestoreDialog** (`/api/v1/settings`, `/api/v1/database/backup`, `/api/v1/database/restore`)

- **System Health & Logs:**
  - **SystemHealthSummary** (`/api/v1/health`)
  - **ResourceMonitor** (`/api/v1/health`)
  - **LiveLogViewer** (if log API is available)
  - **MaintenanceToolsPanel** (`/api/v1/database/backup`, `/api/v1/database/restore`, `/api/v1/database/migrate`)

### 5.4 Wireframes & UI Mockups
Below are simple ASCII wireframes for each main page. Replace with digital mockups as needed.

#### Dashboard
```
+-------------------------------------------------------------+
| App Name        | Time         | [Acknowledge All] [Export] |
+-----------------+-------------------------------------------+
| Sidebar |  [Thermal Image Display]   [Alarm Status]         |
|         |  [Zone Overlays]           [Custom Widgets]       |
|         |  [Data Retention Warning]                        |
+-------------------------------------------------------------+
```

#### Zones
```
+-----------------+-------------------------------------------+
| Sidebar |  [Zone List/Table]   [Zone Editor/Preview]         |
|         |  [Zone Details Panel] [Multi-Zone Comparison]      |
+-------------------------------------------------------------+
```

#### Alarms/Events
```
+-----------------+-------------------------------------------+
| Sidebar |  [Alarm/Event History Table] [Alarm Details]       |
|         |  [Acknowledge/Reset]   [Event Frame Player]        |
|         |  [Batch Export]        [Annotation Tool]           |
+-------------------------------------------------------------+
```

#### Analytics
```
+-----------------+-------------------------------------------+
| Sidebar |  [Analytics Chart]   [Analytics Controls]          |
|         |  [Automated Report Scheduler]                      |
+-------------------------------------------------------------+
```

#### Notifications/Settings
```
+-----------------+-------------------------------------------+
| Sidebar |  [Notification Settings Form] [System Settings]    |
|         |  [Config Backup/Restore]                           |
+-------------------------------------------------------------+
```

#### System Health
```
+-----------------+-------------------------------------------+
| Sidebar |  [System Health Summary] [Resource Monitor]        |
|         |  [Live Log Viewer]     [Maintenance Tools]         |
+-------------------------------------------------------------+
```

### 5.5 Detailed Component Specifications
Below are example specifications for key components. Expand as needed for all major components.

#### ThermalImageDisplay
- **Props:**
  - `frameData: number[]` (32x24 array)
  - `zones: Zone[]`
  - `overlays: Overlay[]`
  - `loading: boolean`
  - `error: string | null`
- **State:**
  - `hoveredZoneId: string | null`
- **Events:**
  - `onZoneClick(zoneId: string)`
- **Data Dependencies:**
  - `/api/v1/thermal/real-time`, `/api/v1/zones`
- **Example Usage:**
  ```jsx
  <ThermalImageDisplay frameData={frame} zones={zones} overlays={overlays} loading={isLoading} error={error} onZoneClick={handleZoneClick} />
  ```

#### AlarmHistoryTable
- **Props:**
  - `alarms: Alarm[]`
  - `loading: boolean`
  - `error: string | null`
- **State:**
  - `selectedAlarmId: string | null`
- **Events:**
  - `onAcknowledge(alarmId: string)`
- **Data Dependencies:**
  - `/api/v1/alarms/history`, `/api/v1/alarms/acknowledge`

#### ZoneEditor
- **Props:**
  - `zone: Zone | null`
  - `onSave(zone: Zone)`
  - `onCancel()`
- **State:**
  - `editValues: Partial<Zone>`
- **Events:**
  - `onFieldChange(field: string, value: any)`
- **Data Dependencies:**
  - `/api/v1/zones` (GET/POST/DELETE)

---

## 6. Data Flow & State Management
- Global State: Redux Toolkit (alarms, zones, events, health, notifications, settings, analytics, dashboard layout)
- Local State: React useState/useReducer for dialogs, forms, temporary selections, etc.
- Data Fetching: RTK Query or custom hooks for API data, caching, invalidation. Each resource has a dedicated slice/service. Use optimistic updates for fast UI.
- State Structure Example:
```
state = {
  alarms: { list: [], status: {}, loading: false, error: null },
  zones: { list: [], selectedZone: null, loading: false },
  events: { list: [], selectedEvent: null, frames: [], loading: false },
  health: { status: {}, resource: {}, loading: false },
  notifications: { settings: {}, deliveryLog: [] },
  settings: { ... },
  analytics: { trends: {}, heatmaps: {}, anomalies: {} },
  dashboard: { layout: {}, widgets: {} },
}
```
- Patterns: Use selectors, thunks/RTK Query endpoints, Context for rarely-changing data, store loading/error state, use localStorage/IndexedDB for dashboard layout, user preferences, unsaved annotations

---

## 7. API Contracts & Integration
- API Mapping: Each feature mapped to backend endpoints (see Feature-to-Component Mapping)
- API Contract Documentation: For each endpoint, specify request/response format, error codes, and examples

### Example: `/api/v1/alarms/history`
- **Request:**
  - `GET /api/v1/alarms/history`
- **Response:**
  ```json
  [
    {"alarm_id": 1, "zone_id": 1, "timestamp": "2025-06-10T12:34:56Z", "acknowledged": false, "max_temp": 30.2}
  ]
  ```
- **Error:**
  - `500 Internal Server Error` with `{ "detail": "Database unavailable" }`

---

## 8. Error Handling, Loading, Performance, and Security
### 8.1 Error Handling & Loading
- Show a global loading spinner for full-page data loads (e.g., initial dashboard, analytics page)
- Use per-component spinners or skeleton loaders for partial data (e.g., table rows, charts, widgets)
- For long-running actions (e.g., batch export, report generation), show progress bars or status indicators
- Disable relevant UI controls while loading to prevent duplicate actions
- Display clear, actionable error messages near the affected component (e.g., “Failed to load alarms. [Retry]”)
- For critical errors (e.g., cannot connect to backend), show a persistent banner or modal with troubleshooting steps
- Provide retry/cancel options for recoverable errors
- Log errors to the browser console for developer troubleshooting; optionally send logs to backend if supported
- For form submissions, show field-level validation errors and a summary at the top if multiple errors occur
- Use error boundaries in React to catch and gracefully handle unexpected rendering errors
- Always provide feedback: never leave the user wondering if something is happening
- Use color and iconography to distinguish between loading, success, warning, and error states
- For repeated failures, suggest next steps (e.g., “Check your network connection or contact support.”)
- API hooks return `{ data, isLoading, error, refetch }`
- Components: show spinner if `isLoading`, error message if `error`, render normally if `data`

### 8.2 Performance
- Use virtualization for large tables/lists (e.g., alarms, events)
- Implement lazy loading or pagination for historical data and analytics
- Cache frequently accessed data (e.g., zones, settings) in Redux/RTK Query
- Throttle or debounce real-time updates to avoid UI overload

### 8.3 Security & Privacy
- Validate all user input on the frontend before sending to the backend
- Escape/encode all dynamic content to prevent XSS
- Do not store sensitive data (e.g., raw frames, analytics) in localStorage
- Use HTTPS for all API calls in production

---

## 9. Testing & QA Plan
### Unit Testing
- Use Jest and React Testing Library for all React components, hooks, and utility functions
- Write tests for all component states: loading, error, empty, and normal data
- Mock API calls and test edge cases (e.g., failed fetch, invalid data)
### Integration Testing
- Test data flow between components (e.g., dashboard widgets updating from global state)
- Simulate user interactions (e.g., alarm acknowledge, zone edit) and verify UI updates and API calls
- Test routing/navigation between main pages
### End-to-End (E2E) Testing
- Use Cypress or Playwright to automate real user flows:
  - Dashboard load, alarm acknowledge, event playback, export, settings change, etc.
- Test error and loading states in the browser
- Run E2E tests in CI for every major change
### Acceptance Criteria
- Each feature works as described in the spec
- All error/loading states are handled gracefully
- No critical or high-severity bugs in production
### Manual QA
- Maintain a checklist for manual testing of critical workflows before releases
- Test on all supported browsers and screen sizes
### Continuous Integration (CI)
- Run all tests (unit, integration, E2E) on every pull request and before deployment
- Block merges on test failures

---

## 10. Implementation Roadmap
1. Scaffold frontend project (React + TypeScript)
2. Implement API service layer and state management (Redux Toolkit + RTK Query)
3. Build Dashboard (real-time data, alarm status, widgets)
4. Add Zones page (list, editor, comparison)
5. Add Alarms/Events (history, acknowledge, playback, export)
6. Add Analytics (charts, reports)
7. Add Notifications/Settings (forms, backup/restore)
8. Add System Health/Logs (health, resource, logs, maintenance)
9. Polish UI, add error handling, and QA
10. Final review and user feedback

---

## 11. Stakeholder Review Checklist
- [ ] All features and requirements are covered in the spec
- [ ] Wireframes/mockups reviewed and approved
- [ ] API contracts validated against backend
- [ ] Performance guidelines included
- [ ] Testing and QA plan approved
- [ ] Implementation roadmap agreed upon

---

## 12. Implementation Checklist (Atomic Steps)

> **Status Legend:**
> - ⬜ To Do
> - 🟡 In Progress
> - 🟢 Done
> - 🔴 Blocked

### 1. Project Setup
- **Initialize git repository and .gitignore**
  - Status: ⬜
  - Acceptance: Git repo exists, .gitignore covers node_modules, build, env files
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 4. Deployment & Environment Setup
- **Create project directory structure**
  - Status: ⬜
  - Acceptance: All main folders (src, components, hooks, store, api, assets) exist
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 3. Technology Stack & Environment
- **Initialize package.json**
  - Status: ⬜
  - Acceptance: package.json with project metadata, scripts
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 3. Technology Stack & Environment
- **Install React, TypeScript, dependencies**
  - Status: ⬜
  - Acceptance: All core dependencies installed, app runs
  - Responsible: Frontend Dev
  - Dependencies: package.json
  - Spec: 3. Technology Stack & Environment
- **Set up ESLint, Prettier, TS config**
  - Status: ⬜
  - Acceptance: Linting, formatting, and type checking work in CI
  - Responsible: Frontend Dev
  - Dependencies: package.json
  - Spec: 3. Technology Stack & Environment
- **Add README and update**
  - Status: ⬜
  - Acceptance: README covers setup, usage, and project info
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 4. Deployment & Environment Setup

### 2. Environment & Tooling
- **Create .env and .env.example files**
  - Status: ⬜
  - Acceptance: .env files exist, app loads config from env
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 4. Deployment & Environment Setup
- **Add scripts for dev, build, lint, test, format**
  - Status: ⬜
  - Acceptance: Scripts work as expected
  - Responsible: Frontend Dev
  - Dependencies: package.json
  - Spec: 4. Deployment & Environment Setup
- **Set up Storybook for component development**
  - Status: ⬜
  - Acceptance: Storybook runs, at least one component documented
  - Responsible: Frontend Dev
  - Dependencies: React, components
  - Spec: 3. Technology Stack, 5. UI/UX Design
- **Configure VSCode settings and recommended extensions**
  - Status: ⬜
  - Acceptance: .vscode/settings.json exists, recommended extensions listed
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 3. Technology Stack & Environment

### 3. Core Architecture
- **Set up routing (React Router)**
  - Status: ⬜
  - Acceptance: Navigation between all main pages works
  - Responsible: Frontend Dev
  - Dependencies: App shell
  - Spec: 5.1 Navigation & Layout
- **Set up Redux Toolkit store and slices**
  - Status: ⬜
  - Acceptance: Store initialized, at least one slice with actions
  - Responsible: Frontend Dev
  - Dependencies: None
  - Spec: 6. Data Flow & State Management
- **Set up RTK Query for API integration**
  - Status: ⬜
  - Acceptance: API hooks/services work, data loads in UI
  - Responsible: Frontend Dev
  - Dependencies: Store
  - Spec: 6. Data Flow, 7. API Contracts
- **Create global theme and style provider (MUI/AntD)**
  - Status: ⬜
  - Acceptance: Theme provider wraps app, theme switch works
  - Responsible: Frontend Dev
  - Dependencies: App shell
  - Spec: 3. Technology Stack, 5. UI/UX
- **Implement error boundary component**
  - Status: ⬜
  - Acceptance: Error boundary catches and displays errors
  - Responsible: Frontend Dev
  - Dependencies: App shell
  - Spec: 8. Error Handling

### 4. UI Foundation
- **Implement App shell (sidebar, top bar, main content area)**
  - Status: ⬜
  - Acceptance: Sidebar, top bar, main area render, responsive
  - Responsible: Frontend Dev
  - Dependencies: Directory structure
  - Spec: 5.1 Navigation, 5.4 Wireframes
- **Add navigation structure and routes**
  - Status: ⬜
  - Acceptance: All main routes render correct page
  - Responsible: Frontend Dev
  - Dependencies: Routing
  - Spec: 5.1 Navigation & Layout
- **Add responsive layout and breakpoints**
  - Status: ⬜
  - Acceptance: Layout adapts to desktop/tablet
  - Responsible: Frontend Dev
  - Dependencies: App shell
  - Spec: 5.1 Navigation & Layout
- **Add loading spinner and skeleton components**
  - Status: ⬜
  - Acceptance: Loading states visible for all async data
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 8.1 Error Handling & Loading
- **Add notification/toast system**
  - Status: ⬜
  - Acceptance: User sees feedback for actions/errors
  - Responsible: Frontend Dev
  - Dependencies: App shell
  - Spec: 8.1 Error Handling & Loading

### 5. Feature Implementation (by Feature/Page)
#### Dashboard
- **Fetch and display real-time thermal image**
  - Status: ⬜
  - Acceptance: Image loads from API, updates in real time
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Overlay zones and temperature data**
  - Status: ⬜
  - Acceptance: Zones overlay on image, data updates
  - Responsible: Frontend Dev
  - Dependencies: Thermal image
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Show alarm status and quick actions**
  - Status: ⬜
  - Acceptance: Alarm status visible, actions work
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add customizable widgets**
  - Status: ⬜
  - Acceptance: User can add/remove/rearrange widgets
  - Responsible: Frontend Dev
  - Dependencies: App shell
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Show data retention warnings**
  - Status: ⬜
  - Acceptance: Warning appears when storage is low
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping

#### Zones
- **List all zones**
  - Status: ⬜
  - Acceptance: Table of zones loads from API
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add zone editor (create/edit/delete)**
  - Status: ⬜
  - Acceptance: User can add/edit/delete zones, changes persist
  - Responsible: Frontend Dev
  - Dependencies: List all zones
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Implement multi-zone comparison**
  - Status: ⬜
  - Acceptance: User can compare zones visually
  - Responsible: Frontend Dev
  - Dependencies: List all zones
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add zone details panel**
  - Status: ⬜
  - Acceptance: Details panel shows info for selected zone
  - Responsible: Frontend Dev
  - Dependencies: List all zones
  - Spec: 5.2 Main Pages, 5.3 Mapping

#### Alarms/Events
- **List alarm/event history**
  - Status: ⬜
  - Acceptance: Table loads from API, paginated
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Implement acknowledge/reset actions**
  - Status: ⬜
  - Acceptance: User can acknowledge/reset alarms
  - Responsible: Frontend Dev
  - Dependencies: List alarm/event history
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Show event frame player**
  - Status: ⬜
  - Acceptance: User can play back event frames
  - Responsible: Frontend Dev
  - Dependencies: List alarm/event history
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add batch export functionality**
  - Status: ⬜
  - Acceptance: User can export selected events/alarms
  - Responsible: Frontend Dev
  - Dependencies: List alarm/event history
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add annotation tool**
  - Status: ⬜
  - Acceptance: User can annotate frames/events
  - Responsible: Frontend Dev
  - Dependencies: Event frame player
  - Spec: 5.2 Main Pages, 5.3 Mapping

#### Analytics
- **Display charts, heatmaps, trends**
  - Status: ⬜
  - Acceptance: Analytics data loads, charts render
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add export tools**
  - Status: ⬜
  - Acceptance: User can export analytics data
  - Responsible: Frontend Dev
  - Dependencies: Analytics charts
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Implement automated report scheduler**
  - Status: ⬜
  - Acceptance: User can schedule/download reports
  - Responsible: Frontend Dev
  - Dependencies: Analytics charts
  - Spec: 5.2 Main Pages, 5.3 Mapping

#### Notifications/Settings
- **Implement notification settings form**
  - Status: ⬜
  - Acceptance: User can configure notifications
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Implement system settings form**
  - Status: ⬜
  - Acceptance: User can configure system settings
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add config backup/restore dialog**
  - Status: ⬜
  - Acceptance: User can backup/restore config
  - Responsible: Frontend Dev
  - Dependencies: System settings form
  - Spec: 5.2 Main Pages, 5.3 Mapping

#### System Health
- **Show system health summary**
  - Status: ⬜
  - Acceptance: Health data loads, summary visible
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add resource monitor**
  - Status: ⬜
  - Acceptance: Resource usage visible in UI
  - Responsible: Frontend Dev
  - Dependencies: System health summary
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Implement live log viewer**
  - Status: ⬜
  - Acceptance: Logs stream in real time
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 5.2 Main Pages, 5.3 Mapping
- **Add maintenance tools panel**
  - Status: ⬜
  - Acceptance: User can trigger backup/restore/migrate
  - Responsible: Frontend Dev
  - Dependencies: System health summary
  - Spec: 5.2 Main Pages, 5.3 Mapping

### 6. State Management
- **Create slices/services for all resources**
  - Status: ⬜
  - Acceptance: Slices/services exist for all data types
  - Responsible: Frontend Dev
  - Dependencies: Store setup
  - Spec: 6. Data Flow & State Management
- **Implement selectors and async thunks/endpoints**
  - Status: ⬜
  - Acceptance: Selectors and async actions work for all slices
  - Responsible: Frontend Dev
  - Dependencies: Slices/services
  - Spec: 6. Data Flow & State Management
- **Add local state for UI controls and dialogs**
  - Status: ⬜
  - Acceptance: All dialogs/forms have local state
  - Responsible: Frontend Dev
  - Dependencies: UI foundation
  - Spec: 6. Data Flow & State Management
- **Persist user preferences**
  - Status: ⬜
  - Acceptance: Preferences (e.g., dashboard layout) persist
  - Responsible: Frontend Dev
  - Dependencies: Local state
  - Spec: 6. Data Flow & State Management

### 7. API Integration
- **Define API endpoints and types**
  - Status: ⬜
  - Acceptance: All endpoints/types defined in code
  - Responsible: Frontend Dev
  - Dependencies: API contract
  - Spec: 7. API Contracts & Integration
- **Implement API hooks/services**
  - Status: ⬜
  - Acceptance: All API hooks/services return correct data
  - Responsible: Frontend Dev
  - Dependencies: Endpoints/types
  - Spec: 7. API Contracts & Integration
- **Add error/loading state handling for all API calls**
  - Status: ⬜
  - Acceptance: All API calls handle error/loading
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 8.1 Error Handling & Loading
- **Mock API for Storybook/testing**
  - Status: ⬜
  - Acceptance: Mocked data available in Storybook/tests
  - Responsible: Frontend Dev
  - Dependencies: API hooks
  - Spec: 7. API Contracts & Integration

### 8. Error Handling & UX
- **Add global and per-component error handling**
  - Status: ⬜
  - Acceptance: All errors are caught and displayed
  - Responsible: Frontend Dev
  - Dependencies: Error boundary
  - Spec: 8.1 Error Handling & Loading
- **Add user-friendly error messages and retry options**
  - Status: ⬜
  - Acceptance: All errors have clear messages and retry
  - Responsible: Frontend Dev
  - Dependencies: Error handling
  - Spec: 8.1 Error Handling & Loading
- **Add form validation and feedback**
  - Status: ⬜
  - Acceptance: All forms validate input and show feedback
  - Responsible: Frontend Dev
  - Dependencies: Forms
  - Spec: 8.1 Error Handling & Loading
- **Add accessibility checks for critical actions**
  - Status: ⬜
  - Acceptance: Keyboard navigation and ARIA for key actions
  - Responsible: Frontend Dev
  - Dependencies: UI foundation
  - Spec: 2. Requirements & Constraints

### 9. Testing
- **Write unit tests for all components and hooks**
  - Status: ⬜
  - Acceptance: 80%+ coverage, all logic tested
  - Responsible: QA
  - Dependencies: Components/hooks
  - Spec: 9. Testing & QA Plan
- **Write integration tests for data flow and user actions**
  - Status: ⬜
  - Acceptance: All main flows tested
  - Responsible: QA
  - Dependencies: Unit tests
  - Spec: 9. Testing & QA Plan
- **Write E2E tests for main user flows**
  - Status: ⬜
  - Acceptance: All critical flows tested in browser
  - Responsible: QA
  - Dependencies: Integration tests
  - Spec: 9. Testing & QA Plan
- **Add test coverage reporting**
  - Status: ⬜
  - Acceptance: Coverage report generated in CI
  - Responsible: QA
  - Dependencies: Unit/integration tests
  - Spec: 9. Testing & QA Plan

### 10. Documentation
- **Document all components in Storybook**
  - Status: ⬜
  - Acceptance: All components have stories
  - Responsible: Frontend Dev
  - Dependencies: Components
  - Spec: 10. Documentation
- **Update README with usage and setup instructions**
  - Status: ⬜
  - Acceptance: README is up to date
  - Responsible: Frontend Dev
  - Dependencies: All features
  - Spec: 10. Documentation
- **Add API contract documentation**
  - Status: ⬜
  - Acceptance: API docs match backend and code
  - Responsible: Frontend Dev
  - Dependencies: API contract
  - Spec: 7. API Contracts & Integration

### 11. Deployment
- **Set up build and deployment scripts**
  - Status: ⬜
  - Acceptance: Scripts work for build/deploy
  - Responsible: Frontend Dev
  - Dependencies: package.json
  - Spec: 4. Deployment & Environment Setup
- **Configure environment variables for production**
  - Status: ⬜
  - Acceptance: .env.production exists, app loads config
  - Responsible: Frontend Dev
  - Dependencies: Build scripts
  - Spec: 4. Deployment & Environment Setup
- **Test production build locally**
  - Status: ⬜
  - Acceptance: Build runs locally, no errors
  - Responsible: Frontend Dev
  - Dependencies: Build scripts
  - Spec: 4. Deployment & Environment Setup
- **Deploy to target environment**
  - Status: ⬜
  - Acceptance: App is live and accessible
  - Responsible: Frontend Dev
  - Dependencies: Test prod build
  - Spec: 4. Deployment & Environment Setup

### 12. Review & QA
- **Manual QA on all supported browsers/devices**
  - Status: ⬜
  - Acceptance: All features work on supported browsers/devices
  - Responsible: QA
  - Dependencies: Deploy to target
  - Spec: 12. Review & QA
- **Review against spec and stakeholder checklist**
  - Status: ⬜
  - Acceptance: All spec items checked off
  - Responsible: QA
  - Dependencies: Manual QA
  - Spec: 11. Stakeholder Review Checklist
- **Final code review and cleanup**
  - Status: ⬜
  - Acceptance: No critical issues, code is clean
  - Responsible: Frontend Dev
  - Dependencies: All features
  - Spec: 12. Review & QA

---

## 13. API & Function Mapping for Implementation Checklist

### Dashboard
- **Fetch and display real-time thermal image**
  - API: `GET /api/v1/thermal/real-time`
  - Frontend: `useGetThermalRealTimeQuery` (RTK Query hook)
  - Component: `ThermalImageDisplay`
- **Overlay zones and temperature data**
  - API: `GET /api/v1/zones`, `GET /api/v1/zones/{zone_id}/average`
  - Frontend: `useGetZonesQuery`, `useGetZoneAverageQuery(zone_id)`
  - Component: `ZoneOverlay`, `ThermalImageDisplay`
- **Show alarm status and quick actions**
  - API: `GET /api/v1/alarms/history`, `POST /api/v1/alarms/acknowledge`
  - Frontend: `useGetAlarmsHistoryQuery`, `useAcknowledgeAlarmMutation`
  - Component: `AlarmStatusIndicator`, `AcknowledgeAlarmButton`
- **Add customizable widgets**
  - API: N/A (frontend state)
  - Frontend: Widget management functions (`addWidget`, `removeWidget`, etc.)
  - Component: `WidgetContainer`
- **Show data retention warnings**
  - API: `GET /api/v1/health`
  - Frontend: `useGetHealthQuery`
  - Component: `DataRetentionWarning`

### Zones
- **List all zones**
  - API: `GET /api/v1/zones`
  - Frontend: `useGetZonesQuery`
  - Component: `ZoneListTable`
- **Add zone editor (create/edit/delete)**
  - API: `POST /api/v1/zones`, `DELETE /api/v1/zones/{zone_id}`
  - Frontend: `useCreateZoneMutation`, `useDeleteZoneMutation`
  - Component: `ZoneEditor`
- **Implement multi-zone comparison**
  - API: `GET /api/v1/analytics/trends`, `GET /api/v1/analytics/heatmap`, `GET /api/v1/analytics/anomalies`
  - Frontend: `useGetAnalyticsTrendsQuery`, `useGetAnalyticsHeatmapQuery`, `useGetAnalyticsAnomaliesQuery`
  - Component: `MultiZoneComparisonChart`
- **Add zone details panel**
  - API: `GET /api/v1/zones/{zone_id}/average`
  - Frontend: `useGetZoneAverageQuery(zone_id)`
  - Component: `ZoneDetailsPanel`

### Alarms/Events
- **List alarm/event history**
  - API: `GET /api/v1/alarms/history`, `GET /api/v1/events/{event_id}/frames`
  - Frontend: `useGetAlarmsHistoryQuery`, `useGetEventFramesQuery(event_id)`
  - Component: `AlarmHistoryTable`, `EventListTable`
- **Implement acknowledge/reset actions**
  - API: `POST /api/v1/alarms/acknowledge`
  - Frontend: `useAcknowledgeAlarmMutation`
  - Component: `AcknowledgeAlarmButton`, `AlarmDetailsDialog`
- **Show event frame player**
  - API: `GET /api/v1/events/{event_id}/frames`, `GET /api/v1/events/{event_id}/frames.png`, `GET /api/v1/events/{event_id}/frames/blobs`
  - Frontend: `useGetEventFramesQuery`, `useGetEventFramesPngQuery`, `useGetEventFramesBlobsQuery`
  - Component: `EventFramePlayer`
- **Add batch export functionality**
  - API: `GET /api/v1/frames/export`, `GET /api/v1/events/{event_id}/frames.png`
  - Frontend: `useExportFramesQuery`, `useGetEventFramesPngQuery`
  - Component: `BatchExportDialog`
- **Add annotation tool**
  - API: N/A (frontend only, local/browser storage)
  - Frontend: Annotation state management functions
  - Component: `AnnotationTool`

### Analytics
- **Display charts, heatmaps, trends**
  - API: `GET /api/v1/analytics/heatmap`, `GET /api/v1/analytics/trends`, `GET /api/v1/analytics/anomalies`
  - Frontend: `useGetAnalyticsHeatmapQuery`, `useGetAnalyticsTrendsQuery`, `useGetAnalyticsAnomaliesQuery`
  - Component: `AnalyticsChart`
- **Add export tools**
  - API: `GET /api/v1/frames/export?overlay=stats`
  - Frontend: `useExportFramesStatsQuery`
  - Component: `AnalyticsChart`, `ExportButton`
- **Implement automated report scheduler**
  - API: `GET /api/v1/reports`, `GET /api/v1/frames/export?overlay=stats`
  - Frontend: `useGetReportsQuery`, `useExportFramesStatsQuery`
  - Component: `AutomatedReportScheduler`

### Notifications/Settings
- **Implement notification settings form**
  - API: `GET /api/v1/notifications/settings`, `POST /api/v1/notifications/settings`
  - Frontend: `useGetNotificationSettingsQuery`, `useUpdateNotificationSettingsMutation`
  - Component: `NotificationSettingsForm`
- **Implement system settings form**
  - API: `GET /api/v1/settings`, `POST /api/v1/settings`
  - Frontend: `useGetSystemSettingsQuery`, `useUpdateSystemSettingsMutation`
  - Component: `SystemSettingsForm`
- **Add config backup/restore dialog**
  - API: `POST /api/v1/database/backup`, `POST /api/v1/database/restore`
  - Frontend: `useBackupDatabaseMutation`, `useRestoreDatabaseMutation`
  - Component: `ConfigBackupRestoreDialog`

### System Health
- **Show system health summary**
  - API: `GET /api/v1/health`
  - Frontend: `useGetHealthQuery`
  - Component: `SystemHealthSummary`
- **Add resource monitor**
  - API: `GET /api/v1/health`
  - Frontend: `useGetHealthQuery`
  - Component: `ResourceMonitor`
- **Implement live log viewer**
  - API: `GET /api/v1/logs` (if available)
  - Frontend: `useGetLogsQuery`
  - Component: `LiveLogViewer`
- **Add maintenance tools panel**
  - API: `POST /api/v1/database/backup`, `POST /api/v1/database/restore`, `POST /api/v1/database/migrate`
  - Frontend: `useBackupDatabaseMutation`, `useRestoreDatabaseMutation`, `useMigrateDatabaseMutation`
  - Component: `MaintenanceToolsPanel`

---

## 14. Backend Integration & API Contract Management

### 14.1 OpenAPI/Swagger Integration
- If your backend exposes an OpenAPI/Swagger spec (e.g., `/openapi.json` or `/swagger.json`), use it to:
  - Generate RTK Query endpoints and TypeScript types automatically (e.g., with [openapi-typescript-codegen](https://github.com/ferdikoomen/openapi-typescript-codegen) or [rtk-query-codegen-openapi](https://github.com/openapi-ts/rtk-query-codegen-openapi)).
  - Keep frontend and backend in sync as APIs evolve.
- **Recommended workflow:**
  1. Download or reference the OpenAPI spec from the backend.
  2. Run codegen to produce API hooks/types in `src/api/`.
  3. Use generated hooks in your components and Redux slices.
  4. Regenerate on backend changes.

### 14.2 Running Frontend Against Backend
- Set `REACT_APP_API_BASE_URL` in `.env` to your backend’s base URL (e.g., `http://localhost:8000`).
- If CORS issues arise, use a proxy in `package.json` or a tool like [http-proxy-middleware](https://github.com/chimurai/http-proxy-middleware).
- Document any required authentication or headers (if added in the future).

### 14.3 Sample API Responses
- For each endpoint, collect and document sample JSON responses (success and error cases) in this spec or in a `docs/api_samples/` folder.
- Example:
  ```json
  // GET /api/v1/alarms/history
  [
    {"alarm_id": 1, "zone_id": 1, "timestamp": "2025-06-10T12:34:56Z", "acknowledged": false, "max_temp": 30.2}
  ]
  // Error
  { "detail": "Database unavailable" }
  ```
- Use these samples for frontend mocking, Storybook, and test fixtures.

### 14.4 Frontend-Backend Sync Workflow
- On backend API changes:
  1. Update the OpenAPI/Swagger spec.
  2. Regenerate frontend API hooks/types.
  3. Update sample responses and contract tests.
  4. Run frontend tests and Storybook against the live backend or mocks.
- Consider using contract testing tools (e.g., [pact](https://docs.pact.io/)) for automated validation.

### 14.5 Automated API Documentation
- Link to the live API docs (Swagger UI, Redoc, etc.) in this spec for developer reference.
- Example: [http://localhost:8000/docs](http://localhost:8000/docs) or [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 14.6 Local Backend Startup & Frontend Connection
- To run the backend locally for development/testing:
  1. Open a terminal in the `backend` folder.
  2. Start the backend server (see backend README for details, e.g., `python -m backend.src.main` or `uvicorn backend.src.main:app --reload`).
  3. By default, the backend will run at `http://127.0.0.1:8000`.
- In your frontend `.env`, set:
  ```env
  REACT_APP_API_BASE_URL=http://127.0.0.1:8000
  ```
- If you encounter CORS issues, ensure the backend has CORS enabled for your frontend origin, or use a proxy as described above.
- You can now develop and test the frontend with live API data from your local backend.

---

## 15. OpenAPI Specification Integration

The full OpenAPI 3.1 spec for the backend API is now included in `frontend/api.json`.

- **Location:** `frontend/api.json`
- **How to use:**
  - Use this file for API client code generation (e.g., with OpenAPI Generator, Swagger Codegen, or tools like openapi-typescript, or RTK Query codegen plugins).
  - Keep this file in sync with the backend (`GET http://127.0.0.1:8000/openapi.json`).
  - Use it for contract testing, API documentation, and as the single source of truth for frontend-backend integration.
- **Sample usage:**
  - Generate TypeScript types and API hooks:
    ```sh
    npx openapi-typescript frontend/api.json --output src/types/api.d.ts
    # or
    npx @rtk-query/codegen-openapi --file frontend/api.json --output src/api/generatedApi.ts
    ```
  - Reference the OpenAPI file in your README and developer docs.
- **Live API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

> **Note:** Always update `frontend/api.json` after backend API changes to keep the frontend in sync.

---

*Check off each atomic step as you complete it. Add more atomic steps as needed for your workflow.*
