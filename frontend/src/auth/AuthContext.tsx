import { createContext, useContext } from 'react'
import type { Me } from '../api/types'

export interface AuthContextValue {
  me: Me | null
  isLoading: boolean
  refetch: () => Promise<unknown>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthContext.Provider')
  }
  return ctx
}
