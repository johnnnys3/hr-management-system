// frontend/src/layout/useSidebarCollapse.test.ts
import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useSidebarCollapse } from './useSidebarCollapse'

const STORAGE_KEY = 'hrms.sidebar.collapsed'

describe('useSidebarCollapse', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('defaults to not collapsed when nothing is stored', () => {
    const { result } = renderHook(() => useSidebarCollapse())
    expect(result.current.collapsed).toBe(false)
  })

  it('reads a previously stored collapsed=true value', () => {
    window.localStorage.setItem(STORAGE_KEY, 'true')
    const { result } = renderHook(() => useSidebarCollapse())
    expect(result.current.collapsed).toBe(true)
  })

  it('toggling persists the new value to localStorage', () => {
    const { result } = renderHook(() => useSidebarCollapse())
    act(() => {
      result.current.setCollapsed(true)
    })
    expect(result.current.collapsed).toBe(true)
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe('true')
  })
})
