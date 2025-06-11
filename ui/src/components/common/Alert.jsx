import React from 'react';
import { AlertCircle, CheckCircle, X } from 'lucide-react';

const Alert = ({ type, message, onClose }) => {
  if (!message) return null;

  const alertStyles = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-700',
      icon: <CheckCircle className="h-5 w-5 text-green-500" />,
      closeColor: 'text-green-500'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-700',
      icon: <AlertCircle className="h-5 w-5 text-red-500" />,
      closeColor: 'text-red-500'
    }
  };

  const style = alertStyles[type];

  return (
    <div className={`${style.bg} border ${style.border} rounded-lg p-4 flex items-center space-x-2`}>
      {style.icon}
      <span className={style.text}>{message}</span>
      <button onClick={onClose} className={`ml-auto ${style.closeColor}`}>
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

export default Alert;
