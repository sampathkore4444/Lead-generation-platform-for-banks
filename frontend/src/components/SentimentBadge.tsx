// Sentiment Badge Component
import { ThumbsUp, ThumbsDown, Minus } from 'lucide-react';

interface SentimentBadgeProps {
  sentiment: 'positive' | 'neutral' | 'negative';
  score: number;
  showLabel?: boolean;
}

export function SentimentBadge({ sentiment, score, showLabel = true }: SentimentBadgeProps) {
  const config = {
    positive: {
      icon: ThumbsUp,
      bg: 'bg-green-100',
      text: 'text-green-800',
      label: 'Positive'
    },
    neutral: {
      icon: Minus,
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      label: 'Neutral'
    },
    negative: {
      icon: ThumbsDown,
      bg: 'bg-red-100',
      text: 'text-red-800',
      label: 'Negative'
    }
  };

  const { icon: Icon, bg, text, label } = config[sentiment];

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${bg} ${text}`}>
      <Icon className="w-3 h-3" />
      {showLabel && <span>{label} ({Math.abs(score * 100).toFixed(0)}%)</span>}
    </span>
  );
}

// Fraud Risk Badge
interface FraudBadgeProps {
  risk_level: 'low' | 'medium' | 'high';
  score: number;
}

export function FraudBadge({ risk_level, score }: FraudBadgeProps) {
  const config = {
    low: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      icon: '✓'
    },
    medium: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      icon: '!'
    },
    high: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      icon: '⚠'
    }
  };

  const { bg, text, icon } = config[risk_level];

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${bg} ${text}`}>
      <span>{icon}</span>
      <span>{risk_level.toUpperCase()} Risk ({score}%)</span>
    </span>
  );
}

export default SentimentBadge;