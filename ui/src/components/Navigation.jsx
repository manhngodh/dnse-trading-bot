import React from 'react'
import { TrendingUp, Code, Globe, DollarSign, ListOrdered } from 'lucide-react'

const Navigation = ({ currentTab, setCurrentTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'strategy-editor', label: 'Strategy Editor', icon: Code },
    { id: 'dnse-trading', label: 'DNSE Trading', icon: DollarSign },
    { id: 'orders', label: 'Orders', icon: ListOrdered },
    { id: 'krx-viewer', label: 'KRX MQTT Viewer', icon: Globe },
  ]

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <TrendingUp className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold text-gray-900">DNSE Trading Bot</span>
          </div>

          {/* Navigation Links */}
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`
                    flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${currentTab === item.id 
                      ? 'bg-primary text-white' 
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation
