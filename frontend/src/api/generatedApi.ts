import { emptySplitApi as api } from "frontend/src/api/emptyApi";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    getRealTimeFrameApiV1ThermalRealTimeGet: build.query<
      GetRealTimeFrameApiV1ThermalRealTimeGetApiResponse,
      GetRealTimeFrameApiV1ThermalRealTimeGetApiArg
    >({
      query: () => ({ url: `/api/v1/thermal/real-time` }),
    }),
    getZonesApiV1ZonesGet: build.query<
      GetZonesApiV1ZonesGetApiResponse,
      GetZonesApiV1ZonesGetApiArg
    >({
      query: () => ({ url: `/api/v1/zones` }),
    }),
    addZoneApiV1ZonesPost: build.mutation<
      AddZoneApiV1ZonesPostApiResponse,
      AddZoneApiV1ZonesPostApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/zones`,
        method: "POST",
        body: queryArg.zoneRequest,
      }),
    }),
    deleteZoneApiV1ZonesZoneIdDelete: build.mutation<
      DeleteZoneApiV1ZonesZoneIdDeleteApiResponse,
      DeleteZoneApiV1ZonesZoneIdDeleteApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/zones/${queryArg.zoneId}`,
        method: "DELETE",
      }),
    }),
    getZoneAverageApiV1ZonesZoneIdAverageGet: build.query<
      GetZoneAverageApiV1ZonesZoneIdAverageGetApiResponse,
      GetZoneAverageApiV1ZonesZoneIdAverageGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/zones/${queryArg.zoneId}/average`,
      }),
    }),
    healthApiV1HealthGet: build.query<
      HealthApiV1HealthGetApiResponse,
      HealthApiV1HealthGetApiArg
    >({
      query: () => ({ url: `/api/v1/health` }),
    }),
    getNotificationsApiV1NotificationsSettingsGet: build.query<
      GetNotificationsApiV1NotificationsSettingsGetApiResponse,
      GetNotificationsApiV1NotificationsSettingsGetApiArg
    >({
      query: () => ({ url: `/api/v1/notifications/settings` }),
    }),
    addNotificationApiV1NotificationsSettingsPost: build.mutation<
      AddNotificationApiV1NotificationsSettingsPostApiResponse,
      AddNotificationApiV1NotificationsSettingsPostApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/notifications/settings`,
        method: "POST",
        body: queryArg.notificationRequest,
      }),
    }),
    updateNotificationApiV1NotificationsSettingsNotificationIdPut:
      build.mutation<
        UpdateNotificationApiV1NotificationsSettingsNotificationIdPutApiResponse,
        UpdateNotificationApiV1NotificationsSettingsNotificationIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/settings/${queryArg.notificationId}`,
          method: "PUT",
          body: queryArg.notificationRequest,
        }),
      }),
    deleteNotificationApiV1NotificationsSettingsNotificationIdDelete:
      build.mutation<
        DeleteNotificationApiV1NotificationsSettingsNotificationIdDeleteApiResponse,
        DeleteNotificationApiV1NotificationsSettingsNotificationIdDeleteApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/settings/${queryArg.notificationId}`,
          method: "DELETE",
        }),
      }),
    getEventFramesApiV1EventsEventIdFramesGet: build.query<
      GetEventFramesApiV1EventsEventIdFramesGetApiResponse,
      GetEventFramesApiV1EventsEventIdFramesGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/events/${queryArg.eventId}/frames`,
      }),
    }),
    downloadEventFramesPngApiV1EventsEventIdFramesPngGet: build.query<
      DownloadEventFramesPngApiV1EventsEventIdFramesPngGetApiResponse,
      DownloadEventFramesPngApiV1EventsEventIdFramesPngGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/events/${queryArg.eventId}/frames.png`,
      }),
    }),
    getEventFrameBlobsApiV1EventsEventIdFramesBlobsGet: build.query<
      GetEventFrameBlobsApiV1EventsEventIdFramesBlobsGetApiResponse,
      GetEventFrameBlobsApiV1EventsEventIdFramesBlobsGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/events/${queryArg.eventId}/frames/blobs`,
      }),
    }),
    exportFramesApiV1FramesExportGet: build.query<
      ExportFramesApiV1FramesExportGetApiResponse,
      ExportFramesApiV1FramesExportGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/frames/export`,
        params: {
          event_id: queryArg.eventId,
          overlay: queryArg.overlay,
        },
      }),
    }),
    getSettingsApiV1SettingsGet: build.query<
      GetSettingsApiV1SettingsGetApiResponse,
      GetSettingsApiV1SettingsGetApiArg
    >({
      query: () => ({ url: `/api/v1/settings` }),
    }),
    setSettingApiV1SettingsPost: build.mutation<
      SetSettingApiV1SettingsPostApiResponse,
      SetSettingApiV1SettingsPostApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/settings`,
        method: "POST",
        body: queryArg.settingsRequest,
      }),
    }),
    backupDatabaseApiV1DatabaseBackupPost: build.mutation<
      BackupDatabaseApiV1DatabaseBackupPostApiResponse,
      BackupDatabaseApiV1DatabaseBackupPostApiArg
    >({
      query: () => ({ url: `/api/v1/database/backup`, method: "POST" }),
    }),
    restoreDatabaseApiV1DatabaseRestorePost: build.mutation<
      RestoreDatabaseApiV1DatabaseRestorePostApiResponse,
      RestoreDatabaseApiV1DatabaseRestorePostApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/database/restore`,
        method: "POST",
        body: queryArg.bodyRestoreDatabaseApiV1DatabaseRestorePost,
      }),
    }),
    migrateDatabaseApiV1DatabaseMigratePost: build.mutation<
      MigrateDatabaseApiV1DatabaseMigratePostApiResponse,
      MigrateDatabaseApiV1DatabaseMigratePostApiArg
    >({
      query: () => ({ url: `/api/v1/database/migrate`, method: "POST" }),
    }),
    getHeatmapApiV1AnalyticsHeatmapGet: build.query<
      GetHeatmapApiV1AnalyticsHeatmapGetApiResponse,
      GetHeatmapApiV1AnalyticsHeatmapGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/analytics/heatmap`,
        params: {
          start_time: queryArg.startTime,
          end_time: queryArg.endTime,
          zone_id: queryArg.zoneId,
        },
      }),
    }),
    getTrendsApiV1AnalyticsTrendsGet: build.query<
      GetTrendsApiV1AnalyticsTrendsGetApiResponse,
      GetTrendsApiV1AnalyticsTrendsGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/analytics/trends`,
        params: {
          start_time: queryArg.startTime,
          end_time: queryArg.endTime,
          zone_id: queryArg.zoneId,
        },
      }),
    }),
    getAnomaliesApiV1AnalyticsAnomaliesGet: build.query<
      GetAnomaliesApiV1AnalyticsAnomaliesGetApiResponse,
      GetAnomaliesApiV1AnalyticsAnomaliesGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/analytics/anomalies`,
        params: {
          start_time: queryArg.startTime,
          end_time: queryArg.endTime,
          zone_id: queryArg.zoneId,
        },
      }),
    }),
    getReportApiV1ReportsGet: build.query<
      GetReportApiV1ReportsGetApiResponse,
      GetReportApiV1ReportsGetApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/reports`,
        params: {
          report_type: queryArg.reportType,
          start_time: queryArg.startTime,
          end_time: queryArg.endTime,
          zone_id: queryArg.zoneId,
        },
      }),
    }),
    getAlarmHistoryApiV1AlarmsHistoryGet: build.query<
      GetAlarmHistoryApiV1AlarmsHistoryGetApiResponse,
      GetAlarmHistoryApiV1AlarmsHistoryGetApiArg
    >({
      query: () => ({ url: `/api/v1/alarms/history` }),
    }),
    acknowledgeAlarmApiV1AlarmsAcknowledgePost: build.mutation<
      AcknowledgeAlarmApiV1AlarmsAcknowledgePostApiResponse,
      AcknowledgeAlarmApiV1AlarmsAcknowledgePostApiArg
    >({
      query: (queryArg) => ({
        url: `/api/v1/alarms/acknowledge`,
        method: "POST",
        body: queryArg.alarmAcknowledgeRequest,
      }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetRealTimeFrameApiV1ThermalRealTimeGetApiResponse =
  /** status 200 Successful Response */ ThermalFrameResponse;
export type GetRealTimeFrameApiV1ThermalRealTimeGetApiArg = void;
export type GetZonesApiV1ZonesGetApiResponse =
  /** status 200 Successful Response */ ZoneResponse[];
export type GetZonesApiV1ZonesGetApiArg = void;
export type AddZoneApiV1ZonesPostApiResponse =
  /** status 200 Successful Response */ ZoneResponse;
export type AddZoneApiV1ZonesPostApiArg = {
  zoneRequest: ZoneRequest;
};
export type DeleteZoneApiV1ZonesZoneIdDeleteApiResponse =
  /** status 200 Successful Response */ {
    [key: string]: string;
  };
export type DeleteZoneApiV1ZonesZoneIdDeleteApiArg = {
  zoneId: number;
};
export type GetZoneAverageApiV1ZonesZoneIdAverageGetApiResponse =
  /** status 200 Successful Response */ ZoneAverageResponse;
export type GetZoneAverageApiV1ZonesZoneIdAverageGetApiArg = {
  zoneId: number;
};
export type HealthApiV1HealthGetApiResponse =
  /** status 200 Successful Response */ {
    [key: string]: string;
  };
export type HealthApiV1HealthGetApiArg = void;
export type GetNotificationsApiV1NotificationsSettingsGetApiResponse =
  /** status 200 Successful Response */ NotificationResponse[];
export type GetNotificationsApiV1NotificationsSettingsGetApiArg = void;
export type AddNotificationApiV1NotificationsSettingsPostApiResponse =
  /** status 200 Successful Response */ NotificationResponse;
export type AddNotificationApiV1NotificationsSettingsPostApiArg = {
  notificationRequest: NotificationRequest;
};
export type UpdateNotificationApiV1NotificationsSettingsNotificationIdPutApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateNotificationApiV1NotificationsSettingsNotificationIdPutApiArg =
  {
    notificationId: number;
    notificationRequest: NotificationRequest;
  };
export type DeleteNotificationApiV1NotificationsSettingsNotificationIdDeleteApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteNotificationApiV1NotificationsSettingsNotificationIdDeleteApiArg =
  {
    notificationId: number;
  };
export type GetEventFramesApiV1EventsEventIdFramesGetApiResponse =
  /** status 200 Successful Response */ EventFrameResponse[];
export type GetEventFramesApiV1EventsEventIdFramesGetApiArg = {
  eventId: number;
};
export type DownloadEventFramesPngApiV1EventsEventIdFramesPngGetApiResponse =
  /** status 200 Successful Response */ any;
export type DownloadEventFramesPngApiV1EventsEventIdFramesPngGetApiArg = {
  eventId: number;
};
export type GetEventFrameBlobsApiV1EventsEventIdFramesBlobsGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetEventFrameBlobsApiV1EventsEventIdFramesBlobsGetApiArg = {
  eventId: number;
};
export type ExportFramesApiV1FramesExportGetApiResponse =
  /** status 200 Successful Response */ any;
export type ExportFramesApiV1FramesExportGetApiArg = {
  eventId?: number | null;
  overlay?: string | null;
};
export type GetSettingsApiV1SettingsGetApiResponse =
  /** status 200 Successful Response */ SettingsResponse[];
export type GetSettingsApiV1SettingsGetApiArg = void;
export type SetSettingApiV1SettingsPostApiResponse =
  /** status 200 Successful Response */ SettingsResponse;
export type SetSettingApiV1SettingsPostApiArg = {
  settingsRequest: SettingsRequest;
};
export type BackupDatabaseApiV1DatabaseBackupPostApiResponse =
  /** status 200 Successful Response */ any;
export type BackupDatabaseApiV1DatabaseBackupPostApiArg = void;
export type RestoreDatabaseApiV1DatabaseRestorePostApiResponse =
  /** status 200 Successful Response */ any;
export type RestoreDatabaseApiV1DatabaseRestorePostApiArg = {
  bodyRestoreDatabaseApiV1DatabaseRestorePost: BodyRestoreDatabaseApiV1DatabaseRestorePost;
};
export type MigrateDatabaseApiV1DatabaseMigratePostApiResponse =
  /** status 200 Successful Response */ any;
export type MigrateDatabaseApiV1DatabaseMigratePostApiArg = void;
export type GetHeatmapApiV1AnalyticsHeatmapGetApiResponse =
  /** status 200 Successful Response */ HeatmapResponse;
export type GetHeatmapApiV1AnalyticsHeatmapGetApiArg = {
  startTime: string;
  endTime: string;
  zoneId?: number | null;
};
export type GetTrendsApiV1AnalyticsTrendsGetApiResponse =
  /** status 200 Successful Response */ TrendResponse;
export type GetTrendsApiV1AnalyticsTrendsGetApiArg = {
  startTime: string;
  endTime: string;
  zoneId?: number | null;
};
export type GetAnomaliesApiV1AnalyticsAnomaliesGetApiResponse =
  /** status 200 Successful Response */ AnomalyResponse;
export type GetAnomaliesApiV1AnalyticsAnomaliesGetApiArg = {
  startTime: string;
  endTime: string;
  zoneId?: number | null;
};
export type GetReportApiV1ReportsGetApiResponse =
  /** status 200 Successful Response */ ReportResponse;
export type GetReportApiV1ReportsGetApiArg = {
  reportType: string;
  startTime: string;
  endTime: string;
  zoneId?: number | null;
};
export type GetAlarmHistoryApiV1AlarmsHistoryGetApiResponse =
  /** status 200 Successful Response */ AlarmEventResponse[];
export type GetAlarmHistoryApiV1AlarmsHistoryGetApiArg = void;
export type AcknowledgeAlarmApiV1AlarmsAcknowledgePostApiResponse =
  /** status 200 Successful Response */ any;
export type AcknowledgeAlarmApiV1AlarmsAcknowledgePostApiArg = {
  alarmAcknowledgeRequest: AlarmAcknowledgeRequest;
};
export type ThermalFrameResponse = {
  timestamp: string;
  frame: number[];
};
export type ZoneResponse = {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  color: string;
  enabled: boolean;
  threshold: number | null;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type ZoneRequest = {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  name?: string | null;
  color?: string | null;
  enabled?: boolean | null;
  threshold?: number | null;
};
export type ZoneAverageResponse = {
  zone_id: number;
  average: number;
};
export type NotificationResponse = {
  id: number;
  name: string;
  type: string;
  config: string;
  enabled: boolean;
  created_at: string;
};
export type NotificationRequest = {
  name: string;
  type: string;
  config: string;
  enabled?: boolean | null;
};
export type EventFrameResponse = {
  id: number;
  event_id: number;
  timestamp: string;
  frame_size: number;
};
export type SettingsResponse = {
  key: string;
  value: string;
  description?: string | null;
};
export type SettingsRequest = {
  key: string;
  value: string;
  description?: string | null;
};
export type BodyRestoreDatabaseApiV1DatabaseRestorePost = {
  file: Blob;
};
export type HeatmapResponse = {
  heatmap: number[][];
  width: number;
  height: number;
  start_time: string;
  end_time: string;
  zone_id?: number | null;
};
export type TrendResponse = {
  timestamps: string[];
  values: number[];
  zone_id?: number | null;
};
export type AnomalyResponse = {
  anomalies: {
    [key: string]: any;
  }[];
  zone_id?: number | null;
};
export type ReportResponse = {
  report_type: string;
  start_time: string;
  end_time: string;
  zone_id?: number | null;
  summary: {
    [key: string]: any;
  };
};
export type AlarmEventResponse = {
  alarm_id: number;
  zone_id: number;
  temperature: number;
  timestamp: string;
  event_type: string;
  acknowledged: boolean;
  acknowledged_at?: string | null;
};
export type AlarmAcknowledgeRequest = {
  alarm_id: number;
};
export const {
  useGetRealTimeFrameApiV1ThermalRealTimeGetQuery,
  useGetZonesApiV1ZonesGetQuery,
  useAddZoneApiV1ZonesPostMutation,
  useDeleteZoneApiV1ZonesZoneIdDeleteMutation,
  useGetZoneAverageApiV1ZonesZoneIdAverageGetQuery,
  useHealthApiV1HealthGetQuery,
  useGetNotificationsApiV1NotificationsSettingsGetQuery,
  useAddNotificationApiV1NotificationsSettingsPostMutation,
  useUpdateNotificationApiV1NotificationsSettingsNotificationIdPutMutation,
  useDeleteNotificationApiV1NotificationsSettingsNotificationIdDeleteMutation,
  useGetEventFramesApiV1EventsEventIdFramesGetQuery,
  useDownloadEventFramesPngApiV1EventsEventIdFramesPngGetQuery,
  useGetEventFrameBlobsApiV1EventsEventIdFramesBlobsGetQuery,
  useExportFramesApiV1FramesExportGetQuery,
  useGetSettingsApiV1SettingsGetQuery,
  useSetSettingApiV1SettingsPostMutation,
  useBackupDatabaseApiV1DatabaseBackupPostMutation,
  useRestoreDatabaseApiV1DatabaseRestorePostMutation,
  useMigrateDatabaseApiV1DatabaseMigratePostMutation,
  useGetHeatmapApiV1AnalyticsHeatmapGetQuery,
  useGetTrendsApiV1AnalyticsTrendsGetQuery,
  useGetAnomaliesApiV1AnalyticsAnomaliesGetQuery,
  useGetReportApiV1ReportsGetQuery,
  useGetAlarmHistoryApiV1AlarmsHistoryGetQuery,
  useAcknowledgeAlarmApiV1AlarmsAcknowledgePostMutation,
} = injectedRtkApi;
