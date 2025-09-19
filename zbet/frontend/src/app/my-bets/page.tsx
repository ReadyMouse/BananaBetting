'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Clock, TrendingUp, CheckCircle, XCircle, DollarSign, Calendar, Filter } from 'lucide-react';
import { cn, getRandomBananaEmoji, formatCurrency } from '@/lib/utils';
import Disclaimer from '@/components/Disclaimer';

// Mock data for user bets
const mockUserBets = [
  {
    id: '1',
    betId: 'bet-001',
    bet: {
      title: 'Will a banana be thrown onto the field?',
      description: 'Classic Savannah Bananas tradition',
      category: 'banana-antics',
      emoji: '🍌'
    },
    amount: 0.05,
    odds: 2.5,
    potentialPayout: 0.125,
    status: 'pending',
    placedAt: '2024-01-15T14:30:00Z',
    settledAt: null
  },
  {
    id: '2',
    betId: 'bet-002',
    bet: {
      title: 'First fan to wear banana costume',
      description: 'Which inning will we spot the first fan?',
      category: 'crowd-fun',
      emoji: '🎭'
    },
    amount: 0.02,
    odds: 1.8,
    potentialPayout: 0.036,
    status: 'won',
    placedAt: '2024-01-14T16:45:00Z',
    settledAt: '2024-01-14T19:30:00Z'
  },
  {
    id: '3',
    betId: 'bet-003',
    bet: {
      title: 'Number of dancing players during warmup',
      description: 'How many players will be caught dancing?',
      category: 'player-props',
      emoji: '💃'
    },
    amount: 0.1,
    odds: 3.2,
    potentialPayout: 0.32,
    status: 'lost',
    placedAt: '2024-01-13T12:15:00Z',
    settledAt: '2024-01-13T15:45:00Z'
  },
  {
    id: '4',
    betId: 'bet-004',
    bet: {
      title: 'Pitcher does the cha-cha',
      description: 'Will the starting pitcher perform the cha-cha?',
      category: 'player-props',
      emoji: '🕺'
    },
    amount: 0.03,
    odds: 4.1,
    potentialPayout: 0.123,
    status: 'pending',
    placedAt: '2024-01-15T10:20:00Z',
    settledAt: null
  },
  {
    id: '5',
    betId: 'bet-005',
    bet: {
      title: 'Home run celebration dance',
      description: 'What type of celebration dance will follow?',
      category: 'baseball',
      emoji: '⚾'
    },
    amount: 0.08,
    odds: 2.9,
    potentialPayout: 0.232,
    status: 'won',
    placedAt: '2024-01-12T13:30:00Z',
    settledAt: '2024-01-12T17:15:00Z'
  },
  {
    id: '6',
    betId: 'bet-006',
    bet: {
      title: 'Crowd noise level (decibels)',
      description: 'Will the crowd noise exceed 120 decibels?',
      category: 'crowd-fun',
      emoji: '📢'
    },
    amount: 0.015,
    odds: 1.6,
    potentialPayout: 0.024,
    status: 'cancelled',
    placedAt: '2024-01-11T11:00:00Z',
    settledAt: '2024-01-11T11:30:00Z'
  }
];

const statusColors = {
  pending: 'bg-banana-100 text-banana-800 border-banana-300',
  won: 'bg-grass-100 text-grass-800 border-grass-300',
  lost: 'bg-red-100 text-red-800 border-red-300',
  cancelled: 'bg-gray-100 text-gray-800 border-gray-300'
};

const statusIcons = {
  pending: Clock,
  won: CheckCircle,
  lost: XCircle,
  cancelled: XCircle
};

