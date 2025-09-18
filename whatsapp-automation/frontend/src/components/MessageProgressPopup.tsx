import React, { useEffect, useState } from 'react';
import { X, MessageSquare, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';

interface ProgressUpdate {
  type: 'session_check' | 'qr_required' | 'qr_scanned' | 'sending' | 'success' | 'error' | 'complete';
  message: string;
  currentPhone?: string;
  progress?: {
    current: number;
    total: number;
    successful: number;
    failed: number;
  };
  timestamp: string;
}

interface MessageProgressPopupProps {
  isOpen: boolean;
  onClose: () => void;
  updates: ProgressUpdate[];
  finalResults?: {
    successful: number;
    failed: number;
    total: number;
    successRate: number;
  };
}

const MessageProgressPopup: React.FC<MessageProgressPopupProps> = ({
  isOpen,
  onClose,
  updates,
  finalResults
}) => {
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (finalResults) {
      setIsComplete(true);
    }
  }, [finalResults]);

  if (!isOpen) return null;

  const latestUpdate = updates[updates.length - 1];
  const progress = latestUpdate?.progress;

  const getProgressPercentage = () => {
    if (!progress || progress.total === 0) return 0;
    return Math.round((progress.current / progress.total) * 100);
  };

  const getStatusIcon = (type: string) => {
    switch (type) {
      case 'session_check':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'qr_required':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'qr_scanned':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'sending':
        return <MessageSquare className="w-4 h-4 text-blue-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'complete':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-6 h-6 text-green-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              {isComplete ? 'Messages Sent!' : 'Sending WhatsApp Messages'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Section */}
        {!isComplete && progress && (
          <div className="p-6 border-b border-gray-200">
            <div className="space-y-4">
              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{getProgressPercentage()}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${getProgressPercentage()}%` }}
                  />
                </div>
              </div>

              {/* Current Status */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Sent</div>
                  <div className="text-2xl font-bold text-green-600">
                    {progress.successful}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Failed</div>
                  <div className="text-2xl font-bold text-red-600">
                    {progress.failed}
                  </div>
                </div>
              </div>

              {/* Current Phone */}
              {latestUpdate?.currentPhone && (
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-sm text-blue-600 font-medium">Currently sending to:</div>
                  <div className="text-blue-900 font-mono">{latestUpdate.currentPhone}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Final Results */}
        {isComplete && finalResults && (
          <div className="p-6 border-b border-gray-200">
            <div className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Campaign Complete!</h3>
                <p className="text-gray-600">Your WhatsApp messages have been sent.</p>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{finalResults.successful}</div>
                  <div className="text-sm text-gray-600">Successful</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{finalResults.failed}</div>
                  <div className="text-sm text-gray-600">Failed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{finalResults.successRate}%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Activity Log */}
        <div className="p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Activity Log</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {updates.map((update, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {getStatusIcon(update.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{update.message}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(update.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {!isComplete && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-500">
                Please keep this window open while messages are being sent...
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        {isComplete && (
          <div className="p-6 border-t border-gray-200">
            <button
              onClick={onClose}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageProgressPopup;
