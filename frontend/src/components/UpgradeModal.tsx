// frontend/src/components/UpgradeModal.tsx - COMPACT VERSION
import React from 'react';
import { X, Check, Zap, Crown, Sparkles, Clock, Users, Shield, Zap as Lightning } from 'lucide-react';
import { MinutesPlan } from '../src/types/minutes';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentMinutes: number;
  onSelectPlan: (plan: MinutesPlan) => void;
}

const PLANS: MinutesPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    minutes: 10,
    price: 0,
    description: 'Perfect for trying out audio separation',
    features: [
      'Up to 10 minutes processing',
      'MP3 output (320kbps)',
      'Basic support',
      '24-hour file retention'
    ]
  },
  {
    id: 'creator',
    name: 'Creator',
    minutes: 120,
    price: 9.99,
    description: 'For regular creators and musicians',
    features: [
      '120 minutes monthly',
      'MP3, WAV, FLAC output',
      'Priority processing',
      '7-day file retention',
      'Batch processing'
    ],
    popular: true
  },
  {
    id: 'pro',
    name: 'Professional',
    minutes: 500,
    price: 29.99,
    description: 'For professional studios and producers',
    features: [
      '500 minutes monthly',
      'All output formats',
      '24/7 priority support',
      '30-day file retention',
      'Batch processing',
      'API access'
    ]
  }
];

const UpgradeModal: React.FC<UpgradeModalProps> = ({
  isOpen,
  onClose,
  currentMinutes,
  onSelectPlan
}) => {
  if (!isOpen) return null;

  const handleSelectPlan = (plan: MinutesPlan) => {
    if (plan.price === 0) {
      // Reset to starter plan
      onSelectPlan(plan);
    } else {
      // In a real app, this would trigger payment
      alert(`In a real app, this would redirect to payment for ${plan.name} plan`);
      onSelectPlan(plan);
    }
    onClose();
  };

  const getPlanIcon = (planId: string) => {
    switch(planId) {
      case 'starter': return <Zap className="w-4 h-4" />;
      case 'creator': return <Users className="w-4 h-4" />;
      case 'pro': return <Shield className="w-4 h-4" />;
      default: return <Zap className="w-4 h-4" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 md:p-4 bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-3xl bg-white dark:bg-gray-900 rounded-xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header - Compact */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="p-1.5 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg">
                <Crown className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                  Upgrade Your Plan
                </h2>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Get more processing minutes and advanced features
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Current minutes status - Compact */}
        <div className="p-3 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Current Balance</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {currentMinutes.toFixed(1)} minutes
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-1 text-blue-600 dark:text-blue-400">
              <Lightning className="w-4 h-4" />
              <span className="text-xs font-medium">Processing Power</span>
            </div>
          </div>
        </div>

        {/* Plans - Compact Layout */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PLANS.map((plan) => (
              <div
                key={plan.id}
                className={`relative rounded-lg border p-3 transition-all duration-200 hover:scale-[1.02] ${
                  plan.popular
                    ? 'border-yellow-500 dark:border-yellow-500 shadow-md'
                    : 'border-gray-300 dark:border-gray-700'
                } ${plan.price === 0 ? 'opacity-100' : 'hover:shadow-lg'}`}
              >
                {plan.popular && (
                  <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                    <div className="flex items-center space-x-1 bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                      <Sparkles className="w-2 h-2" />
                      <span>MOST POPULAR</span>
                    </div>
                  </div>
                )}

                {/* Plan Header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`p-1 rounded ${
                      plan.id === 'starter' ? 'bg-gray-100 dark:bg-gray-800' :
                      plan.id === 'creator' ? 'bg-blue-100 dark:bg-blue-900/30' :
                      'bg-purple-100 dark:bg-purple-900/30'
                    }`}>
                      {getPlanIcon(plan.id)}
                    </div>
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                      {plan.name}
                    </h3>
                  </div>
                  {plan.popular && (
                    <div className="text-[10px] px-1.5 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded">
                      RECOMMENDED
                    </div>
                  )}
                </div>

                {/* Plan Minutes & Price */}
                <div className="mb-2">
                  <div className="flex items-baseline">
                    <span className="text-xl font-bold text-gray-900 dark:text-white">
                      {plan.minutes}
                    </span>
                    <span className="text-xs text-gray-600 dark:text-gray-400 ml-1">minutes</span>
                  </div>
                  {plan.price > 0 ? (
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      ${plan.price.toFixed(2)}/month
                    </div>
                  ) : (
                    <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                      Free Forever
                    </div>
                  )}
                </div>

                {/* Plan Description */}
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                  {plan.description}
                </p>

                {/* Features List - Compact */}
                <ul className="space-y-1 mb-3">
                  {plan.features.slice(0, 3).map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="w-3 h-3 text-green-500 mt-0.5 mr-1.5 flex-shrink-0" />
                      <span className="text-xs text-gray-700 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                  {plan.features.length > 3 && (
                    <li className="text-xs text-gray-500 dark:text-gray-400 pl-4">
                      +{plan.features.length - 3} more features
                    </li>
                  )}
                </ul>

                {/* Upgrade Button */}
                <button
                  onClick={() => handleSelectPlan(plan)}
                  className={`w-full py-2 text-xs font-medium rounded transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white'
                      : plan.price === 0
                      ? 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200'
                      : 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white'
                  }`}
                >
                  {plan.price === 0 ? 'Continue Free' : `Upgrade to ${plan.name}`}
                </button>
              </div>
            ))}
          </div>

          {/* Footer note - Compact */}
          <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-800">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              All plans include high-quality AI separation at 320kbps MP3 professional quality.
            </p>
            <p className="text-[10px] text-gray-400 dark:text-gray-500 text-center mt-1">
              By upgrading, you agree to our Terms of Service and Privacy Policy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UpgradeModal;