export default function MyBetsPage() {
  const [filter, setFilter] = useState('all'); // all, pending, won, lost, cancelled
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, amount
  const [mounted, setMounted] = useState(false);
  const [buttonEmoji, setButtonEmoji] = useState('🍌');

  const filteredBets = mockUserBets
    .filter(bet => filter === 'all' || bet.status === filter)
    .sort((a, b) => {
      switch (sortBy) {
        case 'oldest':
          return new Date(a.placedAt).getTime() - new Date(b.placedAt).getTime();
        case 'amount':
          return b.amount - a.amount;
        case 'newest':
        default:
          return new Date(b.placedAt).getTime() - new Date(a.placedAt).getTime();
      }
    });

  // Calculate stats
  const stats = {
    totalBets: mockUserBets.length,
    pendingBets: mockUserBets.filter(bet => bet.status === 'pending').length,
    wonBets: mockUserBets.filter(bet => bet.status === 'won').length,
    totalWinnings: mockUserBets
      .filter(bet => bet.status === 'won')
      .reduce((total, bet) => total + bet.potentialPayout, 0),
    totalWagered: mockUserBets.reduce((total, bet) => total + bet.amount, 0)
  };

  useEffect(() => {
    setMounted(true);
    setButtonEmoji(getRandomBananaEmoji());
  }, []);

  const formatDate = (dateString: string) => {
    // Use a more deterministic format to avoid hydration mismatches
    const date = new Date(dateString);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const month = months[date.getMonth()];
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${month} ${day}, ${hours}:${minutes}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-banana-50 via-banana-100 to-grass-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center space-x-4 mb-4">
            <motion.span 
              className="text-4xl"
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            >
              🏆
            </motion.span>
            <h1 className="font-baseball text-3xl md:text-5xl font-bold text-banana-800">
              My Banana Bets
            </h1>
            <motion.span 
              className="text-4xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              📊
            </motion.span>
          </div>
          <p className="text-lg text-baseball-600 italic">
            Track your wins, losses, and banana-tastic adventures! 🎪
          </p>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8"
        >
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-banana-200 text-center">
            <Trophy className="mx-auto text-banana-600 mb-2" size={24} />
            <p className="text-2xl font-bold text-banana-800">{stats.totalBets}</p>
            <p className="text-xs text-baseball-600">Total Bets</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-banana-200 text-center">
            <Clock className="mx-auto text-banana-600 mb-2" size={24} />
            <p className="text-2xl font-bold text-banana-800">{stats.pendingBets}</p>
            <p className="text-xs text-baseball-600">Pending</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-grass-200 text-center">
            <CheckCircle className="mx-auto text-grass-600 mb-2" size={24} />
            <p className="text-2xl font-bold text-grass-800">{stats.wonBets}</p>
            <p className="text-xs text-baseball-600">Won</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-grass-200 text-center">
            <DollarSign className="mx-auto text-grass-600 mb-2" size={24} />
            <p className="text-lg font-bold text-grass-800">{stats.totalWinnings.toFixed(4)}</p>
            <p className="text-xs text-baseball-600">ZEC Won</p>
          </div>
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-banana-200 text-center">
            <TrendingUp className="mx-auto text-banana-600 mb-2" size={24} />
            <p className="text-lg font-bold text-banana-800">{stats.totalWagered.toFixed(4)}</p>
            <p className="text-xs text-baseball-600">ZEC Wagered</p>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200 mb-8"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            {/* Status Filter */}
            <div className="flex flex-wrap gap-2">
              {['all', 'pending', 'won', 'lost', 'cancelled'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={cn(
                    'px-4 py-2 rounded-lg font-medium transition-all duration-200 capitalize',
                    filter === status
                      ? 'bg-banana-500 text-white shadow-md'
                      : 'bg-banana-100 text-banana-800 hover:bg-banana-200'
                  )}
                >
                  {status === 'all' ? 'All Bets' : status}
                </button>
              ))}
            </div>

            {/* Sort Options */}
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-baseball-700">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-banana-500"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="amount">Highest Amount</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Bets List */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="space-y-4"
        >
          <AnimatePresence>
            {filteredBets.map((userBet, index) => {
              const StatusIcon = statusIcons[userBet.status];
              return (
                <motion.div
                  key={userBet.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200 hover:shadow-xl transition-all duration-200"
                >
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    {/* Bet Info */}
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="text-3xl">{userBet.bet.emoji}</div>
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-baseball-800 mb-1">
                          {userBet.bet.title}
                        </h3>
                        <p className="text-sm text-baseball-600 mb-2">
                          {userBet.bet.description}
                        </p>
                        <div className="flex items-center space-x-4 text-sm text-baseball-500">
                          <div className="flex items-center space-x-1">
                            <Calendar size={14} />
                            <span>Placed: {formatDate(userBet.placedAt)}</span>
                          </div>
                          {userBet.settledAt && (
                            <div className="flex items-center space-x-1">
                              <Clock size={14} />
                              <span>Settled: {formatDate(userBet.settledAt)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Bet Details */}
                    <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
                      <div className="text-center">
                        <p className="text-sm text-baseball-600">Amount</p>
                        <p className="font-bold text-banana-800">{userBet.amount.toFixed(4)} ZEC</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-baseball-600">Odds</p>
                        <p className="font-bold text-grass-600">{userBet.odds}x</p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-baseball-600">
                          {userBet.status === 'won' ? 'Won' : 'Potential'}
                        </p>
                        <p className={cn(
                          'font-bold',
                          userBet.status === 'won' ? 'text-grass-600' : 'text-banana-800'
                        )}>
                          {userBet.potentialPayout.toFixed(4)} ZEC
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className={cn(
                          'flex items-center space-x-2 px-3 py-2 rounded-lg border text-sm font-medium',
                          statusColors[userBet.status]
                        )}>
                          <StatusIcon size={16} />
                          <span className="capitalize">{userBet.status}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>

        {/* Empty State */}
        {filteredBets.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-center py-12"
          >
            <div className="text-6xl mb-4">🎪</div>
            <h3 className="text-xl font-bold text-baseball-800 mb-2">
              No bets found!
            </h3>
            <p className="text-baseball-600 mb-6">
              {filter === 'all' 
                ? "You haven't placed any bets yet. Time to join the fun!"
                : `No ${filter} bets found. Try a different filter!`}
            </p>
            {filter === 'all' && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.location.href = '/betting'}
                className="bg-banana-500 hover:bg-banana-600 text-white font-bold py-3 px-6 rounded-lg transition-colors flex items-center space-x-2 mx-auto"
              >
                <span>Find Bets</span>
                <span>{buttonEmoji}</span>
              </motion.button>
            )}
          </motion.div>
        )}

        {/* Fun Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center mt-12 p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-banana-200"
        >
          <p className="text-baseball-600 italic mb-4">
            "Every bet is an adventure, every win is a celebration!" 🎉⚾🍌
          </p>
          <Disclaimer />
        </motion.div>
      </div>
    </div>
  );
}
