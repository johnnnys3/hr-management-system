// frontend/src/layout/useSidebarCollapse.ts
import { useState } from 'react'

const STORAGE_KEY = 'hrms.sidebar.collapsed'

export function useSidebarCollapse(): { collapsed: boolean; setCollapsed: (value: boolean) => void } {
  const [collapsed, setCollapsedState] = useState<boolean>(() => window.localStorage.getItem(STORAGE_KEY) === 'true')

  function setCollapsed(value: boolean) {
    setCollapsedState(value)
    window.localStorage.setItem(STORAGE_KEY, String(value))
  }

  return { collapsed, setCollapsed }
}
