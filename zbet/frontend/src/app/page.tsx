'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { motion } from 'framer-motion';
import { TrendingUp, Search, Users, Trophy, Zap, Star } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getRandomBananaEmoji } from '@/lib/utils';

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Simplified adapter function for homepage cards
function getHomepageDisplayData(bettingSystemType: string, systemData: any) {
  switch (bettingSystemType) {
    case 'pari_mutuel':
      const totalPool = systemData?.total_pool || 0;
      const pools = systemData?.betting_pools || [];
      
      // Find the most popular outcome (highest pool amount)
      let topOutcome = null;
      let topPercentage = 0;
      
      if (pools.length > 0 && totalPool > 0) {
        topOutcome = pools.reduce((max: any, pool: any) => 
          pool.pool_amount > max.pool_amount ? pool : max
        );
        topPercentage = Math.round((topOutcome.pool_amount / totalPool) * 100);
      }
      
      return {
        primaryLabel: "Total Pool",
        primaryValue: `${totalPool.toFixed(4)} ZEC`,
        description: topOutcome?.outcome_description || "No bets yet",
        poolCount: pools.length
      };
      
    case 'fixed_odds':
      const odds = systemData?.odds || 2.0;
      return {
        primaryLabel: "Odds",
        primaryValue: `${odds.toFixed(1)}x`,
        secondaryLabel: "Payout",
        secondaryValue: `${(odds * 0.001).toFixed(4)} ZEC`,
        description: "Fixed odds betting",
        poolCount: 1
      };
      
    case 'spread':
      const spread = systemData?.spread || 0;
      const overOdds = systemData?.over_odds || 1.9;
      return {
        primaryLabel: "Spread",
        primaryValue: spread > 0 ? `+${spread}` : `${spread}`,
        secondaryLabel: "Over",
        secondaryValue: `${overOdds.toFixed(1)}x`,
        description: "Point spread betting",
        poolCount: 2
      };
      
    default:
      // For unknown betting systems, show minimal info or indicate system is unknown
      return {
        primaryLabel: "Betting System",
        primaryValue: bettingSystemType || "Unknown",
        secondaryLabel: "Status", 
        secondaryValue: "Not Supported",
        description: "Betting system not yet supported",
        poolCount: 0
      };
  }
}

