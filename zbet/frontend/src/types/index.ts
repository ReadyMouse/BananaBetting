// User types
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  zcash_account?: string;
  zcash_address?: string;
  balance?: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// Authentication types
export interface AuthToken {
  access_token: string;
  token_type: string;
}

// Betting types
export interface Bet {
  id: string;
  title: string;
  description: string;
  odds: number;
  minimumBet: number;
  maximumBet: number;
  category: "baseball" | "banana-antics" | "crowd-fun" | "player-props";
  status: "open" | "closed" | "settled";
  outcome?: "win" | "loss" | "push";
  createdAt: string;
  settlementDate?: string;
}

export interface UserBet {
  id: string;
  betId: string;
  bet: Bet;
  amount: number;
  potentialPayout: number;
  status: "pending" | "won" | "lost" | "cancelled";
  placedAt: string;
  settledAt?: string;
}

// Wallet types
export interface WalletInfo {
  address: string;
  balance: number;
  isConnected: boolean;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Search/Filter types
export interface BetFilters {
  category?: string;
  minOdds?: number;
  maxOdds?: number;
  searchTerm?: string;
}
