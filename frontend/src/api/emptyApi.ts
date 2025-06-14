import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const emptySplitApi = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000' }),
  endpoints: () => ({}),
});
