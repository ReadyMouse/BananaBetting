'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, TrendingUp, Clock, DollarSign, Zap } from 'lucide-react';
import { cn, getRandomBananaEmoji } from '@/lib/utils';

// Mock data for betting opportunities
const mockBets = [
  {
    id: '1',
    title: 'Will a banana be thrown onto the field?',
    description: 'Classic Savannah Bananas tradition - will the crowd toss a banana during the game?',
    odds: 2.5,
    minimumBet: 0.001,
    maximumBet: 1.0,
    category: 'banana-antics',
    status: 'open',
    emoji: '🍌',
    timeLeft: '2h 15m',
    participants: 156
  },
  {
    id: '2',
    title: 'Number of dancing players during warmup',
    description: 'How many players will be caught dancing during pre-game warmup?',
    odds: 3.2,
    minimumBet: 0.005,
    maximumBet: 0.5,
    category: 'player-props',
    status: 'open',
    emoji: '💃',
    timeLeft: '1h 42m',
    participants: 89
  },
  {
    id: '3',
    title: 'First fan to wear banana costume',
    description: 'Which inning will we spot the first fan in a banana costume?',
    odds: 1.8,
    minimumBet: 0.01,
    maximumBet: 2.0,
    category: 'crowd-fun',
    status: 'open',
    emoji: '🎭',
    timeLeft: '45m',
    participants: 234
  },
  {
    id: '4',
    title: 'Pitcher does the cha-cha',
    description: 'Will the starting pitcher perform the cha-cha dance before first pitch?',
    odds: 4.1,
    minimumBet: 0.002,
    maximumBet: 0.8,
    category: 'player-props',
    status: 'open',
    emoji: '🕺',
    timeLeft: '3h 12m',
    participants: 67
  },
  {
    id: '5',
    title: 'Home run celebration dance',
    description: 'What type of celebration dance will follow the first home run?',
    odds: 2.9,
    minimumBet: 0.001,
    maximumBet: 1.5,
    category: 'baseball',
    status: 'open',
    emoji: '⚾',
    timeLeft: '1h 58m',
    participants: 198
  },
  {
    id: '6',
    title: 'Crowd noise level (decibels)',
    description: 'Will the crowd noise exceed 120 decibels during the game?',
    odds: 1.6,
    minimumBet: 0.005,
    maximumBet: 1.0,
    category: 'crowd-fun',
    status: 'open',
    emoji: '📢',
    timeLeft: '2h 33m',
    participants: 112
  }
];

const categories = [
  { id: 'all', name: 'All Bets', emoji: '🎪' },
  { id: 'banana-antics', name: 'Banana Antics', emoji: '🍌' },
  { id: 'player-props', name: 'Player Props', emoji: '⚾' },
  { id: 'crowd-fun', name: 'Crowd Fun', emoji: '🎭' },
  { id: 'baseball', name: 'Baseball', emoji: '⚾' }
];

export default function BettingPage() {
  const [emoji, setEmoji] = useState('🍌');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('time'); // time, odds, participants
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    setEmoji(getRandomBananaEmoji());
  }, []);

  const filteredBets = mockBets
    .filter(bet => {
      const matchesSearch = bet.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           bet.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || bet.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'odds':
          return b.odds - a.odds;
        case 'participants':
          return b.participants - a.participants;
        case 'time':
        default:
          return a.timeLeft.localeCompare(b.timeLeft);
      }
    });

  const handlePlaceBet = (betId: string) => {
    // This would open a betting modal in a real app
    alert(`Placing bet on ${betId}! 🍌`);
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
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            >
              🔍
            </motion.span>
            <h1 className="font-baseball text-3xl md:text-5xl font-bold text-banana-800">
              Find Your Next Win!
            </h1>
            <motion.span 
              className="text-4xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              🍌
            </motion.span>
          </div>
          <p className="text-lg text-baseball-600 italic">
            Discover banana-tastic betting opportunities! 🎪
          </p>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200 mb-8"
        >
          {/* Search Bar */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-baseball-400" size={20} />
            <input
              type="text"
              placeholder="Search for bets... (try 'banana', 'dance', 'crowd')"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-banana-500 transition-colors"
            />
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap gap-3 mb-6">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={cn(
                  'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200',
                  selectedCategory === category.id
                    ? 'bg-banana-500 text-white shadow-md'
                    : 'bg-banana-100 text-banana-800 hover:bg-banana-200'
                )}
              >
                <span>{category.emoji}</span>
                <span>{category.name}</span>
              </button>
            ))}
          </div>

          {/* Sort Options */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-baseball-700">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-banana-500"
              >
                <option value="time">Time Remaining</option>
                <option value="odds">Best Odds</option>
                <option value="participants">Most Popular</option>
              </select>
            </div>

            <div className="text-sm text-baseball-600">
              {filteredBets.length} bets found
            </div>
          </div>
        </motion.div>

        {/* Betting Cards */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <AnimatePresence>
            {filteredBets.map((bet, index) => (
              <motion.div
                key={bet.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.02 }}
                className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200 group cursor-pointer"
              >
                {/* Card Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl group-hover:scale-110 transition-transform">
                    {bet.emoji}
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1 text-sm text-baseball-600">
                      <Clock size={16} />
                      <span>{bet.timeLeft}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-sm text-baseball-600">
                      <TrendingUp size={16} />
                      <span>{bet.participants} players</span>
                    </div>
                  </div>
                </div>

                {/* Card Content */}
                <h3 className="font-bold text-lg text-baseball-800 mb-2 group-hover:text-banana-800 transition-colors">
                  {bet.title}
                </h3>
                <p className="text-sm text-baseball-600 mb-4 line-clamp-2">
                  {bet.description}
                </p>

                {/* Odds and Betting Range */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-baseball-600">Odds:</span>
                    <span className="font-bold text-grass-600 text-xl">{bet.odds}x</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-baseball-600">Bet Range:</span>
                    <span className="text-baseball-800">
                      {bet.minimumBet} - {bet.maximumBet} ZEC
                    </span>
                  </div>
                </div>

                {/* Action Button */}
                <motion.button
                  onClick={() => handlePlaceBet(bet.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full bg-banana-500 hover:bg-banana-600 text-white font-bold py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <DollarSign size={20} />
                  <span>Place Bet</span>
                  <span>{emoji}</span>
                </motion.button>
              </motion.div>
            ))}
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
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-bold text-baseball-800 mb-2">
              No bets found!
            </h3>
            <p className="text-baseball-600">
              Try adjusting your search or category filters. 🍌
            </p>
          </motion.div>
        )}

        {/* Fun Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center mt-12 p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-banana-200"
        >
          <p className="text-baseball-600 italic">
            Remember: Bet responsibly and have fun! 🎪⚾🍌
          </p>
        </motion.div>
      </div>
    </div>
  );
}
