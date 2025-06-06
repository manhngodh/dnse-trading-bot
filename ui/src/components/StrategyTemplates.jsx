import React from 'react';
import { Code, Copy, Download } from 'lucide-react';

const StrategyTemplates = ({ onSelectTemplate }) => {
  const templates = [
    {
      id: 'sma_crossover',
      name: 'SMA Crossover',
      description: 'Simple Moving Average crossover strategy',
      code: `class SMAStrategy extends BaseStrategy {
    constructor(params = {}) {
        super();
        this.shortPeriod = params.shortPeriod || 10;
        this.longPeriod = params.longPeriod || 20;
        this.position = 0;
    }

    onInit() {
        this.shortSMA = this.indicator('SMA', this.shortPeriod);
        this.longSMA = this.indicator('SMA', this.longPeriod);
    }

    onBar(bar) {
        const shortValue = this.shortSMA.getValue();
        const longValue = this.longSMA.getValue();
        
        if (shortValue > longValue && this.position <= 0) {
            this.buy(bar.close, 100);
            this.position = 1;
        } else if (shortValue < longValue && this.position >= 0) {
            this.sell(bar.close, 100);
            this.position = -1;
        }
    }
}`,
      params: {
        shortPeriod: { type: 'number', default: 10, min: 5, max: 50 },
        longPeriod: { type: 'number', default: 20, min: 10, max: 100 }
      }
    },
    {
      id: 'rsi_oversold',
      name: 'RSI Oversold/Overbought',
      description: 'RSI based mean reversion strategy',
      code: `class RSIStrategy extends BaseStrategy {
    constructor(params = {}) {
        super();
        this.period = params.period || 14;
        this.oversold = params.oversold || 30;
        this.overbought = params.overbought || 70;
        this.position = 0;
    }

    onInit() {
        this.rsi = this.indicator('RSI', this.period);
    }

    onBar(bar) {
        const rsiValue = this.rsi.getValue();
        
        if (rsiValue < this.oversold && this.position <= 0) {
            this.buy(bar.close, 100);
            this.position = 1;
        } else if (rsiValue > this.overbought && this.position >= 0) {
            this.sell(bar.close, 100);
            this.position = -1;
        }
    }
}`,
      params: {
        period: { type: 'number', default: 14, min: 5, max: 30 },
        oversold: { type: 'number', default: 30, min: 10, max: 40 },
        overbought: { type: 'number', default: 70, min: 60, max: 90 }
      }
    },
    {
      id: 'macd_divergence',
      name: 'MACD Divergence',
      description: 'MACD signal line crossover strategy',
      code: `class MACDStrategy extends BaseStrategy {
    constructor(params = {}) {
        super();
        this.fastPeriod = params.fastPeriod || 12;
        this.slowPeriod = params.slowPeriod || 26;
        this.signalPeriod = params.signalPeriod || 9;
        this.position = 0;
    }

    onInit() {
        this.macd = this.indicator('MACD', this.fastPeriod, this.slowPeriod, this.signalPeriod);
    }

    onBar(bar) {
        const macdValue = this.macd.getValue();
        const signalValue = this.macd.getSignal();
        
        if (macdValue > signalValue && this.position <= 0) {
            this.buy(bar.close, 100);
            this.position = 1;
        } else if (macdValue < signalValue && this.position >= 0) {
            this.sell(bar.close, 100);
            this.position = -1;
        }
    }
}`,
      params: {
        fastPeriod: { type: 'number', default: 12, min: 5, max: 20 },
        slowPeriod: { type: 'number', default: 26, min: 15, max: 40 },
        signalPeriod: { type: 'number', default: 9, min: 5, max: 15 }
      }
    },
    {
      id: 'bollinger_bands',
      name: 'Bollinger Bands',
      description: 'Bollinger Bands mean reversion strategy',
      code: `class BollingerBandsStrategy extends BaseStrategy {
    constructor(params = {}) {
        super();
        this.period = params.period || 20;
        this.stdDev = params.stdDev || 2;
        this.position = 0;
    }

    onInit() {
        this.bb = this.indicator('BollingerBands', this.period, this.stdDev);
    }

    onBar(bar) {
        const upperBand = this.bb.getUpper();
        const lowerBand = this.bb.getLower();
        const close = bar.close;
        
        if (close < lowerBand && this.position <= 0) {
            this.buy(bar.close, 100);
            this.position = 1;
        } else if (close > upperBand && this.position >= 0) {
            this.sell(bar.close, 100);
            this.position = -1;
        }
    }
}`,
      params: {
        period: { type: 'number', default: 20, min: 10, max: 50 },
        stdDev: { type: 'number', default: 2, min: 1, max: 3, step: 0.1 }
      }
    }
  ];

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
  };

  const handleSelectTemplate = (template) => {
    onSelectTemplate(template);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Code className="w-5 h-5 mr-2" />
        Strategy Templates
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {templates.map((template) => (
          <div key={template.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-medium">{template.name}</h4>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleCopyCode(template.code)}
                  className="text-gray-500 hover:text-gray-700"
                  title="Copy code"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleSelectTemplate(template)}
                  className="text-blue-500 hover:text-blue-700"
                  title="Use template"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <p className="text-sm text-gray-600 mb-3">{template.description}</p>
            
            <div className="text-xs text-gray-500">
              <strong>Parameters:</strong>
              <ul className="mt-1 space-y-1">
                {Object.entries(template.params).map(([key, config]) => (
                  <li key={key} className="flex justify-between">
                    <span>{key}:</span>
                    <span>{config.default} ({config.type})</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <button
              onClick={() => handleSelectTemplate(template)}
              className="w-full mt-3 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600 transition-colors"
            >
              Use This Template
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StrategyTemplates;
