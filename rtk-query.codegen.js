module.exports = {
  schemaFile: 'frontend/api.json',
  apiFile: 'frontend/src/api/emptyApi.ts',
  apiImport: 'emptySplitApi',
  outputFile: 'frontend/src/api/generatedApi.ts',
  exportName: 'api',
  hooks: true,
};
