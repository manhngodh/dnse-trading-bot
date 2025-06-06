import React, { useState, useEffect } from 'react';
import { Settings, RotateCcw, Save } from 'lucide-react';

const ParameterPanel = ({ strategy, onParametersChange, onSave, onReset }) => {
  const [parameters, setParameters] = useState({});
  const [presets, setPresets] = useState([]);

  useEffect(() => {
    if (strategy && strategy.params) {
      const defaultParams = {};
      Object.entries(strategy.params).forEach(([key, config]) => {
        defaultParams[key] = config.default;
      });
      setParameters(defaultParams);
    }
  }, [strategy]);

  const handleParameterChange = (paramName, value) => {
    const newParams = { ...parameters, [paramName]: value };
    setParameters(newParams);
    onParametersChange(newParams);
  };

  const handleSavePreset = () => {
    const presetName = prompt('Enter preset name:');
    if (presetName) {
      const newPreset = {
        id: Date.now().toString(),
        name: presetName,
        parameters: { ...parameters }
      };
      const updatedPresets = [...presets, newPreset];
      setPresets(updatedPresets);
      localStorage.setItem(`presets_${strategy.id}`, JSON.stringify(updatedPresets));
    }
  };

  const handleLoadPreset = (preset) => {
    setParameters(preset.parameters);
    onParametersChange(preset.parameters);
  };

  const handleReset = () => {
    if (strategy && strategy.params) {
      const defaultParams = {};
      Object.entries(strategy.params).forEach(([key, config]) => {
        defaultParams[key] = config.default;
      });
      setParameters(defaultParams);
      onParametersChange(defaultParams);
      onReset();
    }
  };

  const renderParameterInput = (paramName, config) => {
    const value = parameters[paramName] || config.default;

    switch (config.type) {
      case 'number':
        return (
          <div key={paramName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {paramName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
            </label>
            <input
              type="number"
              value={value}
              min={config.min}
              max={config.max}
              step={config.step || 1}
              onChange={(e) => handleParameterChange(paramName, parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {(config.min !== undefined || config.max !== undefined) && (
              <p className="text-xs text-gray-500 mt-1">
                Range: {config.min || 0} - {config.max || '∞'}
              </p>
            )}
          </div>
        );

      case 'boolean':
        return (
          <div key={paramName} className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={value}
                onChange={(e) => handleParameterChange(paramName, e.target.checked)}
                className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-700">
                {paramName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </span>
            </label>
          </div>
        );

      case 'select':
        return (
          <div key={paramName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {paramName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
            </label>
            <select
              value={value}
              onChange={(e) => handleParameterChange(paramName, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {config.options.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        );

      case 'string':
        return (
          <div key={paramName} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {paramName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleParameterChange(paramName, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );

      default:
        return null;
    }
  };

  if (!strategy || !strategy.params) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Strategy Parameters
        </h3>
        <div className="text-center text-gray-500 py-8">
          Select a strategy template to configure parameters
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Strategy Parameters
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={handleReset}
            className="text-gray-500 hover:text-gray-700 p-2 rounded"
            title="Reset to defaults"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={handleSavePreset}
            className="text-blue-500 hover:text-blue-700 p-2 rounded"
            title="Save as preset"
          >
            <Save className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Parameter Presets */}
      {presets.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Saved Presets</h4>
          <div className="flex flex-wrap gap-2">
            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handleLoadPreset(preset)}
                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Parameter Inputs */}
      <div className="space-y-4">
        {Object.entries(strategy.params).map(([paramName, config]) =>
          renderParameterInput(paramName, config)
        )}
      </div>

      {/* Backtest Configuration */}
      <div className="border-t pt-4 mt-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Backtest Configuration</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Initial Capital
            </label>
            <input
              type="number"
              value={parameters.initialCapital || 100000000}
              onChange={(e) => handleParameterChange('initialCapital', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">VND</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Commission Rate
            </label>
            <input
              type="number"
              value={parameters.commission || 0.0015}
              step="0.0001"
              onChange={(e) => handleParameterChange('commission', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">As decimal (0.15% = 0.0015)</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={parameters.startDate || '2024-01-01'}
              onChange={(e) => handleParameterChange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={parameters.endDate || new Date().toISOString().split('T')[0]}
              onChange={(e) => handleParameterChange('endDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Symbol
            </label>
            <input
              type="text"
              value={parameters.symbol || 'VN30F2412'}
              onChange={(e) => handleParameterChange('symbol', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., VN30F2412, HPG, VIC"
            />
          </div>
        </div>
      </div>

      {/* Risk Management */}
      <div className="border-t pt-4 mt-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Risk Management</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Position Size
            </label>
            <input
              type="number"
              value={parameters.maxPositionSize || 1000}
              onChange={(e) => handleParameterChange('maxPositionSize', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Maximum shares per position</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stop Loss %
            </label>
            <input
              type="number"
              value={parameters.stopLoss || 5}
              step="0.1"
              onChange={(e) => handleParameterChange('stopLoss', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Percentage</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Take Profit %
            </label>
            <input
              type="number"
              value={parameters.takeProfit || 10}
              step="0.1"
              onChange={(e) => handleParameterChange('takeProfit', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Percentage</p>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={parameters.enableRiskManagement || false}
                onChange={(e) => handleParameterChange('enableRiskManagement', e.target.checked)}
                className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-700">
                Enable Risk Management
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="border-t pt-4 mt-6">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Current Parameters: {Object.keys(parameters).length} configured
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => onSave(parameters)}
              className="bg-blue-500 text-white px-4 py-2 rounded text-sm hover:bg-blue-600 transition-colors"
            >
              Apply Parameters
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParameterPanel;
