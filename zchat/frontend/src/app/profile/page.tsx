'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  User, 
  Mail, 
  Wallet, 
  Settings, 
  Shield, 
  Bell, 
  Eye, 
  EyeOff, 
  Copy, 
  RefreshCw,
  Edit,
  Save,
  X
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn, formatZcash, getRandomBananaEmoji } from '@/lib/utils';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [emoji, setEmoji] = useState('🍌');
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [showAddress, setShowAddress] = useState(false);
  const [editedUser, setEditedUser] = useState({
    username: user?.username || '',
    email: user?.email || ''
  });

  useEffect(() => {
    setEmoji(getRandomBananaEmoji());
  }, []);

  // Mock wallet data - would come from API
  const walletData = {
    address: user?.zcash_address || 'zs1banana123example456address789here',
    balance: parseFloat(user?.balance || '0.12345678'),
    isConnected: !!user?.zcash_address,
    transactions: [
      { id: '1', type: 'win', amount: 0.05, date: '2024-01-15', description: 'Banana throw bet - WON!' },
      { id: '2', type: 'bet', amount: -0.02, date: '2024-01-14', description: 'Fan costume bet' },
      { id: '3', type: 'win', amount: 0.08, date: '2024-01-12', description: 'Home run dance bet - WON!' },
    ]
  };

  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: false,
      sms: false
    },
    privacy: {
      showStats: true,
      showWins: true,
      publicProfile: false
    },
    betting: {
      autoConfirm: false,
      maxBetAmount: 1.0,
      favoriteCategory: 'banana-antics'
    }
  });

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User, emoji: '👤' },
    { id: 'wallet', name: 'Wallet', icon: Wallet, emoji: '💰' },
    { id: 'settings', name: 'Settings', icon: Settings, emoji: '⚙️' },
    { id: 'security', name: 'Security', icon: Shield, emoji: '🔒' }
  ];

  const handleSaveProfile = () => {
    // In a real app, this would make an API call
    console.log('Saving profile:', editedUser);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedUser({
      username: user?.username || '',
      email: user?.email || ''
    });
    setIsEditing(false);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // In a real app, you'd show a toast notification
    alert('Copied to clipboard! 📋');
  };

  const connectWallet = () => {
    // In a real app, this would initiate wallet connection
    alert('Connecting wallet... 🍌');
  };

  const refreshBalance = () => {
    // In a real app, this would refresh the balance from the API
    alert('Refreshing balance... 🔄');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-banana-50 via-banana-100 to-grass-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
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
              transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
            >
              👤
            </motion.span>
            <h1 className="font-baseball text-3xl md:text-5xl font-bold text-banana-800">
              My Profile
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
            Manage your banana-betting experience! 🎪
          </p>
        </motion.div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:w-64"
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200">
              {/* User Avatar */}
              <div className="text-center mb-6">
                <div className="w-20 h-20 bg-banana-500 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">{emoji}</span>
                </div>
                <h3 className="font-bold text-lg text-baseball-800">{user?.username}</h3>
                <p className="text-sm text-baseball-600">{user?.email}</p>
              </div>

              {/* Navigation Tabs */}
              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 text-left',
                      activeTab === tab.id
                        ? 'bg-banana-500 text-white shadow-md'
                        : 'text-baseball-700 hover:bg-banana-100'
                    )}
                  >
                    <span className="text-lg">{tab.emoji}</span>
                    <span className="font-medium">{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>
          </motion.div>

          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="flex-1"
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-banana-200">
              
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-baseball-800">Profile Information</h2>
                    {!isEditing ? (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="flex items-center space-x-2 px-4 py-2 bg-banana-500 text-white rounded-lg hover:bg-banana-600 transition-colors"
                      >
                        <Edit size={16} />
                        <span>Edit</span>
                      </button>
                    ) : (
                      <div className="flex space-x-2">
                        <button
                          onClick={handleSaveProfile}
                          className="flex items-center space-x-2 px-4 py-2 bg-grass-500 text-white rounded-lg hover:bg-grass-600 transition-colors"
                        >
                          <Save size={16} />
                          <span>Save</span>
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="flex items-center space-x-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        >
                          <X size={16} />
                          <span>Cancel</span>
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-baseball-700 mb-2">
                        Username
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedUser.username}
                          onChange={(e) => setEditedUser({ ...editedUser, username: e.target.value })}
                          className="w-full px-4 py-3 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-banana-500"
                        />
                      ) : (
                        <p className="text-lg text-baseball-800">{user?.username}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-baseball-700 mb-2">
                        Email
                      </label>
                      {isEditing ? (
                        <input
                          type="email"
                          value={editedUser.email}
                          onChange={(e) => setEditedUser({ ...editedUser, email: e.target.value })}
                          className="w-full px-4 py-3 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500 focus:border-banana-500"
                        />
                      ) : (
                        <p className="text-lg text-baseball-800">{user?.email}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-baseball-700 mb-2">
                        Member Since
                      </label>
                      <p className="text-lg text-baseball-800">January 2024 🎉</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Wallet Tab */}
              {activeTab === 'wallet' && (
                <div>
                  <h2 className="text-2xl font-bold text-baseball-800 mb-6">Wallet Management</h2>
                  
                  {/* Balance Card */}
                  <div className="bg-gradient-to-r from-banana-400 to-banana-500 rounded-xl p-6 text-white mb-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-banana-100 mb-1">Current Balance</p>
                        <p className="text-3xl font-bold">{formatZcash(walletData.balance)}</p>
                      </div>
                      <button
                        onClick={refreshBalance}
                        className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                      >
                        <RefreshCw size={24} />
                      </button>
                    </div>
                  </div>

                  {/* Wallet Address */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-baseball-700 mb-2">
                      Wallet Address
                    </label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 px-4 py-3 bg-gray-50 border border-banana-300 rounded-lg">
                        <p className="font-mono text-sm">
                          {showAddress ? walletData.address : '••••••••••••••••••••••••••••••••••••'}
                        </p>
                      </div>
                      <button
                        onClick={() => setShowAddress(!showAddress)}
                        className="p-3 bg-banana-500 text-white rounded-lg hover:bg-banana-600 transition-colors"
                      >
                        {showAddress ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                      <button
                        onClick={() => copyToClipboard(walletData.address)}
                        className="p-3 bg-grass-500 text-white rounded-lg hover:bg-grass-600 transition-colors"
                      >
                        <Copy size={20} />
                      </button>
                    </div>
                  </div>

                  {/* Connection Status */}
                  <div className="mb-6">
                    <div className="flex items-center justify-between p-4 bg-grass-50 border border-grass-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-grass-500 rounded-full"></div>
                        <span className="font-medium text-grass-800">Wallet Connected</span>
                      </div>
                      <button
                        onClick={connectWallet}
                        className="px-4 py-2 bg-grass-500 text-white rounded-lg hover:bg-grass-600 transition-colors"
                      >
                        Reconnect
                      </button>
                    </div>
                  </div>

                  {/* Recent Transactions */}
                  <div>
                    <h3 className="text-lg font-bold text-baseball-800 mb-4">Recent Transactions</h3>
                    <div className="space-y-3">
                      {walletData.transactions.map((tx) => (
                        <div key={tx.id} className="flex items-center justify-between p-4 bg-banana-50 border border-banana-200 rounded-lg">
                          <div>
                            <p className="font-medium text-baseball-800">{tx.description}</p>
                            <p className="text-sm text-baseball-600">{tx.date}</p>
                          </div>
                          <div className={cn(
                            'font-bold',
                            tx.type === 'win' ? 'text-grass-600' : 'text-red-600'
                          )}>
                            {tx.type === 'win' ? '+' : ''}{formatZcash(tx.amount)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Settings Tab */}
              {activeTab === 'settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-baseball-800 mb-6">Settings</h2>
                  
                  <div className="space-y-8">
                    {/* Notifications */}
                    <div>
                      <h3 className="text-lg font-semibold text-baseball-800 mb-4">Notifications</h3>
                      <div className="space-y-3">
                        {Object.entries(settings.notifications).map(([key, value]) => (
                          <label key={key} className="flex items-center justify-between">
                            <span className="text-baseball-700 capitalize">{key} Notifications</span>
                            <input
                              type="checkbox"
                              checked={value}
                              onChange={(e) => setSettings({
                                ...settings,
                                notifications: { ...settings.notifications, [key]: e.target.checked }
                              })}
                              className="w-5 h-5 text-banana-500 rounded focus:ring-banana-500"
                            />
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Privacy */}
                    <div>
                      <h3 className="text-lg font-semibold text-baseball-800 mb-4">Privacy</h3>
                      <div className="space-y-3">
                        {Object.entries(settings.privacy).map(([key, value]) => (
                          <label key={key} className="flex items-center justify-between">
                            <span className="text-baseball-700 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                            <input
                              type="checkbox"
                              checked={value}
                              onChange={(e) => setSettings({
                                ...settings,
                                privacy: { ...settings.privacy, [key]: e.target.checked }
                              })}
                              className="w-5 h-5 text-banana-500 rounded focus:ring-banana-500"
                            />
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Betting Preferences */}
                    <div>
                      <h3 className="text-lg font-semibold text-baseball-800 mb-4">Betting Preferences</h3>
                      <div className="space-y-4">
                        <label className="flex items-center justify-between">
                          <span className="text-baseball-700">Auto-confirm bets</span>
                          <input
                            type="checkbox"
                            checked={settings.betting.autoConfirm}
                            onChange={(e) => setSettings({
                              ...settings,
                              betting: { ...settings.betting, autoConfirm: e.target.checked }
                            })}
                            className="w-5 h-5 text-banana-500 rounded focus:ring-banana-500"
                          />
                        </label>
                        
                        <div>
                          <label className="block text-sm font-medium text-baseball-700 mb-2">
                            Maximum Bet Amount (ZEC)
                          </label>
                          <input
                            type="number"
                            step="0.001"
                            value={settings.betting.maxBetAmount}
                            onChange={(e) => setSettings({
                              ...settings,
                              betting: { ...settings.betting, maxBetAmount: parseFloat(e.target.value) }
                            })}
                            className="w-full px-3 py-2 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-baseball-700 mb-2">
                            Favorite Category
                          </label>
                          <select
                            value={settings.betting.favoriteCategory}
                            onChange={(e) => setSettings({
                              ...settings,
                              betting: { ...settings.betting, favoriteCategory: e.target.value }
                            })}
                            className="w-full px-3 py-2 border border-banana-300 rounded-lg focus:ring-2 focus:ring-banana-500"
                          >
                            <option value="banana-antics">Banana Antics 🍌</option>
                            <option value="player-props">Player Props ⚾</option>
                            <option value="crowd-fun">Crowd Fun 🎭</option>
                            <option value="baseball">Baseball ⚾</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div>
                  <h2 className="text-2xl font-bold text-baseball-800 mb-6">Security</h2>
                  
                  <div className="space-y-6">
                    <div className="p-4 bg-grass-50 border border-grass-200 rounded-lg">
                      <div className="flex items-center space-x-3 mb-2">
                        <Shield className="text-grass-600" size={24} />
                        <h3 className="text-lg font-semibold text-grass-800">Account Security</h3>
                      </div>
                      <p className="text-sm text-grass-700">Your account is secured with modern encryption and authentication.</p>
                    </div>

                    <button className="w-full p-4 bg-banana-500 text-white rounded-lg hover:bg-banana-600 transition-colors font-semibold">
                      Change Password
                    </button>

                    <button className="w-full p-4 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-semibold">
                      Enable Two-Factor Authentication
                    </button>

                    <div className="pt-6 border-t border-banana-200">
                      <button
                        onClick={logout}
                        className="w-full p-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-semibold"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Fun Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center mt-12 p-6 bg-white/50 backdrop-blur-sm rounded-2xl border border-banana-200"
        >
          <p className="text-baseball-600 italic">
            "Stay secure, have fun, and keep those bananas coming!"
          </p>
        </motion.div>
      </div>
    </div>
  );
}