export default function Home() {
  const { isAuthenticated, user, loading } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [buttonEmojis, setButtonEmojis] = useState(['🍌', '🍌']);
  const [featuredBets, setFeaturedBets] = useState<any[]>([]);
  const [betsLoading, setBetsLoading] = useState(true);

  useEffect(() => {
    setMounted(true);
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    if (mounted) {
      // Set random emojis after mounting
      setButtonEmojis([getRandomBananaEmoji(), getRandomBananaEmoji()]);
      // Fetch featured bets
      fetchFeaturedBets();
    }
  }, [mounted]);

  const fetchFeaturedBets = async () => {
    try {
      setBetsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/events`);
      
      if (response.ok) {
        const events = await response.json();
        
        // Transform API events to featured bet format with dynamic system data (take first 3)
        const transformed = events.slice(0, 3).map((event: any) => {
          const systemData = event.betting_system_data;
          const displayData = getHomepageDisplayData(event.betting_system_type, systemData);
          
          return {
            id: event.id,
            title: event.title,
            bettingSystemType: event.betting_system_type,
            displayData: displayData,
            emoji: getCategoryEmoji(event.category),
            category: formatCategory(event.category)
          };
        });
        
        setFeaturedBets(transformed);
      } else {
        setFeaturedBets([]);
      }
    } catch (error) {
      console.error('Failed to fetch featured bets:', error);
      setFeaturedBets([]);
    } finally {
      setBetsLoading(false);
    }
  };

  const getCategoryEmoji = (category: string) => {
    const categoryEmojis: { [key: string]: string } = {
      'banana-antics': '🍌',
      'player-props': '⚾',
      'crowd-fun': '🎭',
      'baseball': '⚾'
    };
    return categoryEmojis[category] || '🎪';
  };

  const formatCategory = (category: string) => {
    const categoryNames: { [key: string]: string } = {
      'banana-antics': 'Banana Antics',
      'player-props': 'Player Props',
      'crowd-fun': 'Crowd Fun',
      'baseball': 'Baseball'
    };
    return categoryNames[category] || category;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-banana-100 to-grass-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 banana-spin">🍌</div>
          <p className="text-banana-800 font-fun text-lg">Loading the fun...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }


  const stats = [
    { label: "Active Bets", value: "47", icon: TrendingUp },
    { label: "Players Online", value: "1,234", icon: Users },
    { label: "Fun Level", value: "MAX", icon: Zap },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-banana-50 via-banana-100 to-grass-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center space-x-4 mb-6">
            <motion.span 
              className="text-6xl"
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              🍌
            </motion.span>
            <h1 className="font-baseball text-4xl md:text-6xl font-bold text-banana-800">
              Welcome Back, {user?.username}!
            </h1>
            <motion.span 
              className="text-6xl"
              animate={{ rotate: [0, -10, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity, delay: 1 }}
            >
              ⚾
            </motion.span>
          </div>
          <p className="text-xl text-baseball-600 italic mb-8">
            Ready for some banana-crazy betting action? 🎪
          </p>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200"
              >
                <div className="flex items-center justify-center space-x-3">
                  <stat.icon className="text-banana-600" size={32} />
                  <div>
                    <p className="text-2xl font-bold text-banana-800">{stat.value}</p>
                    <p className="text-sm text-baseball-600">{stat.label}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Featured Bets */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mb-12"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Star className="text-banana-600" size={28} />
            <h2 className="font-baseball text-2xl font-bold text-banana-800">
              Today's Hottest Bets
            </h2>
            <Star className="text-banana-600" size={28} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {betsLoading ? (
              // Loading placeholder
              Array.from({ length: 3 }).map((_, index) => (
                <div
                  key={`loading-${index}`}
                  className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200 animate-pulse"
                >
                  <div className="text-center mb-4">
                    <div className="text-4xl mb-2">🍌</div>
                    <div className="bg-banana-200 rounded-full h-6 w-24 mx-auto"></div>
                  </div>
                  <div className="bg-gray-200 rounded h-4 mb-3"></div>
                  <div className="flex items-center justify-between">
                    <div className="bg-gray-200 rounded h-4 w-12"></div>
                    <div className="bg-gray-200 rounded h-4 w-16"></div>
                  </div>
                </div>
              ))
            ) : featuredBets.length > 0 ? (
              featuredBets.map((bet, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                  onClick={() => router.push(`/betting/${bet.id}`)}
                  className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200 cursor-pointer group"
              >
                <div className="text-center mb-4">
                  <div className="text-4xl mb-2 group-hover:scale-110 transition-transform">
                    {bet.emoji}
                  </div>
                  <span className="bg-banana-200 text-banana-800 px-3 py-1 rounded-full text-xs font-medium">
                    {bet.category}
                  </span>
                </div>
                <h3 className="font-semibold text-baseball-800 mb-3 text-center">
                  {bet.title}
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-baseball-600">{bet.displayData.primaryLabel}:</span>
                    <span className="font-bold text-banana-600">{bet.displayData.primaryValue}</span>
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-baseball-500">{bet.displayData.secondaryLabel}:</span>
                      <span className="text-grass-600 font-medium">{bet.displayData.secondaryValue}</span>
                    </div>
                    <div className="text-xs text-baseball-500 text-center truncate">
                      {bet.displayData.description}
                    </div>
                  </div>
                </div>
              </motion.div>
              ))
            ) : (
              <div className="col-span-full flex flex-col items-center justify-center py-12">
                <div className="text-6xl mb-4">🍌</div>
                <h3 className="text-xl font-semibold text-baseball-600 mb-2">No bets available</h3>
                <p className="text-baseball-500 text-center">
                  Check back later for exciting betting opportunities!
                </p>
              </div>
            )}
          </div>
        </motion.section>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <motion.button
            onClick={() => router.push('/betting')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-banana-500 hover:bg-banana-600 text-white font-bold py-6 px-8 rounded-2xl shadow-lg transition-colors flex items-center justify-center space-x-3"
          >
            <Search size={24} />
            <span>Find More Bets</span>
            <span className="text-2xl">{buttonEmojis[0]}</span>
          </motion.button>

          <motion.button
            onClick={() => router.push('/my-bets')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-grass-500 hover:bg-grass-600 text-white font-bold py-6 px-8 rounded-2xl shadow-lg transition-colors flex items-center justify-center space-x-3"
          >
            <Trophy size={24} />
            <span>My Bets</span>
            <span className="text-2xl">{buttonEmojis[1]}</span>
          </motion.button>
        </motion.div>

        {/* Fun Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center mt-12 p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-banana-200"
        >
          <p className="text-baseball-600 italic">
            "Banana-ball is 90% fun, 10% skill, and 100% bananas!"
          </p>
        </motion.div>
      </div>
    </div>
  );
}